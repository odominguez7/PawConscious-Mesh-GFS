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
                                  │ POST /api/validate
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

### Agent: evidence-grader
- Input: `Claim[]`
- Tools:
  - **BioMCP** (primary) — PubMed, Europe PMC, Semantic Scholar, ClinicalTrials.gov, MyVariant in one MCP
  - **AI2 Asta MCP** (grading layer) — citation count, influential-citation count, citation graph
  - **Gemini grounding** (situational) — open-web context
- Output: per-claim `Evidence` — papers found, relevance scores, citation influence

### Agent: vet-panel
- Input: `Claim[]` + `Evidence`
- Tools: Vertex AI Search over vet handbook corpus (Plumb's OSS subset + AAFCO public + NASC public), Gemini 3 Pro for rubric application
- Output: per-claim 1-5 rubric score, escalation flag for human-vet review

### Agent: compliance
- Input: `Claim[]`
- Tools: Vertex AI Search over FTC §255 + NASC + AAFCO + state vet board corpus, Gemini 3 Pro
- Output: per-claim regulator mapping, violation flags

### Agent: auditor (GUARDIAN Falsifier port)
- Input: full merged bundle (claims + evidence + vet scores + compliance map)
- Tools: ADK Eval (4 SOP gates), Gemini 2.5 Flash adversarial pass
- Output: `AuditVerdict` (PASS/FAIL/CONDITIONAL) + findings list (cherry-pick detection, citation-existence check, claim-direction match, sample-size adequacy)

## Data layer

- **Firestore:** transparency log (append-only), per-brand state, agent run history
- **Cloud SQL:** cert registry (ACID, regulator-grade), expert DID metadata
- **BigQuery:** audit chain analytics, claim-taxonomy data flywheel
- **Cloud Storage:** raw PDP captures, evidence PDFs, generated audit-grade PDFs
- **Vertex Memory Bank (Preview):** per-brand context that persists across sessions
- **Secret Manager:** API keys for BioMCP, AI2 Asta, Firecrawl

## Public surfaces

- `https://mesh.pawconscious.com/portal` — brand-owner UI (Next.js, ports from existing PawConscious)
- `https://mesh.pawconscious.com/console` — Mesh Console (live A2A traffic viz, ports from GUARDIAN Ops Center)
- `https://mesh.pawconscious.com/.well-known/agent-card.json` — public A2A card
- `https://mesh.pawconscious.com/a2a/v1/tasks/send` — A2A endpoint
- `https://resolve.pcec.dev/v0/claim/{urn}` — PCEC resolver (separate domain, neutral)
- `https://mesh.pawconscious.com/embed/{certId}.js` — badge embed (ports from existing PawConscious)

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
- Domain: `pawconscious.com/mesh` (Cloudflare DNS → Cloud Run via Load Balancer or direct)
- Hosted submission URL: `pawconscious.com/mesh` (canonical) or `pawconscious-mesh.run.app` (fallback)
