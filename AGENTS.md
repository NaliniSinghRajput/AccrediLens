# AGENTS.md

## Mission

Help maintain AccrediLens as a local-first, evidence-grounded accreditation review tool. Preserve source traceability, local-data privacy and mandatory human review.

## Repository map

- `frontend/`: Next.js 14, React and TypeScript user interface.
- `backend/`: FastAPI API, ingestion worker, retrieval and local Ollama integration.
- `docker-compose.yml`: PostgreSQL, Redis and Qdrant services.
- `turn-on.ps1` / `turn-off.ps1`: Windows lifecycle scripts.
- `docs/demo-evidence.pdf`: non-confidential ingestion test document.
- `ARCHITECTURE.md`: component, data-flow and trust-boundary reference.

## Non-negotiable rules

1. Never commit `.env` files, keys, tokens, databases, uploads, institutional evidence, personal data or model weights.
2. Do not claim that generated text is an accreditation decision. Answers must remain reviewable and source-grounded.
3. Preserve page, section, paragraph and chunk metadata through ingestion and retrieval changes.
4. Keep the standard development endpoints consistent: frontend `localhost:3001`, backend `127.0.0.1:8000`.
5. Keep Ollama inference local unless an explicit, documented design decision changes the privacy boundary.
6. Do not silently weaken authentication, CORS, citation requirements or evidence isolation.

## Change workflow

1. Read `README.md`, `ARCHITECTURE.md` and the files affected by the task.
2. Keep changes scoped; do not reformat unrelated files.
3. Update documentation when ports, environment variables, models, commands or architecture change.
4. Run the same checks as CI before publishing:
   - `docker compose config`
   - `python -m compileall -q backend/app`
   - PowerShell parser checks for `turn-on.ps1` and `turn-off.ps1`
   - `npm ci`, `npm run lint`, `npx tsc --noEmit`, and `npm run build` in `frontend/`
5. Report anything not tested, especially Ollama-dependent ingestion or inference.

## Definition of done

A change is complete when it is minimal, documented, does not expose sensitive data, preserves evidence traceability, and the GitHub Actions CI workflow is green.
