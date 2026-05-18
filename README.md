# PawConscious Mesh

**The trust mesh for expert-claim commerce.** Multi-agent A2A network that turns a product URL into a regulator-grade substantiation bundle: signed verifiable credentials, citation-grounded evidence, vet-rubric verdict, falsifier-attested audit chain.

Built for the **Google for Startups AI Agents Challenge 2026** (deadline 2026-06-05). First vertical: US DTC pet supplements. Generalizes to any expert-claim e-commerce.

## What it is

Paste a product PDP URL. Five specialized ADK agents fan out in parallel via Vertex AI Agent Engine, each exposing an A2A v0.3 agent card:

| Agent | Tools | Job |
|---|---|---|
| `claim-extractor` | Firecrawl MCP + Gemini 3 Pro | Pull every health/efficacy claim from PDP copy |
| `evidence-grader` | BioMCP + AI2 Asta MCP + Gemini grounding | Search PubMed/Europe PMC/Semantic Scholar, grade citations by influence |
| `vet-panel` | Vertex AI Search + Gemini 3 Pro | Rubric scoring per claim against vet handbook corpus |
| `compliance` | Vertex AI Search (FTC §255 + NASC + AAFCO corpus) | Map every claim to regulator language |
| `auditor` (Falsifier) | ADK Eval + Gemini 2.5 Flash | Adversarial pass to catch hallucinated citations, cherry-picks |

Output: signed substantiation bundle (verifiable credential + C2PA-style manifest) + embeddable badge + audit-grade PDF + draft expert outreach.

Public A2A agent card at `/.well-known/agent-card.json` exposes three skills callable by any LLM agent:
- `verify_claim(sku, claim_text)`
- `fetch_substantiation_bundle(claim_id)`
- `attest_expert(expert_did)`

## Why now

- **$2.8B US pet supplement market 2025**, 5-7% CAGR, within a **$158B US pet industry**
- **Less than 5% of brands** carry any third-party verification (NASC covers manufacturing only; clinical substantiation is white space)
- **Cosequin $11.5M class-action settlement (2024)** + VetriScience GlycoFlex pending + Morgan & Morgan multi-brand pet-food docket → plaintiffs' bar is the live catalyst, not regulators
- **Google A2A protocol shipped 1.0 GA April 2026** and was donated to Linux Foundation. AI-shopping agents (Rufus, Perplexity Shopping, Gemini Shopping) need a callable trust oracle

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
   ┌──────────────┼──────────────┐
   ▼              ▼              ▼
 Badge JS     Audit PDF     Expert outreach
 (PDP embed)               (drafted, not sent)
```

## Tech stack

- **Orchestration:** Google ADK 2.0, Vertex AI Agent Engine
- **Models:** Gemini 3 Pro (reasoning), Gemini 2.5 Flash (routing + auditor)
- **Protocol:** A2A v0.3 (Linux Foundation, Apr 2026)
- **MCP servers:** BioMCP (biomedical), AI2 Asta (Semantic Scholar), Firecrawl (PDP scraping)
- **Search/grounding:** Vertex AI Search (vet + regulator corpora), Gemini Grounding with Google Search
- **Runtime:** Cloud Run (per-agent), Firestore (per-brand state), BigQuery (audit chain), Cloud SQL (cert registry)
- **Demo render:** Veo 3.1 Fast + Lyria 2 + ElevenLabs (via O22 pipeline)

## Status

Active build. See `PLAN.md` for the 19-day roadmap and `docs/PCEC-v0.md` for the open spec stub.

## License

MIT (per GFS hackathon rules — OSI-approved license required, detectable at top of repo).

## Provenance

PawConscious Mesh ports the agentic infrastructure built across GUARDIAN v3-v9 (Falsifier, A2A peer scaffold, Ops Center, Mission Bridge) onto the PawConscious commercial wedge (vet panel, FTC substantiation, embeddable badge). O22 pipeline produces the demo cinematic.
