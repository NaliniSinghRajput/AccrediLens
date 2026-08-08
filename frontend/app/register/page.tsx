"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { AuthShell } from "@/components/AuthShell";
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
      await api.register({
        full_name: fullName,
        email,
        password,
      });

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
    <AuthShell mode="register">
      <form className="auth-form" onSubmit={submit}>
        <label>
          Full name
          <input
            autoComplete="name"
            value={fullName}
            onChange={(event) => setFullName(event.target.value)}
            placeholder="Your full name"
            required
          />
        </label>

        <label>
          Institutional email
          <input
            autoComplete="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="name@institution.edu"
            type="email"
            required
          />
        </label>

        <label>
          Password
          <input
            autoComplete="new-password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="Minimum 8 characters"
            type="password"
            minLength={8}
            required
          />
        </label>

        <p className="field-note">
          Use at least eight characters.
        </p>

        {error && (
          <p className="error" role="alert">
            {error}
          </p>
        )}

        <button className="auth-submit" disabled={loading}>
          {loading ? "Creating workspace..." : "Create account"}
        </button>
      </form>
    </AuthShell>
  );
}
