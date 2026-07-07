import type { Answer } from "@/lib/api";

export function AnswerCard({ answer }: { answer: Answer }) {
  return (
    <article className="card">
      <p className="muted">{new Date(answer.created_at).toLocaleString()} · {answer.mode.toUpperCase()} · Confidence: {answer.confidence}</p>
      <h2>Answer</h2>
      <p>{answer.answer}</p>
      {answer.tutor_explanation && (
        <>
          <h2>Tutor Explanation</h2>
          <p>{answer.tutor_explanation}</p>
        </>
      )}
      <h2>References</h2>
      {answer.sources.length === 0 ? (
        <p className="muted">No sufficiently relevant passage was found in the uploaded PDF.</p>
      ) : (
        answer.sources.map((source, index) => (
          <div className="source" key={`${answer.id}-${source.chunk_id}`}>
            <strong>{index + 1}. Page {source.page_number}, Section: {source.section_title}, Paragraph {source.paragraph_start}-{source.paragraph_end}</strong>
            <p className="muted">Type: {source.source_type} · Chunk: {source.chunk_id} · Score: {source.score}</p>
            <pre>{source.text_excerpt}</pre>
          </div>
        ))
      )}
    </article>
  );
}
