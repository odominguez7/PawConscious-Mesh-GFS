# PawConscious Mesh — ACP for Pet

[![ADK eval baseline](https://img.shields.io/badge/ADK%20eval-baseline%20spec%20live-9C5E1A?style=flat-square&labelColor=1A1D1E)](tests/adk_eval/cases.json)
[![Live](https://img.shields.io/badge/live-mesh--api.run.app-13322B?style=flat-square&labelColor=1A1D1E)](https://mesh-api-40952019806.us-central1.run.app/)
[![Track 3](https://img.shields.io/badge/GFS%20Track%203-all%204%20mandates%20met-9C5E1A?style=flat-square&labelColor=1A1D1E)](https://mesh-api-40952019806.us-central1.run.app/architecture)
[![MIT](https://img.shields.io/badge/license-MIT-13322B?style=flat-square&labelColor=1A1D1E)](LICENSE)


**Start here:** [`START_HERE.md`](START_HERE.md) — the complete picture in one doc, written for the founder at 1am. Everything else is depth on a specific dimension.

---

**One-line summary:** A SaaS tool that turns a pet product URL into a signed, continuously-updated evidence bundle — citations, vet scores, FTC mapping, audit verdict — that the brand shows plaintiffs, retailers, regulators, consumers, and AI shopping agents. Built on Google ADK + Gemini 3 Pro + Vertex AI Agent Engine + A2A v0.3 + BioMCP + Cloud Run.

**Brand:** PawConscious Mesh. **Architecture/protocol:** ACP — Agentic Compliance Protocol. **Wedge:** US DTC pet supplements. **Scales to:** every consumer vertical AI shopping will mediate.

**For the GFS AI Agents Challenge 2026** — deadline June 5.

License: MIT. Hosted at `mesh-api-40952019806.us-central1.run.app` (post-build).

## What it is

Paste a product PDP URL. Five specialized ADK agents fan out in parallel via Vertex AI Agent Engine, each exposing an A2A v0.3 agent card:

| Agent | Tools | Job |
|---|---|---|
| `claim-extractor` | Firecrawl MCP + Gemini 3 Pro | Pull every health/efficacy claim from PDP copy |
| `evidence-grader` | BioMCP + AI2 Asta MCP + Gemini grounding | Search PubMed/Europe PMC/Semantic Scholar, grade citations by influence |
| `vet-panel` | Vertex AI Search + Gemini 3 Pro | Rubric scoring per claim against vet handbook corpus |
| `compliance` | Vertex AI Search (FTC §255 + NASC + AAFCO corpus) | Map every claim to regulator language |
| `auditor` (Falsifier) | ADK Eval + Gemini 2.5 Flash | Adversarial pass to catch hallucinated citations, cherry-picks |

Output (v0.1 shipped): signed certificate bundle (Ed25519, single trust root) + public Firestore transparency chain anchor + machine-readable PCEC v0.1 JSON-LD.

Roadmap (v0.2+, not present): embeddable badge JS, audit-grade PDF export, drafted expert outreach.

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
         ┌─────────────────────────┐
         │ Vertex AI Agent Engine  │
         │ orchestrator            │
         │ ParallelAgent fan-out   │
         └────────┬────────────────┘
                  │ A2A v0.3
   ┌──────┬──────┴─┬──────┬──────┐
   ▼      ▼        ▼      ▼      ▼
claim  evidence  vet   compli  audit
extr.  grader   panel  ance    Falsifier
   │      │        │      │      │
   ▼      ▼        ▼      ▼      ▼
         ┌─────────────────────────┐
         │ SequentialAgent merge   │
         │ + sign VC + anchor in   │
         │   transparency log      │
         └────────┬────────────────┘
                  ▼
                  ▼
       signed PCEC v0.1 bundle
       + chain anchor (Firestore)
       + agent-card discoverable via A2A
```

(Roadmap: badge JS · audit PDF · expert outreach — v0.2+, not shipped in this submission.)

## Tech stack

- **Orchestration:** Google ADK 2.0, Vertex AI Agent Engine
- **Models:** Gemini 3 Pro (reasoning), Gemini 2.5 Flash (routing + auditor)
- **Protocol:** A2A v0.3 (Linux Foundation, Apr 2026)
- **MCP servers:** BioMCP (biomedical), AI2 Asta (Semantic Scholar), Firecrawl (PDP scraping)
- **Search/grounding:** Vertex AI Search (vet + regulator corpora), Gemini Grounding with Google Search
- **Runtime:** Cloud Run (per-agent), Firestore (per-brand state), BigQuery (audit chain), Cloud SQL (cert registry)
- **Demo render:** screen-cap of live product + ElevenLabs founder VO (Veo/Lyria deferred per CEO plan 2026-05-19)

## Status

Active build. See `PLAN.md` for the 19-day roadmap and `docs/PCEC-v0.md` for the open spec stub.

## License

MIT (per GFS hackathon rules — OSI-approved license required, detectable at top of repo).

## Provenance

PawConscious Mesh ports the agentic infrastructure built across GUARDIAN v3-v9 (Falsifier, A2A peer scaffold) onto the PawConscious commercial wedge (vet rubric simulation, FTC substantiation mapping).
