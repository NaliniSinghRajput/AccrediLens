"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { AuthGuard } from "@/components/AuthGuard";
import { api } from "@/lib/api";

export default function UploadPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!file) return;
    setLoading(true);
    setError("");
    try {
      const paper = await api.uploadPaper(file);
      await api.processPaper(paper.id);
      router.push(`/papers/${paper.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthGuard>
      <section className="panel" style={{ maxWidth: 680 }}>
        <h1>Upload Paper</h1>
        <form onSubmit={submit}>
          <label>Research paper PDF<input type="file" accept="application/pdf" onChange={(event) => setFile(event.target.files?.[0] || null)} required /></label>
          {error && <p className="error">{error}</p>}
          <button disabled={loading || !file}>{loading ? "Uploading..." : "Upload and process"}</button>
        </form>
      </section>
    </AuthGuard>
  );
}
