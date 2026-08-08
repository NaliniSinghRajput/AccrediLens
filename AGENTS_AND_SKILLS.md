# Agents and Skills

This document is the judge-facing manifest for AccrediLens. It combines the repository operating rules in [AGENTS.md](AGENTS.md) with the bounded product capabilities in [SKILLS.md](SKILLS.md).

## Agent mission

AccrediLens is a local-first accreditation evidence assistant. Its agents help reviewers ingest evidence, retrieve source passages, draft grounded answers and identify missing support. They do not make official NBA or NAAC decisions.

## Agent roles

| Agent | Responsibility | Required output |
|---|---|---|
| Ingestion agent | Validate PDFs, extract text, retain page/paragraph metadata, chunk and index evidence | Traceable evidence records and processing status |
| Retrieval agent | Match questions or criteria to semantically relevant chunks | Ranked passages with document locations |
| Grounded-answer agent | Draft answers from retrieved context only | Reviewable answer with citations or an insufficient-evidence notice |
| Criterion-analysis agent | Compare available evidence with accreditation requirements | Supported, unsupported and missing-evidence findings |
| Operations agent | Check service health, ports, builds and local dependencies | Actionable diagnostics without secrets |

## Skills

1. **Evidence ingestion** — process non-confidential text PDFs while preserving provenance.
2. **Semantic retrieval** — retrieve bounded, ranked evidence from Qdrant.
3. **Grounded generation** — use local Ollama inference and cite supplied sources.
4. **Criterion analysis** — explain requirements and highlight evidence gaps.
5. **Privacy-preserving operation** — keep evidence, databases, secrets and model weights out of Git.
6. **Operational diagnostics** — verify the API, worker, frontend and supporting services.

## Safety and quality rules

- Human review is mandatory for every accreditation conclusion.
- Never fabricate evidence or citations; state when evidence is insufficient.
- Never commit credentials, uploads, institutional records, personal data, databases or model weights.
- Preserve source locations throughout ingestion and retrieval.
- Do not weaken authentication, CORS, evidence isolation or citation requirements.
- Keep standard development endpoints at frontend `localhost:3001` and backend `127.0.0.1:8000`.

## Definition of done

A change is complete only when it is scoped, documented, privacy-safe, traceable and accepted by the GitHub Actions checks, including the Playwright browser smoke test.
