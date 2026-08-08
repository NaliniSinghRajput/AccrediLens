# Local Intelligent LMS

YouTube Link:- https://youtu.be/OT_tZVG7PaI?si=fymGlFuaon_3ZI87

A local-first Intelligent Learning Management System for research paper Q&A.

This application allows a user to upload a research paper PDF, process it locally, create embeddings, store chunks in a vector database, and ask questions based only on the uploaded PDF.

The system is designed so that the LLM does not answer directly from its own general knowledge. It first retrieves relevant evidence from the selected PDF and then answers using only that evidence.

## Current Status

Working local MVP.

Tested successfully on Windows 11 with:

- Docker Desktop
- PostgreSQL
- Redis
- Qdrant
- FastAPI backend
- Next.js frontend
- Ollama local AI runtime
- qwen3:8b
- nomic-embed-text

## Core Features

- User registration and login
- PDF upload
- PDF processing status
- Research paper library
- PDF text extraction
- Page-wise metadata
- Paragraph extraction
- Chunk creation
- Local embedding generation
- Qdrant vector search
- Direct Q&A mode
- Tutor-style explanation mode
- Answer history
- Source references with page, section, paragraph, chunk, and source type
- Fully local AI inference
- No OpenAI API
- No cloud LLM API

## Architecture

```text
Browser
  |
  | Next.js / React frontend
  |
FastAPI backend
  |
  | PDF parsing, chunking, retrieval, answer generation
  |
PostgreSQL + Qdrant + Redis + Ollama
```

## Services

| Service | Purpose | URL / Port |
|---|---|---|
| Frontend | Website interface | http://localhost:3000 |
| Backend | FastAPI server | http://localhost:8000 |
| Backend health check | API status | http://localhost:8000/health |
| PostgreSQL | Metadata database | localhost:5432 |
| Redis | Background job queue | localhost:6379 |
| Qdrant | Vector database | http://localhost:6333 |
| Ollama | Local AI runtime | http://localhost:11434 |

## Folder Structure

```text
intelligent-lms
├── backend
│   ├── app
│   │   ├── api
│   │   ├── core
│   │   ├── services
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── worker.py
│   ├── storage
│   ├── .env.example
│   └── requirements.txt
├── frontend
│   ├── app
│   ├── components
│   ├── lib
│   ├── .env.example
│   └── package.json
├── docker-compose.yml
├── turn-on.ps1
├── turn-off.ps1
├── .gitignore
└── README.md
```

## Required Software

Install these before running the project:

1. Docker Desktop
2. Python 3.11
3. Node.js
4. Ollama for Windows
5. VS Code, recommended

## Important Python Note

Use Python 3.11 for this project.

Do not use Python 3.14 for this project because some Python packages may not have stable Windows wheels yet.

Check installed Python versions:

```powershell
py -0p
```

Create the backend virtual environment using Python 3.11:

```powershell
py -3.11 -m venv .venv
```

## Ollama Models

Install Ollama for Windows from:

```text
https://ollama.com/download/windows
```

Then pull the required local models:

```powershell
ollama pull qwen3:8b
ollama pull nomic-embed-text
```

Optional faster model:

```powershell
ollama pull qwen3:4b
```

The current MVP works with only:

```text
qwen3:8b
nomic-embed-text
```

## First-Time Setup

Open PowerShell and go to the project folder:

```powershell
cd C:\Projects\intelligent-lms
```

Create environment files:

```powershell
copy backend\.env.example backend\.env
copy frontend\.env.example frontend\.env.local
```

Start Docker services:

```powershell
docker compose up -d
```

Check Docker services:

```powershell
docker compose ps
```

Expected services:

```text
postgres
redis
qdrant
```

## Backend Setup

Go to backend folder:

```powershell
cd C:\Projects\intelligent-lms\backend
```

Create virtual environment:

```powershell
py -3.11 -m venv .venv
```

Check Python version:

```powershell
.\.venv\Scripts\python.exe --version
```

It should show Python 3.11.x.

Install backend packages:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Start backend:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Check backend:

```text
http://localhost:8000/health
```

