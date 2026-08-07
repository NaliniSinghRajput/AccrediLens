from dataclasses import dataclass
import re

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import Answer, AnswerSource, Paper, Question
from app.services.ollama_client import OllamaClient
from app.services.vector_store import VectorStore


ABSTAIN_ANSWER = "The uploaded paper does not provide enough information to answer this question."


@dataclass
class Evidence:
    chunk_id: str
    page_number: int
    section_title: str
    paragraph_start: int
    paragraph_end: int
    source_type: str
    text: str
    score: float


def lexical_overlap(question: str, text: str) -> float:
    stopwords = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "of",
        "to",
        "in",
        "for",
        "with",
        "is",
        "are",
        "was",
        "were",
        "what",
        "how",
        "why",
        "does",
        "do",
        "this",
        "that",
    }
    q_terms = {term.lower().strip(".,:;()[]") for term in question.split()}
    q_terms = {term for term in q_terms if len(term) > 2 and term not in stopwords}
    if not q_terms:
        return 0.0
    text_lower = text.lower()
    hits = sum(1 for term in q_terms if term in text_lower)
    return hits / len(q_terms)


def rerank(question: str, evidence: list[Evidence]) -> list[Evidence]:
    for item in evidence:
        item.score = (item.score * 0.78) + (lexical_overlap(question, item.text) * 0.22)
    return sorted(evidence, key=lambda item: item.score, reverse=True)


def confidence_for(evidence: list[Evidence]) -> str:
    if len(evidence) >= 2 and evidence[0].score >= 0.62:
        return "High"
    if evidence and evidence[0].score >= 0.45:
        return "Medium"
    return "Low"


def build_prompt(question: str, evidence: list[Evidence], tutor: bool) -> str:
    context_blocks = []
    for idx, item in enumerate(evidence, start=1):
        context_blocks.append(
            "\n".join(
                [
                    f"[SOURCE {idx}]",
                    f"chunk_id: {item.chunk_id}",
                    f"page: {item.page_number}",
                    f"section: {item.section_title}",
                    f"paragraphs: {item.paragraph_start}-{item.paragraph_end}",
                    f"source_type: {item.source_type}",
                    "text:",
                    item.text,
                ]
            )
        )
    mode_instruction = (
        "Also write a Tutor Explanation that simplifies the answer step by step, but do not add external examples."
        if tutor
        else "Keep Tutor Explanation empty."
    )
    return f"""
You are a local-first research-paper assistant. The uploaded PDF excerpts below are the only source of truth.

Rules:
- Answer only from the provided sources.
- Do not use outside knowledge.
- Do not include hidden reasoning, chain-of-thought, or <think> tags.
- If the sources do not answer the question, say exactly: {ABSTAIN_ANSWER}
- Do not invent citations. The application will attach citations from the retrieved source metadata.
- Be concise, technical, and faithful to the evidence.
- {mode_instruction}

Question:
{question}

Retrieved PDF evidence:
{chr(10).join(context_blocks)}

Return in this exact format:
Answer:
<answer based only on evidence>

Tutor Explanation:
<simple explanation if requested, otherwise leave blank>
""".strip()


def split_model_response(text: str) -> tuple[str, str | None]:
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE).strip()
    answer = text.strip()
    tutor = None
    if "Tutor Explanation:" in text:
        before, after = text.split("Tutor Explanation:", 1)
        answer = before.replace("Answer:", "").strip()
        tutor = after.strip() or None
    elif text.startswith("Answer:"):
        answer = text.replace("Answer:", "", 1).strip()
    return answer, tutor


async def answer_question(db: Session, paper: Paper, user_id: str, question_text: str, mode: str) -> Answer:
    settings = get_settings()
    question = Question(paper_id=paper.id, user_id=user_id, text=question_text, mode=mode)
    db.add(question)
    db.commit()
    db.refresh(question)

    ollama = OllamaClient()
    query_vector = (await ollama.embed([question_text]))[0]
    results = VectorStore().search(paper_id=paper.id, vector=query_vector, limit=settings.retrieval_top_k)

    evidence = [
        Evidence(
            chunk_id=str(point.payload.get("chunk_id")),
            page_number=int(point.payload.get("page_number")),
            section_title=str(point.payload.get("section_title")),
            paragraph_start=int(point.payload.get("paragraph_start")),
            paragraph_end=int(point.payload.get("paragraph_end")),
            source_type=str(point.payload.get("source_type")),
            text=str(point.payload.get("text")),
            score=float(point.score or 0.0),
        )
        for point in results
        if point.payload
    ]
    evidence = [
        item
        for item in rerank(question_text, evidence)
        if item.score >= settings.similarity_threshold
    ][: settings.final_context_k]

    if len(evidence) < settings.sufficiency_min_sources or not evidence or evidence[0].score < settings.similarity_threshold:
        answer = Answer(
            question_id=question.id,
            paper_id=paper.id,
            user_id=user_id,
            mode=mode,
            answer=ABSTAIN_ANSWER,
            tutor_explanation=None,
            confidence="Low",
        )
        db.add(answer)
        db.commit()
        db.refresh(answer)
        return answer

    prompt = build_prompt(question_text, evidence, tutor=mode == "tutor")
    raw_response = await ollama.generate(prompt)
    answer_text, tutor_text = split_model_response(raw_response)
    if not answer_text:
        answer_text = ABSTAIN_ANSWER

    answer = Answer(
        question_id=question.id,
        paper_id=paper.id,
        user_id=user_id,
        mode=mode,
        answer=answer_text,
        tutor_explanation=tutor_text if mode == "tutor" else None,
        confidence=confidence_for(evidence),
    )
    db.add(answer)
    db.commit()
    db.refresh(answer)

    for item in evidence:
        db.add(
            AnswerSource(
                answer_id=answer.id,
                chunk_id=item.chunk_id,
                page_number=item.page_number,
                section_title=item.section_title,
                paragraph_start=item.paragraph_start,
                paragraph_end=item.paragraph_end,
                source_type=item.source_type,
                score=f"{item.score:.4f}",
                text_excerpt=item.text[:1500],
            )
        )
    db.commit()
    db.refresh(answer)
    return answer
