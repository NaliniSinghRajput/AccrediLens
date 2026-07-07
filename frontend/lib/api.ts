const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export type Paper = {
  id: string;
  title: string | null;
  original_filename: string;
  status: string;
  error_message: string | null;
  created_at: string;
  processed_at: string | null;
  page_count?: number;
  paragraph_count?: number;
  chunk_count?: number;
};

export type Source = {
  chunk_id: string;
  page_number: number;
  section_title: string;
  paragraph_start: number;
  paragraph_end: number;
  source_type: string;
  score: string;
  text_excerpt: string;
};

export type Answer = {
  id: string;
  mode: string;
  answer: string;
  tutor_explanation: string | null;
  confidence: string;
  sources: Source[];
  created_at: string;
};

export function getToken() {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem("lms_token");
}

export function setToken(token: string) {
  window.localStorage.setItem("lms_token", token);
}

export function clearToken() {
  window.localStorage.removeItem("lms_token");
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers = new Headers(init.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (!(init.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_BASE_URL}${path}`, { ...init, headers });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed with status ${response.status}`);
  }
  return response.json();
}

export const api = {
  register: (payload: { email: string; password: string; full_name: string }) =>
    request<{ id: string; email: string; full_name: string }>("/auth/register", {
      method: "POST",
      body: JSON.stringify(payload)
    }),
  login: (payload: { email: string; password: string }) =>
    request<{ access_token: string; token_type: string }>("/auth/login", {
      method: "POST",
      body: JSON.stringify(payload)
    }),
  uploadPaper: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return request<Paper>("/papers/upload", { method: "POST", body: form });
  },
  listPapers: () => request<Paper[]>("/papers"),
  getPaper: (paperId: string) => request<Paper>(`/papers/${paperId}`),
  processPaper: (paperId: string) => request<{ status: string; job_id: string }>(`/papers/${paperId}/process`, { method: "POST" }),
  getStatus: (paperId: string) => request<{ paper_id: string; status: string; error_message: string | null }>(`/papers/${paperId}/status`),
  ask: (paperId: string, question: string) =>
    request<Answer>(`/papers/${paperId}/ask`, { method: "POST", body: JSON.stringify({ question }) }),
  tutor: (paperId: string, question: string) =>
    request<Answer>(`/papers/${paperId}/tutor`, { method: "POST", body: JSON.stringify({ question }) }),
  answers: (paperId: string) => request<Answer[]>(`/papers/${paperId}/answers`),
  answerSources: (answerId: string) => request<Source[]>(`/answers/${answerId}/sources`)
};