Expected output:

```json
{"status":"ok"}
```

## Worker Setup

Open a second PowerShell window.

Run:

```powershell
cd C:\Projects\intelligent-lms\backend
.\.venv\Scripts\python.exe -m app.worker
```

The worker processes uploaded PDFs in the background.

On Windows, the worker must use RQ `SimpleWorker`, not the default fork-based worker.

## Frontend Setup

Open a third PowerShell window.

Run:

```powershell
cd C:\Projects\intelligent-lms\frontend
npm.cmd install
npm.cmd run dev
```

Open:

```text
http://localhost:3000
```

If PowerShell blocks `npm`, use:

```powershell
npm.cmd
```

instead of:

```powershell
npm
```

## Daily Use: Turn On Script

The project includes a startup script:

```text
turn-on.ps1
```

Run it from the project root:

```powershell
cd C:\Projects\intelligent-lms
powershell -ExecutionPolicy Bypass -File .\turn-on.ps1
```

This script starts:

- Docker services
- Ollama
- FastAPI backend
- Background worker
- Next.js frontend
- Browser at http://localhost:3000

## Daily Use: Turn Off Script

The project includes a shutdown script:

```text
turn-off.ps1
```

Run it from the project root:

```powershell
cd C:\Projects\intelligent-lms
powershell -ExecutionPolicy Bypass -File .\turn-off.ps1
```

This script stops:

- Frontend
- Backend
- Worker
- Ollama
- Docker services

## Recommended Daily Workflow

To start:

```powershell
cd C:\Projects\intelligent-lms
powershell -ExecutionPolicy Bypass -File .\turn-on.ps1
```

To stop:

```powershell
cd C:\Projects\intelligent-lms
powershell -ExecutionPolicy Bypass -File .\turn-off.ps1
```

## How To Use The App

1. Open the website:

```text
http://localhost:3000
```

2. Register a local user.

3. Login.

4. Upload a research paper PDF.

5. Wait until the paper status becomes:

```text
READY
```

6. Open the paper.

7. Ask a question.

8. Check the answer, confidence level, and references.

## Example Questions

Good specific questions:

```text
What problem does the proposed federated learning model solve?
```

```text
What methodology is used in this paper?
```

```text
What datasets or simulation tools are mentioned?
```

```text
What are the main results of this paper?
```

Avoid very broad questions like:

```text
What does this paper tell you?
```

Broad questions may produce lower confidence because retrieval is less precise.

## Answer Format

The intended answer format is:

```text
Answer:
Answer based only on retrieved PDF evidence.

Tutor Explanation:
Simple explanation based only on the paper evidence.

References:
1. Page number, section title, paragraph number, source type, chunk ID

Confidence:
High / Medium / Low
```

If the PDF does not contain enough evidence, the system should answer:

```text
The uploaded paper does not provide enough information to answer this question.
```

## RAG Flow

The question does not go directly to the LLM.

Correct flow:

```text
User question
  ↓
Question embedding
  ↓
Vector search filtered by selected paper_id
  ↓
Reranking / scoring
  ↓
Evidence sufficiency check
  ↓
Local LLM answer using retrieved chunks only
  ↓
Citations added from source metadata
```

## Local-Only AI

This project does not use:

- OpenAI API
- Cloud LLM API
- External AI services

The AI models run locally through Ollama.

The backend talks to Ollama at:

```text
http://localhost:11434
```

## Databases

PostgreSQL stores:

- users
- papers
- pages
- paragraphs
- chunks
- questions
- answers
- answer sources
- processing jobs

Qdrant stores:

- vector embeddings
- chunk metadata
- paper_id filters

Redis handles:

- background job queue

## Important Files

Backend entry point:

```text
backend/app/main.py
```

Worker:

```text
backend/app/worker.py
```

PDF parser:

```text
backend/app/services/pdf_parser.py
```

Chunker:

```text
backend/app/services/chunker.py
```

RAG logic:

```text
backend/app/services/rag.py
```

Ollama client:

```text
backend/app/services/ollama_client.py
```

Vector store:

```text
backend/app/services/vector_store.py
```

