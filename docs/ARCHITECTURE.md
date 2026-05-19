# PawConscious Mesh — Architecture

## System overview

```
                          USER (brand owner)
                                  │ paste product URL
                                  ▼
                       ┌──────────────────────────┐
                       │ Next.js portal (pawcon-  │
                       │ scious.com/mesh)         │
                       └──────────┬───────────────┘
                                  │ POST /a2a/v1/tasks/send (202 async)
                                  ▼
                       ┌──────────────────────────┐
                       │ Vertex AI Agent Engine   │
                       │ (managed orchestrator)   │
                       │                          │
                       │ ParallelAgent ──fan-out──┐
                       │ SequentialAgent ←merge───┤
                       └──────────┬───────────────┘
                                  │ A2A v0.3
        ┌─────────────────┬───────┴────────┬──────────────────┬───────────────────┐
        ▼                 ▼                ▼                  ▼                   ▼
  ┌──────────┐     ┌──────────────┐  ┌─────────┐       ┌────────────┐      ┌──────────┐
  │ claim-   │     │ evidence-    │  │ vet-    │       │ compliance │      │ auditor  │
  │ extractor│     │ grader       │  │ panel   │       │            │      │(Falsifier│
  │          │     │              │  │         │       │            │      │ port)    │
  │ ADK +    │     │ ADK + Gemini │  │ ADK +   │       │ ADK +      │      │ ADK +    │
  │ Gemini   │     │ 3 Pro        │  │ Gemini  │       │ Gemini     │      │ Gemini   │
  │ 3 Pro    │     │              │  │ 3 Pro   │       │ 3 Pro      │      │ 2.5 Flash│
  └────┬─────┘     └──────┬───────┘  └────┬────┘       └─────┬──────┘      └────┬─────┘
       │ Firecrawl       │ BioMCP +       │ Vertex AI         │ Vertex AI         │ ADK
       │ MCP             │ AI2 Asta MCP   │ Search            │ Search            │ Eval
       │                 │ + Gemini       │ (vet handbook     │ (FTC §255 +       │
       │                 │ grounding      │  corpus)          │  NASC + AAFCO)    │
       ▼                 ▼                ▼                   ▼                   ▼
  Claims list      Cited evidence    Rubric scores       Regulator map      Audit verdict
       │                 │                │                   │                   │
       └─────────────────┴────────────────┴───────────────────┴───────────────────┘
                                            │ merge
                                            ▼
                              ┌──────────────────────────┐
                              │ SequentialAgent          │
                              │ - assemble PCEC bundle   │
                              │ - sign with Ed25519      │
                              │ - anchor in transparency │
                              │   log                    │
                              └──────────┬───────────────┘
                                         │
                  ┌──────────────────────┼──────────────────────┐
                  ▼                      ▼                      ▼
            ┌────────────┐        ┌────────────┐        ┌────────────┐
            │ Cloud SQL  │        │ Firestore  │        │ BigQuery   │
            │ cert       │        │ trans-     │        │ audit chain│
            │ registry   │        │ parency log│        │ + analytics│
            └────────────┘        └────────────┘        └────────────┘
                  │                      │                      │
                  └──────────────────────┼──────────────────────┘
                                         ▼
                          ┌─────────────────────────────┐
                          │ Output artifacts             │
                          │  - Verified-by-Vets badge JS │
                          │  - Audit-grade PDF           │
                          │  - PCEC JSON-LD              │
                          │  - Drafted vet outreach      │
                          └─────────────────────────────┘

                          + Public A2A agent card at
                            /.well-known/agent-card.json
                            (callable by Rufus, Perplexity,
                             ChatGPT commerce, Gemini Shopping,
                             any A2A v0.3 agent)
```

## Component-by-component

### Vertex AI Agent Engine — orchestrator
- ADK 2.0 `ParallelAgent` fans out to 5 specialist agents simultaneously
- `SequentialAgent` merges results, runs the auditor as final gate, signs the PCEC bundle
- Registered as a discoverable resource for Gemini Enterprise plug-in pattern

### Agent: claim-extractor
- Input: product URL
- Tools: Firecrawl MCP (PDP scrape), Gemini 3 Pro (claim extraction)
- Output: structured `Claim[]` per PDP — claim text, claim kind (efficacy/safety/ingredient/expert), position on page

### Agent: evidence-grader (PRODUCTION-QUALITY)
- Input: `Claim[]`
- Tools (dual path per codex G7 P0.2):
  - **BioMCP** (primary, off-GCP) — PubMed, Europe PMC, Semantic Scholar, ClinicalTrials.gov in one MCP
  - **PubMed-in-BigQuery + Vertex AI Search** (Google-first parallel path) — public PubMed dataset loaded into BigQuery, indexed by Vertex AI Search, queried via Gemini-grounded retrieval. Hits "first-party Google" rubric dimension judges look for.
  - **AI2 Asta MCP** (grading layer) — citation count, influential-citation count
  - **Gemini grounding with Google Search** (situational opener) — open-web context for breadth, never as sole source
