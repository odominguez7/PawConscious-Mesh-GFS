# PawConscious

The check every AI shopping agent should run before recommending a consumer product.

> **Live:** [mesh-api-40952019806.us-central1.run.app](https://mesh-api-40952019806.us-central1.run.app) ·
> **Demo:** [/demo?judge=1](https://mesh-api-40952019806.us-central1.run.app/demo?judge=1) ·
> **Architecture:** [/architecture](https://mesh-api-40952019806.us-central1.run.app/architecture) ·
> **A2A card:** [/.well-known/agent-card.json](https://mesh-api-40952019806.us-central1.run.app/.well-known/agent-card.json) ·
> **Chain head:** [/pcec/v0/chain/head](https://mesh-api-40952019806.us-central1.run.app/pcec/v0/chain/head)

---

## What this is

Paste a product page URL. Seven agents on Google Cloud return a signed evidence bundle in about 90 seconds, up to a few minutes on a cold start. Grounded in PubMed via BioMCP. Cross-checked against FTC §255 and AAFCO via Vertex AI Search. Adversarially stress-tested with Google Search grounding. Signed with Ed25519 and anchored to a public Firestore transparency log.

The shopping agent gets a verdict it can act on. The brand gets a receipt it can show plaintiffs, retailers, and buyers. The verdict is independently verifiable offline.

## 30-second quickstart

Demo API key for judges: `demo-key-2026-06`.

```bash
curl -X POST "https://mesh-api-40952019806.us-central1.run.app/a2a/v1/tasks/send" \
  -H "X-API-Key: demo-key-2026-06" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {"role":"user","parts":[{"type":"text","text":"https://www.nativepet.com/products/hip-joint"}]},
    "skill": "verify_claim"
  }'
# → 202 { task_id, poll_url, head_anchor_at_submit }

# Then poll until status=completed (about 1 to 3 minutes):
curl "https://mesh-api-40952019806.us-central1.run.app/a2a/v1/tasks/get/<task_id>" \
  -H "X-API-Key: demo-key-2026-06"
```

Python and TypeScript snippets live at [/agents](https://mesh-api-40952019806.us-central1.run.app/agents).

## How it works

Three stages, seven agents.

**Stage 1 — reasoning mesh (5 agents).** A claim extractor runs first (ADK `LlmAgent` + Firecrawl). For every claim the orchestrator fans out three agents in parallel via `asyncio.gather`: evidence grader (BioMCP → PubMed + Semantic Scholar), vet rubric (Gemini 2.5 Pro grounded in published research), and compliance (Vertex AI Search over FTC §255 + AAFCO + NASC). An auditor agent then merges the evidence and runs an adversarial pre-sign pass.

**Stage 2 — sign.** The merged bundle is canonicalized, signed with Ed25519 against `did:web:<host>`, and appended to a public Firestore transparency log. The chain anchor is `sha256(bundle_hash + ":" + prev_chain_anchor)`. Anyone can verify the entire history offline.

**Stage 3 — adversarial (2 agents).** After signing, a cert composer renders the human-readable report and a Second Opinion agent runs four stress tests against the signed verdict (court, regulator, scientific consensus, public skepticism) using Google Search grounding via `google.genai`. Fails closed when the adversarial pass can't complete.

Full diagram at [/architecture](https://mesh-api-40952019806.us-central1.run.app/architecture).

## Track 3 mandate map

Google for Startups AI Agents Challenge · Track 3 (Refactor for Cloud Marketplace + Gemini Enterprise).

| Mandate | Code | Live proof |
|---|---|---|
| B2B focus | Subscription pricing for DTC brands · per-call pricing for AI shopping agents | [/#biz](https://mesh-api-40952019806.us-central1.run.app/#biz) |
| Cloud-native runtime | `services/mesh_api/` + `services/shopper_agent/` on independent Cloud Run services | [/health](https://mesh-api-40952019806.us-central1.run.app/health) |
| Gemini via Vertex AI | 6 agents on Gemini 2.5 Pro · 1 on Gemini 2.5 Flash | [`agents/orchestrator.py`](agents/orchestrator.py) |
| A2A interoperability | A2A v0.3 public agent card · JSON-RPC 2.0 envelopes · async tasks lifecycle | [/.well-known/agent-card.json](https://mesh-api-40952019806.us-central1.run.app/.well-known/agent-card.json) |
| Multi-agent collaboration | 7 agents · adversarial Second Opinion blocks errors a single Gemini call would ship | [/demo?judge=1](https://mesh-api-40952019806.us-central1.run.app/demo?judge=1) |
| Vertex AI Search grounding | Compliance agent over FTC §255 + AAFCO + NASC | [`agents/compliance.py`](agents/compliance.py) |
| Google Search grounding | Second Opinion runs 4 stress tests | [`agents/second_opinion.py`](agents/second_opinion.py) |
| Cryptographic agent identity | Ed25519 + did:web + Firestore transparency log | [/.well-known/did.json](https://mesh-api-40952019806.us-central1.run.app/.well-known/did.json) |
| Vertex AI Agent Engine | Orchestrator deployed as managed Reasoning Engine, routed in via feature flag | [/health/agent-engine](https://mesh-api-40952019806.us-central1.run.app/health/agent-engine) |
| Marketplace-ready discovery | Public A2A agent card · MIT-licensed open-source repo | [agent-card.json](https://mesh-api-40952019806.us-central1.run.app/.well-known/agent-card.json) |

## Run it locally

```bash
git clone https://github.com/odominguez7/PawConscious-Mesh-GFS.git
cd PawConscious-Mesh-GFS
python -m venv .venv && source .venv/bin/activate
pip install -e .
pytest tests/                          # 31 unit tests + ADK eval baseline
cd services/mesh_api && PORT=8088 python main.py
# → http://localhost:8088
```

## Open spec

[PCEC v0.1](docs/PCEC-v0.md) (Pet Claim Endorsement Certificate). MIT-licensed. Donation path to the Linux Foundation, same route Adobe used for C2PA.

The signed bundle shape is Pydantic JSON over A2A v0.3. JSON-LD evolution is on the v0.2 roadmap. Reference TypeScript and Python clients live in [`services/shopper_agent/`](services/shopper_agent/).

## Stack

Built on Google Cloud:

- **Intelligence:** Gemini 2.5 Pro · Gemini 2.5 Flash · Vertex AI
- **Orchestration:** Agent Development Kit (ADK 2.0) · `asyncio.gather` for the parallel fan-out · ADK `ParallelAgent` + `SequentialAgent` wrappers for the Phase 4 Vertex AI Agent Engine deployment surface
- **Runtime:** Cloud Run · Vertex AI Agent Engine (Reasoning Engine)
- **Grounding:** Vertex AI Search (FTC §255 + AAFCO + NASC corpora) · Google Search grounding via `google.genai`
- **Evidence retrieval:** BioMCP (Model Context Protocol server, MIT) · Semantic Scholar Graph API
- **Identity + integrity:** Ed25519 · did:web · Firestore (append-only transparency log)
- **Interop:** Linux Foundation A2A v0.3

Backend is Python 3.13 + FastAPI. Frontend is server-rendered HTML with vanilla JS for the demo cinematic.

## What this is not

- The vet rubric is a Gemini 2.5 Pro simulation, not licensed DVM attestation. Replaced by the `attest_expert` A2A skill in v0.2 (stipend-funded panel from accredited veterinary nutrition programs).
- The auditor is a deterministic Falsifier v0 (PMID-format check + claim-direction match). The Second Opinion adversarial pass catches what the auditor misses.
- No third-party shopping integrations are claimed. Amazon Rufus, Perplexity Shopping, Klarna agent, Gemini Shopping are the *use case*, not *current customers*. Any A2A v0.3-compatible client can call us today.
- PCEC v0.1 is the open spec. PCEC v0.2 with JSON-LD + co-signed bundles (NASC / NSF / accredited vet schools) is on the roadmap.

## License

MIT. See [LICENSE](LICENSE).

## Built solo for Google for Startups

Submission for the Google for Startups AI Agents Challenge · Track 3 (Refactor for Cloud Marketplace + Gemini Enterprise) · deadline 2026-06-05.

Omar Dominguez · MIT Sloan MBA 2026.
