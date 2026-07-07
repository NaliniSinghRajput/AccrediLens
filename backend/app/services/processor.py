import asyncio
from datetime import datetime, timezone

from sqlalchemy import delete

from app.core.database import SessionLocal
from app.models import Chunk, Page, Paper, Paragraph, ProcessingJob
from app.services.chunker import make_chunks
from app.services.ollama_client import OllamaClient
from app.services.pdf_parser import parse_pdf
from app.services.vector_store import VectorStore


def process_paper_job(paper_id: str, job_id: str | None = None) -> None:
    asyncio.run(process_paper(paper_id, job_id))


async def process_paper(paper_id: str, job_id: str | None = None) -> None:
    db = SessionLocal()
    try:
        paper = db.get(Paper, paper_id)
        if not paper:
            return
        job = db.get(ProcessingJob, job_id) if job_id else None
        paper.status = "processing"
        if job:
            job.status = "processing"
            job.message = "Extracting PDF text"
        db.commit()

        parsed = parse_pdf(paper.storage_path)
        db.execute(delete(Page).where(Page.paper_id == paper_id))
        db.execute(delete(Paragraph).where(Paragraph.paper_id == paper_id))
        db.execute(delete(Chunk).where(Chunk.paper_id == paper_id))

        paper.title = parsed.title or paper.original_filename
        for page in parsed.pages:
            db.add(Page(paper_id=paper_id, page_number=page.page_number, text=page.text))
        for para in parsed.paragraphs:
            db.add(
                Paragraph(
                    paper_id=paper_id,
                    page_number=para.page_number,
                    section_title=para.section_title,
                    paragraph_number=para.paragraph_number,
                    source_type=para.source_type,
                    text=para.text,
                )
            )

        prepared_chunks = make_chunks(parsed.paragraphs)
        chunk_rows: list[Chunk] = []
        for prepared in prepared_chunks:
            row = Chunk(
                paper_id=paper_id,
                page_number=prepared.page_number,
                section_title=prepared.section_title,
                paragraph_start=prepared.paragraph_start,
                paragraph_end=prepared.paragraph_end,
                source_type=prepared.source_type,
                text=prepared.text,
                token_count=prepared.token_count,
            )
            db.add(row)
            chunk_rows.append(row)
        db.commit()
        for row in chunk_rows:
            db.refresh(row)

        if job:
            job.message = "Generating local embeddings"
            db.commit()

        ollama = OllamaClient()
        vectors = await ollama.embed([chunk.text for chunk in chunk_rows])
        points = []
        for chunk, vector in zip(chunk_rows, vectors, strict=False):
            chunk.qdrant_point_id = chunk.id
            points.append(
                (
                    chunk.id,
                    vector,
                    {
                        "paper_id": paper_id,
                        "chunk_id": chunk.id,
                        "page_number": chunk.page_number,
                        "section_title": chunk.section_title,
                        "paragraph_start": chunk.paragraph_start,
                        "paragraph_end": chunk.paragraph_end,
                        "source_type": chunk.source_type,
                        "text": chunk.text,
                    },
                )
            )
        VectorStore().upsert_chunks(points)

        paper.status = "ready"
        paper.error_message = None
        paper.processed_at = datetime.now(timezone.utc)
        if job:
            job.status = "completed"
            job.message = "Paper is ready"
        db.commit()
    except Exception as exc:
        paper = db.get(Paper, paper_id)
        if paper:
            paper.status = "failed"
            paper.error_message = str(exc)
        if job_id:
            job = db.get(ProcessingJob, job_id)
            if job:
                job.status = "failed"
                job.message = str(exc)
        db.commit()
        raise
    finally:
        db.close()