- Output: per-claim `Evidence` — papers found (real PMIDs), relevance scores, citation-influence ranking. Language is "automated draft triage," not "regulator-grade grading."

### Agent: vet-panel (THIN per codex G7 P1.4)
- Input: `Claim[]` + `Evidence`
- Tools: Gemini 3 Pro with a prompt-encoded 5-vet rubric simulation
- Output: per-claim 1-5 rubric score, escalation flag for human-vet review
- **No Vertex AI Search**, **no licensed handbook ingest**, **no Plumb's** — pure prompt-based for hackathon to avoid licensing risk (codex G7 P0.7)

### Agent: compliance (THIN)
- Input: `Claim[]`
- Tools: Vertex AI Search over **public-redistributable corpus only** — FTC 16 CFR §255 federal text (public domain), AAFCO public-side docs, NASC public-side seal program docs, FDA-CVM GFI public list
- Output: per-claim regulator mapping, violation flags
- **No member-only NASC content. No state vet board paid corpora.**

### Agent: auditor (Falsifier port, THIN per codex G7 P1.6)
- Input: full merged bundle (claims + evidence + vet scores + compliance map)
- Tools: Gemini 2.5 Flash consistency check (NOT full ADK Eval — datasets don't exist in 18 days)
- Output: `AuditVerdict` (PASS/FAIL/CONDITIONAL) — checks: citation existence (does the PMID actually exist), claim-direction match (does the paper support the direction claimed). No cherry-pick detection, no sample-size adequacy in v0.1.

### Agent: ShopperAgent (DEMO-PURPOSE, separate service)
- Input: user shopping intent (e.g., "best joint supplement for senior labs")
- Tools: fetch `https://mesh-api-40952019806.us-central1.run.app/.well-known/agent-card.json`, call `verify_claim()` via A2A v0.3
- Output: ranked product list with trust scores attached
- **Source publicly committed to repo** so judges can verify the external A2A call is real, not staged. This is the live moment in the demo (codex G7 P0.4).

## Data layer

- **Firestore:** transparency log (append-only), per-brand state, agent run history
- **Cloud SQL:** cert registry (ACID, regulator-grade), expert DID metadata
- **BigQuery:** audit chain analytics, claim-taxonomy data flywheel
- **Cloud Storage:** raw PDP captures, evidence PDFs, generated audit-grade PDFs
- **Vertex Memory Bank (Preview):** per-brand context that persists across sessions
- **Secret Manager:** API keys for BioMCP, AI2 Asta, Firecrawl

## Public surfaces

- `https://mesh-api-40952019806.us-central1.run.app/portal` — brand-owner UI (Next.js, ports from existing PawConscious)
- `https://mesh-api-40952019806.us-central1.run.app/console` — Mesh Console (live A2A traffic viz, ports from GUARDIAN Ops Center)
- `https://mesh-api-40952019806.us-central1.run.app/.well-known/agent-card.json` — public A2A card
- `https://mesh-api-40952019806.us-central1.run.app/a2a/v1/tasks/send` — A2A endpoint
- `https://resolve.pcec.dev/v0/claim/{urn}` — PCEC resolver (separate domain, neutral)
- `https://mesh-api-40952019806.us-central1.run.app/embed/{certId}.js` — badge embed (ports from existing PawConscious)

## Security

- Vet DIDs use `did:web` for hackathon (DNS-based, simple); migrate to `did:key` + verifiable presentations post-v1
- Ed25519 software signing for hackathon; HSM (Cloud HSM or AWS KMS-backed) for v1
- A2A endpoint rate-limited per IP (Cloud Armor)
- Firestore transparency log is public-read, agent-write only
- All MCP credentials in Secret Manager

## Observability

- ADK Eval runs in CI per PR (5 evalsets, gemini-3-flash-preview judge)
- Vertex AI Agent Engine built-in tracing
- Cloud Logging + Cloud Trace per agent
- BigQuery audit chain queryable for ad-hoc forensics

## Deployment

- Cloud Run per agent (5 services + orchestrator + portal + console + resolver = 9 services)
- Cloud Build pipeline triggered on `main` push
- GitHub Actions secondary CI for ADK Eval gates
- Domain: `mesh-api-40952019806.us-central1.run.app` (Cloudflare DNS → Cloud Run via Load Balancer or direct)
- Hosted submission URL: `mesh-api-40952019806.us-central1.run.app` (canonical) or `pawconscious-mesh.run.app` (fallback)
