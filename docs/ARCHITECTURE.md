# PawConscious Mesh — Architecture

## System overview

```
                          USER (brand owner)
                                  │ paste product URL
                                  ▼
                       ┌──────────────────────────┐
                       │ Mesh-API (FastAPI)       │
                       │ services/mesh_api/main.py│
                       └──────────┬───────────────┘
                                  │ POST /a2a/v1/tasks/send (202 async)
                                  ▼
        STAGE 1 ─ Orchestrator (agents/orchestrator.py)
        ────────────────────────────────────────────────
                       ┌──────────────────────────┐
                       │ claim-extractor          │
                       │ (sequential, runs first) │
                       └──────────┬───────────────┘
                                  │ Claim[]
                                  ▼
                  per-claim asyncio.gather fan-out
        ┌─────────────────┬─────────────────┬─────────────────┐
        ▼                 ▼                 ▼                 │
  ┌──────────┐     ┌──────────────┐  ┌─────────┐              │
  │ evidence-│     │ vet-panel    │  │compliance│              │
  │ grader   │     │              │  │          │              │
  └────┬─────┘     └──────┬───────┘  └─────┬────┘              │
       │ BioMCP +         │ prompt-only    │ Vertex AI Search  │
       │ Semantic Scholar │ 5-vet rubric   │ (FTC + NASC +     │
       │ Graph API batch  │                │  AAFCO corpus)    │
       ▼                  ▼                ▼                   │
  EvidenceBundle    VetRubricScore   ComplianceMapping         │
       └──────────────────┴────────────────┘                   │
                          │ merged                             │
                          ▼                                    │
                       ┌──────────────────────────┐            │
                       │ auditor (Falsifier v0)   │            │
                       │ PMID format + direction  │            │
                       └──────────┬───────────────┘            │
                                  ▼                            │
                       AuditVerdict                            │
                                  │                            │
        ────────────────────────────────────────────────       │
        STAGE 2 ─ Mesh-API signing layer                       │
        ────────────────────────────────────────────────       │
                       ┌──────────────────────────┐            │
                       │ assemble PCEC v0.1       │            │
                       │ sign Ed25519             │            │
                       │ chain anchor =           │            │
                       │  sha256(bundle_hash      │            │
                       │  + ':' + prev_hash)      │            │
                       │ append to Firestore      │            │
                       │ transparency log         │            │
                       └──────────┬───────────────┘            │
                                  ▼                            │
        ────────────────────────────────────────────────       │
        STAGE 3 ─ A2A background worker (post-signing)         │
        ────────────────────────────────────────────────       │
                       ┌──────────────────────────┐            │
                       │ report-writer            │            │
                       │ Cert Composer (HTML)     │            │
                       │ + branded narrative      │            │
                       └──────────┬───────────────┘            │
                                  ▼                            │
                       ┌──────────────────────────┐            │
                       │ second-opinion           │            │
                       │ Google Search grounding  │            │
                       │ 4-stress-test pass       │            │
                       └──────────┬───────────────┘            │
                                  ▼                            │
                  ┌──────────────────────────────┐             │
                  │ Output artifacts (v0.1)       │            │
                  │  - PCEC v0.1 signed bundle    │            │
                  │  - Ed25519 signature          │            │
                  │  - Firestore chain anchor     │            │
                  │  - Cert HTML                  │            │
                  │  - Second-opinion verdict     │            │
                  └──────────────────────────────┘             │
                                                               │
                  + Public A2A agent card at                   │
                    /.well-known/agent-card.json   ◄───────────┘
                    (callable by any A2A v0.3 agent —
                     Rufus, Operator, Perplexity, Gemini
                     Shopping — verified by our own
                     ShopperAgent in this repo)
```

## Component-by-component

### Stage 1 — Orchestrator (`agents/orchestrator.py`)

The orchestrator implements a four-step pipeline:

1. `claim-extractor` runs first (sequential) and pulls `Claim[]` from the PDP.
2. For each claim, `asyncio.gather` fans out three agents in parallel: `evidence-grader`, `vet-panel`, `compliance`.
3. After the three results land, `auditor` runs on the merged per-claim evidence.
4. Returns an `EndorsementClaimBundle` (PCEC v0.1 shape) to the caller.

Production parallel primitive is `asyncio.gather`. ADK `ParallelAgent` + `SequentialAgent` wrappers are documented in the orchestrator docstring as the Phase 4 Vertex AI Agent Engine deployment surface — v0.1 ships with asyncio for deterministic stability under load.

### Agent: claim-extractor

- **Runtime SDK:** `google.genai` (called from `agents/orchestrator.py::extract_claims`)
- **ADK scaffold:** `agents/claim_extractor.py::build_claim_extractor_agent` declares the equivalent ADK `LlmAgent` + `FunctionTool` for Phase 4 Vertex AI Agent Engine deployment. v0.1 executes via `google.genai` direct for deterministic latency under load.
- **Model:** Gemini 2.5 Pro
- **Input:** product URL
- **Tools:** httpx + BeautifulSoup primary path; Firecrawl `/v2/scrape` fallback for retailer PDPs (Chewy/Petco/Amazon) that block direct scraping
- **Output:** structured `Claim[]` — claim text, claim kind (efficacy/safety/ingredient/expert), position on page

### Agent: evidence-grader

- **SDK:** `google.genai`
- **Model:** Gemini 2.5 Pro
- **Input:** `Claim`
- **Tools:**
  - **BioMCP** (primary) — PubMed, Europe PMC search via `from biomcp.articles.search import PubmedRequest, search_articles`. 21 biomedical tools, MIT, actively maintained
  - **Semantic Scholar Graph API batch** (`agents/citation_enricher.py`) — populates `citation_count` and `influential_citation_count` for every PMID returned by BioMCP. Public surface of AI2 Asta; MCP wrapper drops in when AI2 ships one. Batch endpoint preserves request order; 429-anonymous-tier path returns input unchanged (graceful)