Frontend pages:

```text
frontend/app
```

Frontend API client:

```text
frontend/lib/api.ts
```

## Common Problems And Fixes

### Problem: npm is not recognized

Install Node.js LTS.

Then close PowerShell and open a new PowerShell window.

Check:

```powershell
node --version
npm.cmd --version
```

### Problem: npm.ps1 cannot be loaded

Use:

```powershell
npm.cmd install
npm.cmd run dev
```

instead of:

```powershell
npm install
npm run dev
```

### Problem: Python package install fails with psycopg2-binary

Use Python 3.11, not Python 3.14.

Recreate venv:

```powershell
cd C:\Projects\intelligent-lms\backend
Remove-Item -Recurse -Force .venv
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Problem: password cannot be longer than 72 bytes

This is usually caused by incompatible bcrypt version.

Use:

```powershell
.\.venv\Scripts\python.exe -m pip install "bcrypt==4.0.1" --force-reinstall
```

Also make sure `requirements.txt` contains:

```text
bcrypt==4.0.1
```

### Problem: Worker crashes with os.fork error on Windows

Windows does not support `os.fork`.

The worker must use `SimpleWorker`.

In `backend/app/worker.py`, use:

```python
from rq import Queue, SimpleWorker
```

and:

```python
worker = SimpleWorker([Queue("paper-processing", connection=redis)], connection=redis)
```

### Problem: Frontend moves from port 3000 to 3001

This means port 3000 is already in use.

This is called a port conflict.

Fix:

```powershell
powershell -ExecutionPolicy Bypass -File .\turn-off.ps1
powershell -ExecutionPolicy Bypass -File .\turn-on.ps1
```

### Problem: PDF stays processing

Check worker window.

If worker crashed, restart worker:

```powershell
cd C:\Projects\intelligent-lms\backend
.\.venv\Scripts\python.exe -m app.worker
```

## GitHub Notes

Before uploading to GitHub, make sure these are not committed:

```text
backend/.env
frontend/.env.local
backend/storage/uploads
node_modules
.venv
.next
```

These should be ignored by `.gitignore`.

Recommended repository visibility:

```text
Private
```

At least until the project is cleaned and hardened.

## Current Limitations

This is a working MVP, not the final production system.

Current limitations:

- No OCR fallback yet
- No PDF page highlighting yet
- No advanced reranker yet
- No admin dashboard yet
- No course/module structure yet
- No quiz generation yet
- No flashcard generation yet
- No Alembic migrations yet
- No production authentication hardening yet

## Future Improvements

Planned improvements:

- Better source viewer
- PDF page preview
- Highlight exact source text
- Stronger reranker
- Grounding verifier
- OCR fallback using Tesseract
- Quiz generation from PDF only
- Flashcard generation from PDF only
- Course/module organization
- Admin settings
- Better UI
- One-click Windows desktop launcher
- GitHub Actions checks
- Alembic migrations
- Dockerized backend and frontend

## Local Test Account

Create any local account from the Register page.

Example:

```text
Name: Prof. N. S. Rajput
Email: prof.rajput.local@example.com
Password: LocalLMS@2026!
```

Do not use this password for any real online account.

## License

For internal local development and research use.

Add a formal license later before public release.
## Quick start

### Requirements

- Python 3.11+
- Node.js 20+ and npm
- Docker Desktop with Docker Compose
- PostgreSQL, Redis, and Qdrant
- Git

### Backend

    cd backend
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

Set `FRONTEND_ORIGIN=http://localhost:3001` in the backend environment.

### Frontend

Create `frontend/.env.local` containing:

    NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000

Then run:

    cd frontend
    npm install
    npm run dev -- --port 3001

Open http://localhost:3001.

### Demo PDF

Use the included [demo evidence PDF](docs/demo-evidence.pdf) to test document ingestion.

### Models and sensitive files

Large model weights are not committed. Provision them separately when required. Never commit `.env` files, API keys, databases, uploaded evidence, or user information.

If backend port 8000 is occupied, run it on port 8001 and change `NEXT_PUBLIC_API_BASE_URL` accordingly.
