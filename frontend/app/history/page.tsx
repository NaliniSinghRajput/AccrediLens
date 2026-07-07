"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { AuthGuard } from "@/components/AuthGuard";
import { AnswerCard } from "@/components/AnswerCard";
import { api, type Answer, type Paper } from "@/lib/api";

type HistoryItem = {
  paper: Paper;
  answers: Answer[];
};

export default function HistoryPage() {
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const papers = await api.listPapers();
        const history = await Promise.all(
          papers.map(async (paper) => ({
            paper,
            answers: paper.status === "ready" ? await api.answers(paper.id) : []
          }))
        );
        setItems(history.filter((item) => item.answers.length > 0));
      } catch (err) {
        setError(err instanceof Error ? err.message : "Could not load history");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <AuthGuard>
      <h1>Answer History</h1>
      {loading && <p className="muted">Loading history...</p>}
      {error && <p className="error">{error}</p>}
      {!loading && items.length === 0 && <p className="muted">No answer history yet.</p>}
      <div className="grid">
        {items.map((item) => (
          <section className="grid" key={item.paper.id}>
            <Link href={`/papers/${item.paper.id}`}><h2>{item.paper.title || item.paper.original_filename}</h2></Link>
            {item.answers.map((answer) => <AnswerCard answer={answer} key={answer.id} />)}
          </section>
        ))}
      </div>
    </AuthGuard>
  );
}