- **Output:** per-claim `EvidenceBundle` — real PMIDs, relevance scores, citation influence

### Agent: vet-panel

- **SDK:** `google.genai`
- **Model:** Gemini 2.5 Pro
- **Input:** `Claim` + `Evidence`
- **Tools:** Prompt-only 5-vet rubric simulation. No Vertex AI Search, no licensed handbook ingest, no Plumb's (codex G7 P0.7 — avoid licensing risk)
- **Output:** per-claim 1-5 rubric score, escalation flag for human-vet review

### Agent: compliance

- **SDK:** `google.genai`
- **Model:** Gemini 2.5 Pro
- **Input:** `Claim`
- **Tools:** Vertex AI Search over **public-redistributable corpus only** — FTC 16 CFR §255 federal text (public domain), AAFCO public docs, NASC public-side seal program docs
- **Output:** per-claim `ComplianceMapping` with snippet-level `GroundingSource` (sha256-hashed for tamper-evidence)

### Agent: auditor (Falsifier v0)

- **SDK:** `google.genai`
- **Model:** Gemini 2.5 Flash
- **Input:** merged bundle (claims + evidence + vet scores + compliance map) per claim
- **Tools:** PMID format check + claim-direction match check
- **Output:** `AuditVerdict` (PASS/FAIL/CONDITIONAL). Real-existence verification of cited papers is a v0.2 follow-up via the `citation_enricher` hook now wired into evidence-grader.

### Stage 2 — Mesh-API signing layer (`services/mesh_api/main.py`)

Receives the `EndorsementClaimBundle` from the orchestrator, signs it with Ed25519, computes the chain anchor as `sha256(bundle_hash + ':' + (prev_hash or 'genesis'))`, and appends it to the Firestore transparency log.

### Stage 3 — A2A background worker (post-signing)

Runs after the bundle is signed. Best-effort; if either step fails, the frontend falls back to the static cert.

#### Agent: report-writer (Cert Composer)

- **SDK:** `google.genai`
- **Model:** Gemini 2.5 Pro
- **Input:** signed bundle
- **Output:** HTML certificate with branded layout, 150-200-word executive narrative, and "Ship before launch" actionable fixes

#### Agent: second-opinion

- **SDK:** `google.genai`
- **Model:** Gemini 2.5 Pro
- **Tools:** Google Search grounding via `google.genai` (`tools=[types.Tool(google_search=types.GoogleSearch())]`)
- **Input:** signed bundle + brand context
- **Behavior:** Runs 4 stress tests (COURT · REGULATOR · SCIENTIFIC CONSENSUS · PUBLIC SKEPTICISM) to try to break the bundle's conclusion using real-time external evidence (regulatory actions, plaintiff cases, scientific consensus shifts)
- **Output:** verdict + strongest counter + 1-line founder-voice summary
- **Proven impact:** flipped a Native Pet PASS → NEEDS REVIEW by surfacing an FDA warning letter and the Cosequin $11.5M class-action precedent

### ShopperAgent (separate service)

- **Input:** user shopping intent (e.g., "best joint supplement for senior labs")
- **Tools:** fetch `https://mesh-api-40952019806.us-central1.run.app/.well-known/agent-card.json`, call `verify_claim()` via A2A v0.3
- **Output:** ranked product list with trust scores attached
- **Source publicly committed** to repo so judges can verify the external A2A call is real, not staged

## Data layer

- **Firestore:** transparency log (append-only, chain anchored), per-task state
- **Cloud Storage:** raw PDP captures
- **Secret Manager:** API keys for BioMCP, Firecrawl, Semantic Scholar (optional — anonymous tier works)

## Public surfaces

**Shipped today (v0.1):**
- `https://mesh-api-40952019806.us-central1.run.app/` — Mesh Console (live A2A traffic viz)
- `https://mesh-api-40952019806.us-central1.run.app/architecture` — interactive architecture diagram
- `https://mesh-api-40952019806.us-central1.run.app/a2a/app/.well-known/agent-card.json` — public A2A card
- `https://mesh-api-40952019806.us-central1.run.app/a2a/v1/tasks/send` — A2A entry (async, 202)
- `https://mesh-api-40952019806.us-central1.run.app/a2a/v1/tasks/get/{task_id}` — poll for results
- `https://mesh-api-40952019806.us-central1.run.app/pcec/v0/chain/head` — public transparency log head
- `https://shopper-agent-40952019806.us-central1.run.app/` — ShopperAgent demo consumer

**Roadmap (v0.2+, not shipped):**
- `/portal` — brand-owner Next.js UI
- `/embed/{certId}.js` — badge embed
- `https://resolve.pcec.dev/v0/claim/{urn}` — neutral PCEC resolver domain

## Security

- Ed25519 software signing for hackathon; HSM-backed signing on the v0.2 roadmap
- A2A endpoint API-key-gated during hackathon (`X-API-Key`); rate-limited per IP
- Firestore transparency log is public-read, agent-write only
- All MCP credentials in Secret Manager

## Observability

- Cloud Logging + Cloud Trace per agent
- Per-agent latency tracked in `_progress` updates surfaced to the A2A status response
- ADK Eval runner scaffolded at `tests/adk_eval/run.py` — first cases written; cross-platform httpx/Cloud Run quirk under investigation before the badge goes green

## Deployment

- Cloud Run (per-service): `mesh-api`, `shopper-agent`
- Cloud Build pipeline triggered on `main` push (`cloudbuild.mesh-api.yaml`)
- Hosted submission URL: `mesh-api-40952019806.us-central1.run.app`
