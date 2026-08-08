# AccrediLens Agent Skills

This file describes the bounded capabilities exercised by the AccrediLens evidence assistant. It is a capability manifest, not permission for autonomous accreditation decisions.

## 1. Evidence ingestion

**Input:** non-confidential, text-based PDF evidence.

**Actions:** validate the upload, extract text, preserve page/paragraph metadata, create chunks, generate local embeddings and index them in Qdrant.

**Output:** a searchable evidence record with processing status and traceable chunks.

**Boundary:** scanned image-only PDFs require OCR, which is not currently implemented.

## 2. Evidence retrieval

**Input:** a reviewer question or accreditation criterion.

**Actions:** embed the query, retrieve semantically relevant chunks, apply configured score/quantity thresholds and assemble bounded context.

**Output:** ranked source passages with document and location metadata.

**Boundary:** retrieval relevance does not prove institutional compliance.

## 3. Grounded question answering

**Input:** reviewer question plus retrieved evidence.

**Actions:** prompt the local Ollama model to answer only from supplied context and attach source references.

**Output:** a draft answer with citations for human verification.

**Boundary:** the assistant must expose insufficient evidence and must not invent missing facts.

## 4. Criterion analysis and tutoring

**Input:** a criterion, topic or evidence set.

**Actions:** explain requirements, summarize evidence, identify supported and unsupported aspects, and provide reviewer-oriented guidance.

**Output:** explanatory analysis tied to evidence where evidence is available.

**Boundary:** educational guidance is not an official accreditation judgment.

## 5. Privacy-preserving local inference

**Actions:** use local PostgreSQL, Redis, Qdrant and Ollama services; keep model weights and evidence outside Git.

**Boundary:** agents and contributors must never commit credentials, uploads, institutional records, personal data, databases or local model files.

## 6. Operational diagnostics

**Actions:** check backend health, service ports, Docker dependencies, worker availability and frontend build health; give actionable startup errors.

**Output:** reproducible diagnostic information without exposing secrets.

## Human control

A human reviewer controls uploads, questions, interpretation and final decisions. AccrediLens supports evidence review; it does not replace an accreditation authority.
