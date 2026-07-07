"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { AuthGuard } from "@/components/AuthGuard";
import { StatusBadge } from "@/components/StatusBadge";
import { api, clearToken, type Paper } from "@/lib/api";

export default function DashboardPage() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  async function load() {
    try {
      setPapers(await api.listPapers());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load papers");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <AuthGuard>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center", marginBottom: 18 }}>
        <h1 style={{ margin: 0 }}>Research Paper Library</h1>
        <div style={{ display: "flex", gap: 10 }}>
          <Link className="button" href="/upload">Upload PDF</Link>
          <button className="secondary" onClick={() => { clearToken(); window.location.href = "/login"; }}>Logout</button>
        </div>
      </div>
      {loading && <p className="muted">Loading papers...</p>}
      {error && <p className="error">{error}</p>}
      {!loading && papers.length === 0 && (
        <section className="panel">
          <h2>No papers yet</h2>
          <p className="muted">Upload a research paper PDF to create grounded chunks and citations.</p>
          <Link className="button" href="/upload">Upload first paper</Link>
        </section>
      )}
      <div className="grid">
        {papers.map((paper) => (
          <Link className="card" href={`/papers/${paper.id}`} key={paper.id}>
            <StatusBadge status={paper.status} />
            <h2 style={{ marginTop: 12 }}>{paper.title || paper.original_filename}</h2>
            <p className="muted">{paper.original_filename}</p>
            {paper.error_message && <p className="error">{paper.error_message}</p>}
          </Link>
        ))}
      </div>
    </AuthGuard>
  );
}
