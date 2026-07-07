"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { api, setToken } from "@/lib/api";

export default function RegisterPage() {
  const router = useRouter();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      await api.register({ full_name: fullName, email, password });
      const response = await api.login({ email, password });
      setToken(response.access_token);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="panel" style={{ maxWidth: 500, margin: "40px auto" }}>
      <h1>Register</h1>
      <form onSubmit={submit}>
        <label>Full name<input value={fullName} onChange={(event) => setFullName(event.target.value)} required /></label>
        <label>Email<input value={email} onChange={(event) => setEmail(event.target.value)} type="email" required /></label>
        <label>Password<input value={password} onChange={(event) => setPassword(event.target.value)} type="password" minLength={8} required /></label>
        {error && <p className="error">{error}</p>}
        <button disabled={loading}>{loading ? "Creating account..." : "Create account"}</button>
      </form>
      <p className="muted">Already registered? <Link href="/login">Login</Link></p>
    </section>
  );
}
