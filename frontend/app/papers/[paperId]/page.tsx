"use client";

import { FormEvent, useEffect, useState } from "react";
import { AuthGuard } from "@/components/AuthGuard";
import { AnswerCard } from "@/components/AnswerCard";
import { StatusBadge } from "@/components/StatusBadge";
import { api, type Answer, type Paper } from "@/lib/api";

export default function PaperDetailPage({ params }: { params: { paperId: string } }) {
  const [paper, setPaper] = useState<Paper | null>(null);
  const [answers, setAnswers] = useState<Answer[]>([]);
  const [question, setQuestion] = useState("");
  const [mode, setMode] = useState<"qa" | "tutor">("qa");
  const [error, setError] = useState("");
  const [asking, setAsking] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [criterion, setCriterion] = useState("");
  const [runningAgent, setRunningAgent] = useState(false);

  async function load() {
    const nextPaper = await api.getPaper(params.paperId);
    setPaper(nextPaper);
    if (nextPaper.status === "ready") {
      setAnswers(await api.answers(params.paperId));
    }
  }

  useEffect(() => {
    load().catch((err) => setError(err instanceof Error ? err.message : "Could not load paper"));
  }, [params.paperId]);

  useEffect(() => {
    if (!paper || paper.status !== "processing") return;
    const timer = window.setInterval(async () => {
      try {
        const status = await api.getStatus(params.paperId);
        setPaper((current) => current ? { ...current, status: status.status, error_message: status.error_message } : current);
        if (status.status === "ready" || status.status === "failed") {
          window.clearInterval(timer);
          load().catch(() => undefined);
        }
      } catch {
        window.clearInterval(timer);
      }
    }, 2500);
    return () => window.clearInterval(timer);
  }, [paper, params.paperId]);

  async function processAgain() {
    setProcessing(true);
    setError("");
    try {
      await api.processPaper(params.paperId);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not start processing");
    } finally {
      setProcessing(false);
    }
  }

  async function submitQuestion(event: FormEvent) {
    event.preventDefault();
    if (!question.trim()) return;
    setAsking(true);
    setError("");
    try {
      const response = mode === "qa"
        ? await api.ask(params.paperId, question)
        : await api.tutor(params.paperId, question);
      setAnswers((current) => [response, ...current]);
      setQuestion("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Question failed");
    } finally {
      setAsking(false);
    }
  }


  async function runAccreditationAgent(event: FormEvent) {
    event.preventDefault();
    if (!criterion.trim()) return;

    setRunningAgent(true);
    setError("");

    try {
      const response = await api.accreditationAgent(
        params.paperId,
        criterion
      );
      setAnswers((current) => [response, ...current]);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Accreditation analysis failed"
      );
    } finally {
      setRunningAgent(false);
    }
  }


  return (
    <AuthGuard>
      {!paper && <p className="muted">Loading paper...</p>}
      {paper && (
        <div className="grid two" style={{ alignItems: "start" }}>
          <section className="grid" style={{ alignContent: "start" }}>
            <div className="panel">
              <StatusBadge status={paper.status} />
              <h1 style={{ marginTop: 12 }}>{paper.title || paper.original_filename}</h1>
              <p className="muted">{paper.original_filename}</p>
              <p className="muted">
                Pages: {paper.page_count ?? 0} · Paragraphs: {paper.paragraph_count ?? 0} · Chunks: {paper.chunk_count ?? 0}
              </p>
              {paper.error_message && <p className="error">{paper.error_message}</p>}
              {paper.status !== "ready" && (
                <button disabled={processing || paper.status === "processing"} onClick={processAgain}>
                  {paper.status === "processing" ? "Processing..." : "Start processing"}
                </button>
              )}
            </div>

            {paper.status === "ready" && (
          <section className="panel">
            <h2>Accreditation Evidence Agent</h2>
            <p className="muted">
              Map document evidence to an accreditation criterion, identify
              gaps, and generate actions for human review.
            </p>

            <form onSubmit={runAccreditationAgent}>
              <label>
                Accreditation criterion
                <textarea
                  value={criterion}
                  onChange={(event) => setCriterion(event.target.value)}
                  placeholder="Example: Assess the evidence for NBA Criterion 3 - Course Outcomes and Program Outcomes attainment."
                  required
                />
              </label>

              <button disabled={runningAgent}>
                {runningAgent
                  ? "Agent analysing evidence..."
                  : "Run Accreditation Agent"}
              </button>
            </form>
          </section>
        )}


            {paper.status === "ready" && (
              <section className="panel">
                <h2>Ask This Paper</h2>
                <form onSubmit={submitQuestion}>
                  <label>Mode
                    <select value={mode} onChange={(event) => setMode(event.target.value as "qa" | "tutor")}>
                      <option value="qa">Direct Q&A</option>
                      <option value="tutor">Tutor explanation</option>
                    </select>
                  </label>
                  <label>Question
                    <textarea value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="Ask only about this uploaded paper" required />
                  </label>
                  <button disabled={asking}>{asking ? "Retrieving evidence..." : "Ask"}</button>
                </form>
              </section>
            )}
        {error && <p className="error">{error}</p>}
          </section>

          <aside className="grid">
            <h2>Answer History</h2>
            {answers.length === 0 && <p className="muted">No answers yet.</p>}
            {answers.map((answer, index) => (
              <AnswerCard
                answer={answer}
                defaultOpen={index === 0}
                key={answer.id}
              />
            ))}
          </aside>
        </div>
      )}
    </AuthGuard>
  );
}
