# PawConscious Mesh — ACP for Pet

[![Live](https://img.shields.io/badge/live-mesh--api.run.app-13322B?style=flat-square&labelColor=1A1D1E)](https://mesh-api-40952019806.us-central1.run.app/)
[![Track 3](https://img.shields.io/badge/GFS%20Track%203-Gemini%20%2B%20Cloud%20Run%20%2B%20A2A%20%2B%20ADK%204%2F7-9C5E1A?style=flat-square&labelColor=1A1D1E)](https://mesh-api-40952019806.us-central1.run.app/architecture)
[![ADK eval](https://img.shields.io/badge/ADK%20eval-3%2F3%20eligible%20(baseline)-13322B?style=flat-square&labelColor=1A1D1E)](tests/adk_eval/results/latest.json)
[![MIT](https://img.shields.io/badge/license-MIT-13322B?style=flat-square&labelColor=1A1D1E)](LICENSE)

**The trust layer AI agents call before recommending a consumer product.**

Paste a product URL. Seven specialized agents on Google Cloud return a signed PCEC v0.1 evidence bundle in roughly 60-90 seconds (about 30 seconds per claim with the default of 3 claims per PDP). Any A2A v0.3 client can call it. Verifiable did:web signature. We grade evidence; your agent decides.

> **GFS judges, start here:**
> 1. Try the cached demo on `/`: [`https://mesh-api-40952019806.us-central1.run.app/`](https://mesh-api-40952019806.us-central1.run.app/)
> 2. Run one curl against the live A2A endpoint: see [Quickstart](#quickstart) below.
> 3. Check Track 3 compliance: see [Track 3 mandate map](#track-3-mandate-map).
> 4. Reproduce locally: see [`RUN.md`](RUN.md).

## Quickstart

Demo key for hackathon judges: `demo-key-2026-06`.

```bash
# 1. Submit a verify_claim task (async, 202 with task_id).
curl -X POST "https://mesh-api-40952019806.us-central1.run.app/a2a/v1/tasks/send" \
  -H "X-API-Key: demo-key-2026-06" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "verify_claim",
    "input": {
      "product_url": "https://www.nativepet.com/products/hip-joint",
      "max_claims": 3
    }
  }'

# 2. Poll the task (60–90s for a real PDP across all 7 agents).
curl "https://mesh-api-40952019806.us-central1.run.app/a2a/v1/tasks/get/<task_id>" \
  -H "X-API-Key: demo-key-2026-06"
```

The standard A2A v0.3 envelope with `params.message.parts[].text` is also accepted; see [`/agents`](https://mesh-api-40952019806.us-central1.run.app/agents) for the Python + TypeScript versions.

## Track 3 mandate map

Google for Startups AI Agents Challenge 2026 Track 3 (Refactor for Marketplace + Gemini Enterprise) requires B2B + Cloud Run/GKE + Gemini + A2A. Every mandate is satisfied in shipped code.

| Mandate | Where it is | How to verify |
|---|---|---|
| **B2B target** | DTC pet supplement brands (General Counsel / Compliance / CMO buyer). Pricing tiers + buyer-framed hero at [`/`](https://mesh-api-40952019806.us-central1.run.app/) | [`BUSINESS_PLAN.md`](BUSINESS_PLAN.md) |
| **Cloud Run** | `mesh-api` + `shopper-agent` services, us-central1, scale-to-zero, Artifact Registry images | `services/mesh_api/cloudbuild.yaml` + `services/shopper_agent/cloudbuild.yaml` |
| **Gemini** | Gemini 2.5 Pro (6 agents) + Gemini 2.5 Flash (auditor) via `google.genai` + Vertex AI | `agents/*.py` |
| **A2A v0.3** | Public agent card at [`/.well-known/agent-card.json`](https://mesh-api-40952019806.us-central1.run.app/.well-known/agent-card.json); dual-shape envelope (Linux Foundation standard + flat) | `services/mesh_api/main.py` POST `/a2a/v1/tasks/send` |
| **ADK** | 4 of 7 agents on Google ADK as `LlmAgent` + `FunctionTool` wrappers; `SequentialAgent` + `ParallelAgent` topology | [`/health/mesh-shape`](https://mesh-api-40952019806.us-central1.run.app/health/mesh-shape) returns the introspectable topology + `ratio_on_adk: "4/7"` |
| **Vertex AI Agent Engine** | Reasoning Engine deployed; routing flag with p95 gate + timeout (`ACP_USE_AGENT_ENGINE`) | [`/health/agent-engine`](https://mesh-api-40952019806.us-central1.run.app/health/agent-engine) returns the resource path + traffic-gate state |

## What the mesh actually does

```
                      BRAND PRODUCT URL
                              │
                              ▼
              ┌──────────────────────────────┐
              │ Stage 1 — orchestrator       │
              │ agents/orchestrator.py       │
              │ asyncio.gather fan-out       │
              │ ADK topology: SequentialAgent│
              │   [claim_extractor,          │
              │    ParallelAgent[evidence,   │
              │                 compliance], │
              │    auditor]                  │
              └──────────────┬───────────────┘
                             │
                  ┌─ claim_extractor (sequential first)
                  ▼
       per-claim parallel ──► evidence_grader (BioMCP → PubMed)
                          ──► vet_rubric (5-vet rubric simulation)
                          ──► compliance (Vertex AI Search → FTC §255)
                             │
                             ▼
                         auditor (Falsifier v0)
                             │
                             ▼
              ┌──────────────────────────────┐
              │ Stage 2 — mesh-api signing   │
              │ services/mesh_api/main.py    │
              │ Ed25519 + chain anchor       │
              │ sha256(bundle_hash:prev_hash)│
              │ → Firestore transparency log │
              └──────────────┬───────────────┘
                             ▼
              ┌──────────────────────────────┐
              │ Stage 3 — post-sign          │
              │ report_writer (HTML cert)    │
              │ second_opinion (Google       │
              │   Search grounded 4-stress)  │
              └──────────────┬───────────────┘
                             ▼
            signed PCEC v0.1 bundle + chain anchor
            + cert HTML + adversarial verdict
            + agent-card discoverable via A2A v0.3
```

For the interactive diagram with hover tooltips, see [`/architecture`](https://mesh-api-40952019806.us-central1.run.app/architecture).

## On the word "mesh"

Internally, the orchestrator is a single-process multi-agent pipeline (`asyncio.gather` fan-out across per-claim graders, sequential into the auditor). It is not an inter-service A2A topology.

We call the system "Mesh" because the **public A2A v0.3 agent card at the edge** is the discoverable, callable mesh. Any external A2A v0.3 client (our ShopperAgent reference, Amazon Rufus, Perplexity Shopping, an agent you build) becomes a node in the broader trust mesh by calling our two skills (`verify_claim`, `fetch_substantiation_bundle`). The internal pipeline serves the public mesh.

The 4-of-7 agents on ADK live as real `LlmAgent` + `FunctionTool` declarations; the runtime currently uses `asyncio.gather` for determinism and judge-visible debug. ADK Runner runtime path is gated behind the same feature-flag + p95-gate pattern as `ACP_USE_AGENT_ENGINE` (see `services/mesh_api/main.py`).

## The 7 agents

| Agent | SDK | Model | Tools | Output | On ADK |
|---|---|---|---|---|---|
| `claim_extractor` | `google.genai` + ADK `LlmAgent` | Gemini 2.5 Pro | httpx + BeautifulSoup primary, Firecrawl fallback | `list[Claim]` | ✅ |
| `evidence_grader` | `google.genai` + ADK `LlmAgent` | Gemini 2.5 Pro | BioMCP (PubMed) + Semantic Scholar Graph API batch | `EvidenceBundle` | ✅ |
| `vet_rubric` | `google.genai` direct | Gemini 2.5 Pro | Prompt-only 5-vet rubric **simulation** (LLM role-play; no real DVMs today; `attest_expert` skill replaces this with licensed-DVM attestation in v0.2) | `VetRubricScore` | ❌ by design (LLM role-play, not a real expert panel) |
| `compliance` | `google.genai` + ADK `LlmAgent` | Gemini 2.5 Pro | Vertex AI Search over FTC §255 + AAFCO PF7 + NASC public corpus | `ComplianceMapping` with snippet provenance | ✅ |
| `auditor` (Falsifier) | `google.genai` + ADK `LlmAgent` | Gemini 2.5 Flash | PMID format + claim-direction match check | `AuditVerdict` | ✅ |
| `report_writer` | `google.genai` direct | Gemini 2.5 Pro | Bundle composition | Human-readable HTML cert | ❌ post-sign rendering, not a reasoning agent |
| `second_opinion` | `google.genai` direct | Gemini 2.5 Pro | Google Search grounding | 4-stress-test verdict (COURT · REGULATOR · CONSENSUS · PUBLIC) | ❌ adversarial review, kept independent of the ADK runtime |

The 4/7-on-ADK split is intentional and documented at [`/health/mesh-shape`](https://mesh-api-40952019806.us-central1.run.app/health/mesh-shape). vet_rubric, report_writer, and second_opinion stay outside ADK because each one has a non-reasoning role (panel simulation, post-sign rendering, independent adversarial review) where the ADK abstractions add ceremony without adding correctness.

## A2A v0.3 — what is callable

Public agent card at [`/.well-known/agent-card.json`](https://mesh-api-40952019806.us-central1.run.app/.well-known/agent-card.json):

- `verify_claim` — paste a PDP URL, get the signed PCEC bundle + chain anchor (~30 seconds)
- `fetch_substantiation_bundle` — fetch a historical bundle by its `urn:pcec:claim:*` URN

Roadmap (v0.2+): `attest_expert` (licensed-DVM attestation), `revoke_bundle`.

The endpoint is API-key gated during the hackathon window (`demo-key-2026-06` above). Our `ShopperAgent` (source in `services/shopper_agent/`) is the live external consumer; see [`/demo/shopper`](https://mesh-api-40952019806.us-central1.run.app/demo/shopper) for the round-trip in action.

## PCEC v0.1 — the open spec

The output bundle conforms to the **Pet Claim Endorsement Credential v0.1**, our open spec stub. MIT licensed. Anyone can run their own mesh; we expect to be the reference implementation, not the only one.

Spec: [`docs/PCEC-v0.md`](docs/PCEC-v0.md). Issuer DID: `did:web:mesh-api-40952019806.us-central1.run.app`.

Chain anchor for the live transparency log: [`/pcec/v0/chain/head`](https://mesh-api-40952019806.us-central1.run.app/pcec/v0/chain/head). Fetch any historical bundle by URN at `/pcec/v0/claim/{urn}`.

## Why now

- **$2.7-2.9B US pet supplement market 2024-2025**, 5-7% CAGR, within a **$158B US pet industry** ([Packaged Facts](https://www.petfoodindustry.com/nutrition/pet-food-additives-supplements/news/15684592/us-pet-supplement-market-surpasses-27b-driven-by-health-and-wellness-trends), [APPA](https://www.petage.com/appa-report-pet-industry-consumer-spending/))
- **Less than 5% of brands** carry any third-party verification. NASC covers manufacturing/GMP, not clinical efficacy. That gap is the wedge ([NASC](https://www.nasc.cc/nasc-seal/))
- **[Cosequin $11.5M class-action settlement (2024)](https://topclassactions.com/lawsuit-settlements/open-lawsuit-settlements/11-5m-cosequin-dog-supplements-class-action-settlement/)** + VetriScience GlycoFlex pending + Morgan & Morgan multi-brand pet-food docket. Plaintiffs' bar is the live catalyst, not regulators.
- **[Google A2A protocol shipped 1.0 GA April 2026](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/)** and was donated to Linux Foundation. AI-shopping agents will need callable trust oracles; the protocol is shipping ahead of consumer adoption.

## Reproduce locally

See [`RUN.md`](RUN.md) for the 3-command quickstart against your own GCP project.

## Repo layout

```
agents/                  # 7-agent reasoning mesh (Python)
services/
  mesh_api/              # Cloud Run service exposing /a2a/v1, /pcec/v0, static pages
  shopper_agent/         # Reference A2A v0.3 consumer (separate Cloud Run service)
shared/                  # PCEC schema, task store, transparency log
corpus/                  # FTC §255 + AAFCO PF7 + NASC public-side passages (Vertex AI Search input)
deploy/                  # Reasoning Engine + Vertex AI Search + signing-key setup
tests/                   # pytest + ADK eval baseline
docs/                    # Architecture, PCEC v0.1 spec, devpost draft, video script
deck/                    # Investor deck (separate from GFS submission)
```

## License

MIT. OSI-approved per GFS hackathon submission rules (license file at repo root, detectable by standard scanners).

## Provenance

PawConscious Mesh ports the agentic infrastructure built across GUARDIAN v3-v9 (Falsifier, A2A peer scaffold) onto the PawConscious commercial wedge (vet rubric simulation, FTC substantiation mapping).
