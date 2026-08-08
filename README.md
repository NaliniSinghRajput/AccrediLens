# AccrediLens

AccrediLens is a local-first accreditation evidence intelligence application. It ingests institutional PDF evidence, extracts and chunks the text, retrieves relevant passages, and produces source-grounded answers for human review.

> Status: working local MVP for research and demonstration. It is not a production accreditation decision system.

## What it does

- Local user registration and login
- PDF evidence upload and background processing
- Evidence library with processing status
- PDF text extraction, paragraph metadata, and chunking
- Local embeddings and Qdrant vector retrieval
- Direct Q&A, tutor explanations, and accreditation-criterion analysis
- Page-, section-, paragraph-, and chunk-level source references
- Local inference through Ollama; no OpenAI or cloud LLM API

## Architecture

```text
Next.js frontend
        |
   FastAPI API
        |
PostgreSQL + Redis/RQ + Qdrant + Ollama
```

## Requirements

- Windows 10/11 (the helper scripts are PowerShell)
- Python 3.11
- Node.js 20+ and npm
- Docker Desktop with Docker Compose
- Ollama
- Git

## Required local models

Model binaries are intentionally not committed to Git.

```powershell
ollama pull qwen3:8b
ollama pull qwen3:4b
ollama pull nomic-embed-text
```

The 4B model is used for faster tasks. If hardware is constrained, adjust the model names in `backend/.env`.

## First-time setup

From the repository root:

```powershell
Copy-Item backend/.env.example backend/.env
Copy-Item frontend/.env.example frontend/.env.local
docker compose up -d

Set-Location backend
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

Set-Location ../frontend
npm.cmd install
Set-Location ..
```

Use a long random value for `JWT_SECRET_KEY` in `backend/.env`. Never commit either environment file.

## Start the complete application

The recommended Windows startup command is:

```powershell
powershell -ExecutionPolicy Bypass -File .\turn-on.ps1
```

This starts Docker services, Ollama if needed, the API, the RQ worker, and the frontend.

- Frontend: http://localhost:3001
- Backend health: http://127.0.0.1:8000/health
- Qdrant: http://localhost:6333
- Ollama: http://localhost:11434

To stop the stack:

```powershell
powershell -ExecutionPolicy Bypass -File .\turn-off.ps1
```

## Manual development startup

Backend:

```powershell
Set-Location backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Worker, in another terminal:

```powershell
Set-Location backend
.\.venv\Scripts\python.exe -m app.worker
```

Frontend, in another terminal:

```powershell
Set-Location frontend
npm.cmd run dev -- --port 3001
```

## Demo PDF

Upload [docs/demo-evidence.pdf](docs/demo-evidence.pdf) for a basic ingestion smoke test. You can also upload any non-confidential, text-based accreditation or institutional PDF. Scanned image-only PDFs need OCR, which is not yet implemented.

## Configuration

The committed examples use one consistent local configuration:

```text
FRONTEND_ORIGIN=http://localhost:3001
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

If port 8000 is occupied, stop the stale listener. As a temporary workaround, run the backend on 8001 and change `NEXT_PUBLIC_API_BASE_URL` to `http://127.0.0.1:8001`, then restart Next.js.

## Repository safety

The repository excludes environment files, virtual environments, dependency folders, generated builds, uploads, databases, logs, and large model weights. Do not commit credentials, real institutional evidence, personal data, or Ollama model files.

## Current limitations

- No OCR fallback for scanned PDFs
- No production authentication hardening
- No Alembic migrations
- No advanced reranker or independent grounding verifier
- No formal accreditation decision automation; human review remains required

## Technology stack

FastAPI, SQLAlchemy, PostgreSQL, Redis/RQ, Qdrant, PyMuPDF, pdfplumber, Next.js, React, TypeScript, and Ollama.
