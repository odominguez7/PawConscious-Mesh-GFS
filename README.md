# PawConscious Mesh — ACP for Pet

[![ADK eval baseline](https://img.shields.io/badge/ADK%20eval-baseline%20spec%20live-9C5E1A?style=flat-square&labelColor=1A1D1E)](tests/adk_eval/cases.json)
[![Live](https://img.shields.io/badge/live-mesh--api.run.app-13322B?style=flat-square&labelColor=1A1D1E)](https://mesh-api-40952019806.us-central1.run.app/)
[![Track 3](https://img.shields.io/badge/GFS%20Track%203-Gemini%20%2B%20Cloud%20Run%20%2B%20A2A%20%2B%20ADK%20scaffold-9C5E1A?style=flat-square&labelColor=1A1D1E)](https://mesh-api-40952019806.us-central1.run.app/architecture)
[![MIT](https://img.shields.io/badge/license-MIT-13322B?style=flat-square&labelColor=1A1D1E)](LICENSE)


**Start here:** [`START_HERE.md`](START_HERE.md) — the complete picture in one doc, written for the founder at 1am. Everything else is depth on a specific dimension.

---

**One-line summary:** A SaaS tool that turns a pet product URL into a signed, continuously-updated evidence bundle — citations, vet scores, FTC mapping, audit verdict, adversarial second opinion — that the brand shows plaintiffs, retailers, regulators, consumers, and AI shopping agents. Built on Google ADK (claim-extractor LlmAgent + FunctionTool scaffold, Phase 4 Agent Engine deployment surface) + google.genai (v0.1 runtime fan-out across all 7 agents) + Gemini 2.5 + A2A v0.3 + BioMCP + Semantic Scholar + Cloud Run.

**Brand:** PawConscious Mesh. **Architecture/protocol:** ACP — Agentic Compliance Protocol. **Wedge:** US DTC pet supplements. **Scales to:** every consumer vertical AI shopping will mediate.

**For the GFS AI Agents Challenge 2026** — deadline June 5.

License: MIT. Hosted at `mesh-api-40952019806.us-central1.run.app` (post-build).

## What it is

Paste a product PDP URL. Seven specialized agents run on Google Cloud across a three-stage pipeline. All seven currently execute via the `google.genai` SDK; `claim-extractor` is additionally scaffolded as an ADK `LlmAgent` + `FunctionTool` (`agents/claim_extractor.py::build_claim_extractor_agent`), documented as the Phase 4 Agent Engine deployment surface. Production orchestrator uses `asyncio.gather`; ADK `ParallelAgent` / `SequentialAgent` wrappers are documented as the v0.2 surface for the same reason.

| Agent | Runtime SDK | Model | Tools | Job |
|---|---|---|---|---|
| `claim-extractor` | google.genai (ADK LlmAgent scaffolded) | Gemini 2.5 Pro | httpx + BeautifulSoup primary, Firecrawl fallback | Pull every health/efficacy claim from PDP copy |
| `evidence-grader` | google.genai | Gemini 2.5 Pro | BioMCP (PubMed) + Semantic Scholar Graph API batch (citation influence) | Search PubMed/Europe PMC, grade citations + influential-citation counts |
| `vet-rubric` | google.genai | Gemini 2.5 Pro | Prompt-only 5-vet rubric **simulation** (LLM role-play; **no real DVMs in loop today**; `attest_expert` A2A skill replaces this with licensed-DVM attestation in v0.2) | Per-claim 1-5 rubric score + human-vet escalation flag |
| `compliance` | google.genai | Gemini 2.5 Pro | Vertex AI Search (FTC §255 + NASC + AAFCO corpus) | Map every claim to regulator language with snippet provenance |
| `auditor` (Falsifier) | google.genai | Gemini 2.5 Flash | PMID format + claim-direction check | Adversarial pass on the merged bundle |
| `report-writer` (Cert Composer) | google.genai | Gemini 2.5 Pro | Bundle composition | Compose the human-readable certificate from the already-signed bundle |
| `second-opinion` | google.genai | Gemini 2.5 Pro | Google Search grounding | Adversarial 4-stress-test pass (COURT · REGULATOR · CONSENSUS · PUBLIC SKEPTICISM) to try to break the conclusion |

Output (v0.1 shipped): signed certificate bundle (Ed25519, single trust root) + public Firestore transparency chain anchor + machine-readable PCEC v0.1 + adversarial second-opinion verdict.

Roadmap (v0.2+, not present): embeddable badge JS, audit-grade PDF export, real-existence citation verification via the live `citation_enricher` hook, ADK Agent Engine deployment from the existing Phase 4 scaffold.

A2A v0.3 agent card at `/.well-known/agent-card.json` exposes two skills (verify on the live card):
- `verify_claim` — paste a PDP URL, get the signed bundle + chain anchor
- `fetch_substantiation_bundle` — fetch a bundle by URN

Roadmap skill (v0.2+): `attest_expert`.

A2A endpoint is API-key-gated during the hackathon period for safety. Our `ShopperAgent` (source in this repo under `services/shopper-agent/`) is the demonstration consumer. Public open access ships post-hackathon once abuse controls are validated.

## Why now

- **$2.7-2.9B US pet supplement market 2024-2025**, 5-7% CAGR, within a **$158B US pet industry** ([Packaged Facts](https://www.petfoodindustry.com/nutrition/pet-food-additives-supplements/news/15684592/us-pet-supplement-market-surpasses-27b-driven-by-health-and-wellness-trends), [APPA](https://www.petage.com/appa-report-pet-industry-consumer-spending/))
- **Less than 5% of brands** carry any third-party verification. NASC covers manufacturing/GMP, not clinical efficacy — that gap is the wedge ([NASC](https://www.nasc.cc/nasc-seal/))
- **[Cosequin $11.5M class-action settlement (2024)](https://topclassactions.com/lawsuit-settlements/open-lawsuit-settlements/11-5m-cosequin-dog-supplements-class-action-settlement/)** + VetriScience GlycoFlex pending + Morgan & Morgan multi-brand pet-food docket → plaintiffs' bar is the live catalyst, not regulators
- **[Google A2A protocol shipped 1.0 GA April 2026](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/)** and was donated to Linux Foundation. AI-shopping agents will need callable trust oracles; the protocol is shipping ahead of consumer adoption

## Architecture

```
                       BRAND PRODUCT URL
                              │
                              ▼
              ┌──────────────────────────────┐
              │ Stage 1 — Orchestrator       │
              │ agents/orchestrator.py       │
              │ asyncio.gather fan-out       │
              └──────────────┬───────────────┘
                             │
                  ┌─ claim-extractor (sequential first) ─┐
                  ▼
       per-claim parallel ──► evidence-grader
                          ──► vet-panel
                          ──► compliance
                             │
                             ▼
                         auditor (post-merge)
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
              │ Stage 3 — A2A bg worker      │
              │ report-writer (HTML cert)    │
              │ second-opinion (Google       │
              │   Search grounded stress)    │
              └──────────────┬───────────────┘
                             ▼
            signed PCEC v0.1 bundle + chain anchor
            + cert HTML + adversarial verdict
            + agent-card discoverable via A2A v0.3
```

(Roadmap: badge JS · audit PDF · ADK Agent Engine deployment — v0.2+, not shipped in this submission.)

## Tech stack

- **Orchestration:** `asyncio.gather` for production parallelism; Google ADK `LlmAgent` + `FunctionTool` scaffolded in `agents/claim_extractor.py::build_claim_extractor_agent` as the Phase 4 Vertex AI Agent Engine deployment surface (v0.1 fan-out uses `google.genai` direct for deterministic latency)
- **Models:** Gemini 2.5 Pro (reasoning across six agents), Gemini 2.5 Flash (auditor)
- **Protocol:** A2A v0.3 (Linux Foundation, donated by Google April 2026)
- **MCP / open ecosystem:** BioMCP (PubMed + Europe PMC), Semantic Scholar Graph API batch (citation influence — public surface of AI2 Asta; MCP wrapper drops in later), Google Search grounding (second-opinion)
- **Search/grounding:** Vertex AI Search (compliance agent only, FTC §255 + NASC + AAFCO public corpus); Gemini grounding with Google Search (second-opinion stress tests)
- **Signing:** Ed25519 software signing in `services/mesh_api/main.py`; HSM-backed signing on the v0.2 roadmap
- **Runtime:** Cloud Run (per-agent), Firestore (transparency log + chain anchor), Cloud Build (CI)
- **Demo render:** screen-cap of live product + ElevenLabs founder VO (Veo/Lyria deferred per CEO plan 2026-05-19)

## Status

Active build. See `PLAN.md` for the 19-day roadmap and `docs/PCEC-v0.md` for the open spec stub.

## License

MIT (per GFS hackathon rules — OSI-approved license required, detectable at top of repo).

## Provenance

PawConscious Mesh ports the agentic infrastructure built across GUARDIAN v3-v9 (Falsifier, A2A peer scaffold) onto the PawConscious commercial wedge (vet rubric simulation, FTC substantiation mapping).
