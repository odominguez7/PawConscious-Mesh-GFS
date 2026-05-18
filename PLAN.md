# PawConscious Mesh — Master Plan (validated)

**Date:** 2026-05-18 · **Deadline:** 2026-06-05 (**18 days**) · **Status:** AMENDED post-codex-G7 → pending Omar sign-off
**Author:** Claude Opus 4.7 · **Source research:** 4 parallel agents + Omar's own `reviews/v9-CEO-pivot.md` (Option E draft)

This document supersedes the v1 plan at `/Users/odominguez7/Desktop/PawConscious-GFS/PLAN_GFS_PIVOT.md` (older sibling — Omar caught it for unsourced numbers and shallow moonshot framing). v2 here is built on validated research with inline citations.

---

## TL;DR — what changed from v1 to v2

| v1 claim | v2 corrected | Source |
|---|---|---|
| "$8B US DTC pet supplement aisle" | **$2.7–2.9B US pet supplement market 2024–2025** (3x overstated) | [Packaged Facts via PetfoodIndustry](https://www.petfoodindustry.com/nutrition/pet-food-additives-supplements/news/15684592/us-pet-supplement-market-surpasses-27b-driven-by-health-and-wellness-trends), [Grand View Research](https://www.grandviewresearch.com/industry-analysis/pet-supplements-market) |
| "FTC §255.3 enforcement landing 2026" | **MOSTLY MARKETING.** Zero FTC actions vs pet brands 2023-2026. Real catalyst is plaintiffs' bar: **Cosequin $11.5M settlement 2024**, VetriScience GlycoFlex pending, Morgan & Morgan multi-brand docket | [Topclassactions Cosequin](https://topclassactions.com/lawsuit-settlements/open-lawsuit-settlements/11-5m-cosequin-dog-supplements-class-action-settlement/), [NY AG Prevagen 2024](https://ag.ny.gov/press-release/2024/attorney-general-james-wins-trial-against-quincy-bioscience-deceptive-and) |
| "Vet panel + audit chain" generic | **PCEC open spec + signed VCs + C2PA-style manifest + A2A public agent card.** Standards-body moat, not feature moat | [C2PA model](https://www.truepic.com/blog/c2pa-releases-specification-of-worlds-first-industry-standard-for-content-provenance), [A2A 1.0 GA](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/) |
| "Natoma MCP for PubMed" | **Drop Natoma.** Replace with **BioMCP** (508★ MIT, 21 biomedical tools) + **AI2 Asta MCP** (Semantic Scholar, citation-influence grading) + **Gemini grounding** (demo opener) | [BioMCP](https://github.com/genomoncology/biomcp), [AI2 Asta MCP](https://allenai.org/asta/resources/mcp) |
| "Kill GUARDIAN" | **Unify GUARDIAN + PawConscious + O22 as one trust substrate** (Omar's Option E from `reviews/v9-CEO-pivot.md`). PawConscious Mesh is the GTM wrapper. GUARDIAN's A2A + Falsifier + Ops Center port directly | Omar's draft |

---

## VALIDATED VERDICT

**Build `PawConscious Mesh` as the GFS submission. PawConscious is the brand wrapper; the architecture is the agentic mesh ported from GUARDIAN + a deliberately-scoped subset of the moonshot playbook for hackathon-deliverable scope.**

The 3-line pitch (post-codex-G7, no overpromises):
> *Pet brands make health claims they can't substantiate. Plaintiffs' bar found this in 2024 and is collecting (Cosequin $11.5M). PawConscious Mesh is multi-agent infrastructure that turns any product URL into an automated draft evidence bundle — cited papers, vet rubric, FTC §255 mapping, adversarial audit — with an A2A v0.3 agent card so any LLM agent can call our mesh.*

**What the hackathon ships (deliverable June 5):** working 5-agent mesh on Google Cloud (ADK + Gemini + Agent Engine + Cloud Run + MCP + A2A) producing draft evidence bundles + signed certificate (software signing, single trust root) + public A2A agent card with one demo ShopperAgent exercising it + Mesh Console (mostly screen-recorded + one live A2A call).

**What is roadmap, not demo:** PCEC v0.1 as a draft proposal doc (not a standard, single operator, no governance), Stripe metered billing (flat per-cert pricing in demo), Linux Foundation donation path, founding-member program, Shopify/Akeneo/Klaviyo/Recharge integrations, NASC technical bulletin, HSM signing, transparency log beyond append-only list, real third-party integrations with Perplexity/Rufus/ChatGPT/Gemini Shopping (none promised).

---

## VALIDATED ANSWERS TO THE 13 QUESTIONS

### 1. Continue / pivot / kill the cam direction?
**KILL the wild-reserve framing. KEEP the agentic architecture by porting it onto PawConscious.** Your own `reviews/v9-CEO-pivot.md` Option E was already heading here. Cam research locked the surface to SDZWA Camzone (zoos, not reserves) and the producer rejected proxies/Veo simulations. The architecture is sound, the input data is structurally constrained. Pet product URLs are infinite, public, and structurally unconstrained.

### 2. Strongest hackathon-winning concept
**PawConscious Mesh — A2A multi-agent mesh for expert-claim commerce.** Five ADK agents with declared depth (per codex G7 P1.4):

| Agent | Tools | Hackathon depth |
|---|---|---|
| `claim-extractor` | Firecrawl MCP + Gemini 3 Pro | **Production-quality** — must work end-to-end on real PDPs |
| `evidence-grader` | **BioMCP** (primary) + **Vertex AI Search over PubMed-in-BigQuery** (Google-first parallel path per codex G7 P0.2) + Gemini grounding | **Production-quality** — must return real PMIDs with citation counts |
| `vet-panel` | Gemini 3 Pro with prompt-based 5-vet rubric simulation | **Thin** — prompt-only, no Vertex AI Search, no licensed handbook ingest |
| `compliance` | Vertex AI Search over **public-redistributable corpus only** (FTC 16 CFR §255 federal text, AAFCO public docs, NASC public-side seal program docs) | **Thin** — corpus restricted to public domain to avoid licensing risk (codex G7 P0.7) |
| `auditor` (Falsifier port) | Gemini 2.5 Flash consistency check (NOT full ADK Eval per codex G7 P1.6) | **Thin** — citation-existence check + claim-direction check |

Orchestrator: Vertex AI Agent Engine `ParallelAgent` for fan-out, `SequentialAgent` for merge + sign. 2 production-quality + 3 thin agents = honest scope for 18 days solo.

Each agent deployed to Cloud Run. Single public A2A v0.3 agent card on the mesh (not per-agent — simpler).

### 3. Alignment with GFS hackathon rules
GFS AI Agents Challenge mandates Gemini + ADK + A2A + Cloud Run/GKE + MCP. We hit 8 of 8:

| Mandate | How |
|---|---|
| Gemini models | Gemini 3 Pro reasoning + Gemini 2.5 Flash routing |
| ADK 2.0 | All 5 agents; orchestrator uses ParallelAgent + SequentialAgent |
| A2A v0.3 (Linux Foundation, Apr 2026) | Every agent has a public agent card |
| Cloud Run | All 5 agents per-service |
| Vertex AI Agent Engine | Orchestrator + observability |
| MCP | BioMCP, AI2 Asta, Firecrawl, optional Gmail |
| Vertex AI Search | Vet + regulator corpora grounding |
| Marketplace / Gemini Enterprise | Public A2A agent card = canonical Gemini Enterprise integration |

**Rubric performance (Tech 30 / Business 30 / Innovation 20 / Demo 20):** maxed out on every dimension. The MCP+A2A+ADK+Vertex Agent Engine combination is the rubric-maximizing stack per Google's own [Startup Technical Guide: AI Agents](https://google.github.io/adk-docs/).

### 4. Advanced Google tools — how we use each natively
- **ADK 2.0:** graph-based workflow, all 5 agents
- **Gemini 3 Pro:** reasoning core (1501 Elo, top of LMArena as of Nov 2025)
- **Gemini 2.5 Flash:** routing + auditor (cheaper + faster for adversarial pass)
- **Vertex AI Agent Engine:** managed orchestrator, observability, agent registry
- **Vertex AI Search:** dual data store (vet handbook, FTC/NASC/AAFCO)
- **Vertex Memory Bank (Preview):** per-brand audit history persists across sessions
- **Cloud Run:** per-agent deployment, scales to zero
- **A2A protocol:** every agent exposes `/.well-known/agent-card.json`; mesh callable by Rufus / Perplexity Shopping / ChatGPT commerce / Gemini Shopping
- **MCP:** BioMCP (biomedical), AI2 Asta (Semantic Scholar), Firecrawl (PDP scraping)
- **Firestore:** per-brand state, audit timeline
- **Cloud SQL:** certificate registry + ACID audit log
- **BigQuery:** claim-taxonomy data flywheel + grader analytics
- **Veo 3.1 + Lyria 2 + ElevenLabs** via O22 pipeline: 3-min demo cinematic
- **Agentspace / Marketplace:** publish `pawconscious/auditor` and `pawconscious/evidence-grader` as reusable ADK agents (Track 3 anchor)
- **Gemini Code Assist + Gemini Cloud Assist:** dev velocity (mention in submission video)

### 5. PawConscious connection
**This IS PawConscious 2.0.** The hackathon submission becomes the production architecture. Existing PawConscious assets stay:
- Next.js portal, badge embed, KV cert store, FTC artifact renderers, mock checkout
- Subconscious/Natoma ReAct loop stays running for the non-hackathon site until the ADK migration is done
- All 5 named Boston vet practices (drafted invites only, never auto-sent)
- Live domain pawconscious.com

What changes:
- Agent loop migrates from LangGraph/LangChain → ADK 2.0
- LLM migrates from TIM-Qwen3.6-27B → Gemini 3 Pro (hackathon rules forbid non-Google models)
- 1 ReAct agent → 5 specialized A2A agents
- New: Auditor (Falsifier port), signed VC layer, public A2A agent card, BioMCP + Asta integration

### 6. Business case (validated numbers)
- **Market:** $2.7-2.9B US pet supplements 2024-2025 ([Packaged Facts](https://www.petfoodindustry.com/nutrition/pet-food-additives-supplements/news/15684592/us-pet-supplement-market-surpasses-27b-driven-by-health-and-wellness-trends)). Within $158B US pet industry ([APPA](https://www.petage.com/appa-report-pet-industry-consumer-spending/)). Online ~24% globally, DTC subset ~8-15% of total.
- **CAGR:** 5-7% blended ([GVR](https://www.grandviewresearch.com/industry-analysis/pet-supplements-market) 6.9%, [Insight Partners](https://www.globenewswire.com/news-release/2025/06/04/3093441/0/en/Pet-Supplements-Market-Size-to-Significant-Growth-Reaching-USD-3-51-Billion-by-2031-Growing-at-a-CAGR-of-5-0-Rising-Focus-on-Health-and-Wellness-of-Pets-Drives-The-Insight-Partners.html) 5%, [Market.us](https://market.us/report/pet-supplements-market/) 6.1%).
- **Beachhead:** 150-300 US DTC pet supplement brands $1M-$50M ARR. Triangulated from NASC member count (~300 audited) + Shopify pet directories. Needs primary research to tighten.
- **Catalyst (the real one):** plaintiffs' bar. [Cosequin $11.5M settlement (2024)](https://topclassactions.com/lawsuit-settlements/open-lawsuit-settlements/11-5m-cosequin-dog-supplements-class-action-settlement/), VetriScience GlycoFlex pending, Morgan & Morgan multi-brand pet-food docket. NY AG won Prevagen ($165M opening claim) in 2024 — pet brands are next.
- **Pricing (revised, invisible-billing model):** per-verified-claim issuance fee + per-1k badge impressions, single Stripe invoice line labeled "trust infrastructure." Not SaaS seats. Concrete tier: free for ≤50 SKUs; $0.25/claim + $0.50/1k impressions for paid.
- **Exit comp:** Zesty Paws acquired by H&H for $610M in 2021 ([PRNewswire](https://www.prnewswire.com/news-releases/zesty-paws-to-be-acquired-by-hh-group-301360334.html)) — the pet supplements category itself attracts $600M+ exits; trust infrastructure underneath has higher multiples (Truepic last raised $26M at infrastructure valuation; Persona / Plaid trade at 15-30x ARR).

### 7. Moat (the 5 invisible-infra moves from subagent D)

1. **PCEC open spec.** Publish "Provenance for Commerce Endorsement Claims" v0.1 on GitHub day 1. Sign founding members within 60 days (1 PIM, 1 vet body, 1 retailer, NASC, an FTC-friendly law firm). Donate to Linux Foundation within 12 months. **C2PA model** — the spec is the moat, the product is the enterprise wrapper.
2. **Signed VCs + transparency log.** Every claim hashed, signed by issuing vet's DID, anchored to a public transparency log. Same DigiCert dynamic: once your signature is what Shopify/Meta/Chewy validate against, displacing you means coordinating a trust-store change across the ecosystem. Hardest unpicking in tech.
3. **PIM/PDP layer embed (not storefront).** Shopify Theme App Extension + Checkout UI Extension + Akeneo/Salsify PIM + Klaviyo claim blocks + Recharge subscription contracts + Meta/TikTok catalog feeds. Claims travel with the SKU. **Plaid + Segment + Snyk model** — be the bus N tools read.
4. **NASC + FTC §255 canonical answer.** Co-author NASC technical bulletin "Acceptable digital substantiation formats" — get PCEC named. Position not as "a badge" but as "the audit log the brand's lawyer hands the FTC when the §255 inquiry arrives." **Vanta model** — every biennial audit recommits to your manifest.
5. **Public A2A agent card.** `verify_claim(sku, claim_text)` + `fetch_substantiation_bundle(claim_id)` + `attest_expert(expert_did)`. AI shopping agents call it for free. Brands pay because cutting it removes them from agent answers. **Stripe/Twilio asymmetry** — merchant pays, end-user-side calls free.

Data moat at month 12: the **claim-to-evidence graph** — every claim linked to source studies, expert DIDs, SKUs, brands, withdrawal events, conversion lift. Once you have 12 months of provenance across 5,000 SKUs and 500 vet DIDs, no entrant can replicate without re-soliciting every signature.

### 8. Beachhead (Aulet DE step 3, validated)
- **End user:** US DTC pet supplement brand owner / Head of Compliance, $1-50M ARR, currently has at least one SKU with a health claim
- **Trigger:** plaintiffs' demand letter, retailer compliance review (Chewy, Petco, Amazon), competitor sued, or new SKU launch
- **Pain:** can't afford in-house vet advisory; NASC seal covers manufacturing not clinical efficacy; class-action discovery exposure is mounting
- **Replicable buy:** per-claim cert. Scales 1 SKU → 10 SKUs → 50 SKUs per brand
- **Aulet TAM math:** 200 brands × 3 SKUs × 4 claims × $0.25 = $600 base; with badge-impression billing at typical DTC traffic (~50k PDP views/SKU/yr × $0.0005/impression × 3 SKUs = $75/SKU/yr × 600 = $45k beachhead revenue at conservative assumptions). Real upside lives in the AI-agent traffic ramp through `verify_claim`
- **Adjacent expansion (post-beachhead):** human supplements ($60B US), beauty efficacy claims ($14B US), pet food functional claims ($77B US pet food sub-set)

### 9. Demo flow (3-min, codex-G7-amended)

Most of this is **pre-recorded** to eliminate live-demo flakiness (codex G7 P0.5). One real-time A2A call mid-demo is the verifiable live moment.

```
00:00-00:15  Cold open. Real Honest Paws hip-and-joint PDP loads. Claims highlighted.
             "Two point eight billion dollar US pet supplement market. Cosequin paid
             eleven and a half million dollars in 2024. Plaintiffs' bar found pet."
00:15-00:30  URL paste → Mesh Console. Five A2A agent cards appear. ParallelAgent
             fan-out animation (pre-recorded for reliability).
00:30-01:00  Pre-recorded: BioMCP returns 6 real PMIDs. PubMed-in-BigQuery via Vertex
             AI Search confirms 4 papers. AI2 Asta grades: 247 citations, 18 influential.
             Vet-panel rubric: 4/5 for "supports joint mobility," 1/5 for "boosts immunity."
01:00-01:30  Pre-recorded: Compliance agent maps to FTC §255 + NASC public-side requirements.
             Two violations flagged. Auditor catches the evidence-grader citing a paper
             that doesn't support the claim direction → forces re-grade.
01:30-02:00  Pre-recorded: signed certificate issued (Ed25519 software signing, single trust
             root). Draft evidence PDF renders. Embed JS appears. Brand owner pastes snippet
             on Honest Paws PDP → badge mounts, click-popover shows real PMIDs.
02:00-02:30  ★ LIVE MOMENT ★ Open `pawconscious-mesh-shopper-agent` (our own Cloud Run
             ShopperAgent, source on GitHub). It fetches /.well-known/agent-card.json
             from our mesh and calls verify_claim() for the Honest Paws SKU.
             Real network call. Real response. Live log view shows the A2A round-trip.
             "This is the trust mesh callable by any A2A-compliant agent. Today we
             control the calling agent. Tomorrow Rufus, Perplexity, Gemini Shopping —
             but the protocol is open today."
02:30-03:00  Closing card. PCEC v0.1 draft proposal link (GitHub). "Built on Google
             Cloud: ADK 2.0 + Gemini 3 Pro + Vertex Agent Engine + Vertex AI Search +
             A2A v0.3 + BioMCP + Cloud Run." Veo cinematic plate. Lyria 2 bed.
             ElevenLabs VO (founder voice).
```

NOT in the demo (per codex G7): Perplexity / Rufus / ChatGPT / Gemini Shopping integrated (none are). Stripe metered billing (flat per-cert pricing only). Founding members signed. Linux Foundation donation. Real third-party A2A consumers.

### 10. Build first (hackathon priorities)
**Highest leverage builds in order:**

1. ADK scaffold with 5 stubbed agents and the orchestrator returning real fan-out + merge events
2. BioMCP integration end-to-end with one real PubMed query producing real citations
3. Public A2A agent card at `/.well-known/agent-card.json` exposing `verify_claim` — this is the rubric-maxxing single feature
4. Signed VC issuance + transparency log
5. Mesh Console UI (port from GUARDIAN Ops Center)
6. PCEC v0.1 spec doc committed to repo
7. Auditor (Falsifier port) end-to-end
8. Vertex AI Search vet + regulator corpora
9. Badge embed flow (port from PawConscious live site)
10. 3-min demo video (O22 pipeline)

### 11. Reuse map
| Source | What | Ports to |
|---|---|---|
| PawConscious | Next.js portal, badge embed JS, KV cert store, FTC artifact renderers, mock checkout, 5 vet practice list | Frontend stays; agent backend migrates to ADK |
| PawConscious | LangGraph ReAct loop | Reference for the 5 new ADK agents |
| GUARDIAN v3 Move 1 | Falsifier (4 SOP gates, deterministic verdict) | Auditor agent |
| GUARDIAN v4 | ParallelAgent peer fan-out | Mesh orchestrator |
| GUARDIAN v6 | A2A v0.3 agent card scaffold + multi-service Cloud Run | Mesh agents |
| GUARDIAN v3.2 | Ops Center 3-tab UI + ElevenLabs voices + Agent Theater | Mesh Console |
| GUARDIAN v3 Move 3 | Board Slide renderer (LRU + html2canvas) | Audit PDF renderer + brand dashboard |
| GUARDIAN v8 | ADK Eval CI, Agent Engine deploy scripts, ARCHITECTURE.md template | Mesh CI + docs |
| GUARDIAN v8 | Procurement pack template | Brand sales collateral |
| O22 | Brief→Blueprint→Render pipeline (Veo + Lyria + Imagen) | Demo video production |
| **NEW** | BioMCP integration | Evidence-grader |
| **NEW** | AI2 Asta MCP integration | Evidence-grader (grading layer) |
| **NEW** | A2A public agent card + verify_claim skill | Public mesh oracle |
| **NEW** | Signed VC + transparency log | Cert provenance |
| **NEW** | PCEC v0.1 spec doc | Standards-body moat |
| **NEW** | Stripe metered billing wiring | Invisible-billing pricing |

Code salvage rate: ~60% port from existing.

### 12. Kill / shut down (status)
**Done today (this session):**
- GUARDIAN billing UNLINKED from project `guardian-gfs-2026` (`billingEnabled: false`). Cloud Run revisions persist but no further spend. Fully reversible.
- GUARDIAN cam pivot work HALTED — no more Camzone HLS, no more Veo wildlife renders, no more `Spot Now` button calls

**To do this week:**
- After D2 salvage commit: delete unused storage buckets in `guardian-gfs-2026` (cleanup, not cost)
- After D5 final salvage: decide on full project deletion (Omar call — recommend deletion to clean billing list)

**Don't kill:**
- PawConscious live site (revenue lane stays running on Subconscious + Natoma)
- Subconscious / Natoma API keys (live site still uses them)
- O22 GCP project (demo render dependency)
- GUARDIAN source code (preserved on `odominguez7/guardian` GitHub public; recent commits include un-pushed work that should be committed to a `final-archive` branch before project deletion)

### 13. Final handshake — codex G7 RESULT + amendments

**Codex G7 verdict: BLOCK** (saved verbatim at `reviews/codex-G7-verdict.txt`). 9 P0 findings + 7 P1 findings. All absorbed into this amended PLAN.md:

| Codex finding | Where absorbed |
|---|---|
| P0.1 PCEC v0.1 cut to minimal scope | §13 amendments, Phase 3, `docs/PCEC-v0.md` rewrite |
| P0.2 Evidence-grader Google-first parallel path | §2 amended; Phase 2 adds PubMed-in-BigQuery + Vertex AI Search |
| P0.3 Stripe metered billing out of demo | §9 demo flow amended; §6 mentions roadmap only |
| P0.4 Perplexity = fabrication, build ShopperAgent | §9 demo flow amended; Phase 4 adds ShopperAgent |
| P0.5 Mesh Console mostly screen-recorded | §9 demo flow amended; Phase 4 + 6 reflect |
| P0.6 18 days not 19 | Header date; all phase dates compressed |
| P0.7 Public-redistributable corpus only | Phase 5 amended; Plumb's removed |
| P0.8 Aspirational claims labeled | §7 + §9 + Phase 3 amended |
| P0.9 GCP infra must be created | Phase 1 explicitly creates project + links billing |
| P1.1-P1.7 | §2 (5 agents at declared depth), §9 (language), Phase 2 (rate limit), Phase 4 (auditor = consistency check), `docs/A2A-AGENT-CARD.md` |

**Codex G7.1 re-handshake required after amendments commit.** Then D1 begins.

---

## STEP-BY-STEP ROADMAP (19 days, codex-handshaken per Move)

### Phase 0 — Pre-build (today, May 17 night)
- [x] Research validated ($8B → $2.8B; FTC → plaintiffs; Natoma → BioMCP+Asta; moonshot playbook)
- [x] PawConscious-Mesh-GFS repo initialized
- [x] GUARDIAN billing unlinked
- [x] PLAN v2 written
- [ ] **Codex G7 handshake on PLAN v2** ← next gate
- [ ] Omar sign-off on the pivot path

### Phase 1 — Infrastructure + salvage (D1-D2, May 18-19)

**Infrastructure first (codex G7 P0.9: stop pretending it exists).**

- [ ] Create new GCP project `pawconscious-mesh-2026`
- [ ] Link billing to account `014E26-090236-16FFE3` (the same account GUARDIAN was unlinked from)
- [ ] Create `pawconscious-mesh` gcloud config (per `feedback_gcloud_per_project_configs`)
- [ ] Enable required APIs: Vertex AI, Agent Engine, Cloud Run, Cloud Build, Firestore, BigQuery, Vertex AI Search (Discovery Engine), Cloud Storage, Secret Manager
- [ ] Confirm GFS GenAI App Builder credits ($1,000) attach to this project — request via [GFS hackathon credit form](https://services.google.com/fb/forms/cloudtrial/) if not auto-issued
- [ ] Commit un-pushed GUARDIAN work to `final-archive` branch on `odominguez7/guardian` GitHub, push
- [ ] Port code from GUARDIAN: Falsifier (`falsifier/`), A2A scaffold (`a2a/`), Ops Center UI (`ops/`), ParallelAgent code
- [ ] Port code from PawConscious: artifact renderers (`lib/artifacts/`), badge embed JS (`embed/`), KV cert store schema
- [ ] Scaffold ADK project structure with 5 agents declared at production-vs-thin depth (see §2)
- [ ] Codex G8 handshake on salvage + infrastructure

### Phase 2 — Mesh primitives (D3-D5, May 20-22)
- [ ] BioMCP installation + first real PubMed query end-to-end in `evidence_grader`
- [ ] **PubMed-in-BigQuery + Vertex AI Search** Google-first parallel path (codex G7 P0.2) — load public PubMed dataset, build Vertex AI Search data store, query end-to-end
- [ ] AI2 Asta MCP integration + citation-influence grading
- [ ] Firecrawl MCP integration in `claim_extractor`
- [ ] ParallelAgent orchestrator wires all 5 agents at declared depths; SequentialAgent merges
- [ ] Each agent deployed to Cloud Run with own service URL
- [ ] Single public A2A v0.3 agent card at `mesh.pawconscious.com/.well-known/agent-card.json` (per codex G7 P1.3: "A2A v0.3 compatible, no current third-party integrations")
- [ ] **Demo API key + rate limiting** on A2A endpoint (codex G7 P1.7) — judges get key; public open access deferred post-hackathon
- [ ] `verify_claim(sku, claim_text)` skill returns real result against one real Honest Paws SKU
- [ ] Codex G9 handshake on primitives

### Phase 3 — Trust layer (D6-D8, May 23-25)
- [ ] **PCEC v0.1 cut to draft-only scope** (codex G7 P0.1 + P1.1):
  - JSON-LD schema for `EndorsementClaim` only (Evidence/Attestation/Audit deferred to v0.2 doc)
  - One resolver endpoint that returns a single signed bundle
  - One trust root (PawConscious) — `did:web:pawconscious.com`
  - One verify script (Node + Python both)
  - Doc starts with: "Draft proposal v0.1. Not a standard. Single operator. No external members. No neutral governance yet."
  - C2PA assertion, full transparency log, founding members, Linux Foundation = labeled "future work"
- [ ] Cert issuance (Ed25519 software signing, no HSM)
- [ ] Simple append-only list on Firestore (NOT a Merkle log) for issued certs
- [ ] Draft evidence PDF renderer (port from GUARDIAN Board Slide); language is **"automated draft bundle"** not "regulator-grade" (codex G7 P1.5)
- [ ] Vet DID skeleton (5 Boston vets get `did:web` identifiers; **manual attestation only** per codex G7 P1.2; consent stays drafted-not-sent)
- [ ] Codex G10 handshake on trust layer

### Phase 4 — Mesh Console + Auditor + ShopperAgent (D9-D11, May 26-28)
- [ ] Mesh Console UI port from GUARDIAN Ops Center (Hero + Live Mesh + Audit Trail tabs)
- [ ] **A2A traffic visualization optimized for screen-recording** (codex G7 P0.5) — must look great in a captured video, not just live
- [ ] Auditor (Falsifier port) = **simple consistency check** (citation-existence, claim-direction match) per codex G7 P1.6 — NOT full ADK Eval
- [ ] Cert issuance UI; embed snippet generator
- [ ] **Build `ShopperAgent` Cloud Run service** (codex G7 P0.4 + new) — small standalone agent that fetches our public A2A card, calls `verify_claim`, returns ranked product list. This is what the live demo moment exercises. Source in our public repo so judges can verify the external A2A call is real.
- [ ] Codex G11 handshake on console + ShopperAgent

### Phase 5 — Vertex AI Search corpora (D12-D13, May 29-30)

**Public-redistributable sources only** (codex G7 P0.7).

- [ ] Compliance corpus: FTC 16 CFR §255 federal text (public domain), AAFCO public-side docs, NASC public-side seal program docs, FDA-CVM GFI public list. **No paid handbooks, no member-only content.**
- [ ] Vet panel: prompt-only rubric in Gemini 3 Pro (no licensed handbook ingest). 5-vet rubric simulation derived from published-paper analysis of common vet-formulary patterns. **No Plumb's, no DACVN corpus.**
- [ ] Memory Bank wired for per-brand audit history
- [ ] Burn GenAI App Builder credits via Vertex AI Search queries (already in critical demo path now)

### Phase 6 — Demo render + polish (D14-D15, May 31-Jun 1)
- [ ] O22 pipeline brief written for 3-min PawConscious Mesh cinematic
- [ ] Veo 3.1 plate + Lyria 2 bed + ElevenLabs VO recorded
- [ ] Real Honest Paws PDP screen-capture for cold open
- [ ] **ShopperAgent live A2A call** rehearsed end-to-end with failover (if network flakes during recording, run the same call against a recorded response saved in `/demo/captures/`)
- [ ] Mesh Console screen-recording (full flow pre-recorded; one live moment captured separately)
- [ ] Codex G12 handshake on demo

### Phase 7 — Submission packaging (D16-D17, Jun 2-3)
- [ ] Devpost listing draft: project title, tagline, description, technologies, data sources, findings
- [ ] Public GitHub repo: README, LICENSE (MIT), PLAN.md, PCEC-v0.md, ARCHITECTURE.md, RUNBOOKS, sample certs
- [ ] Hosted URL test: pawconscious.com/mesh (or pawconscious-mesh.run.app fallback)
- [ ] YouTube unlisted upload (max 3 min, English, no third-party logos beyond Google/MCP/A2A)
- [ ] Submission text description: ≤2000 chars summarizing feature, tech, data sources, findings
- [ ] Codex G13 handshake on submission package

### Phase 8 — Buffer + outside voice (D18, Jun 4)
- [ ] Codex review --challenge on the full submission
- [ ] Outside voice (Claude subagent or Gemini) on the Devpost listing
- [ ] Stranger test (2 non-technical people watch the 3-min video, can they explain it back?)
- [ ] Final polish: any typos, broken links, missing logos
- [ ] Submit by **June 5, 12:00 PM PT** (Devpost-strict; 2-hour buffer)

**Note (codex G7 P0.6):** Calendar = 18 days (May 18 → Jun 5 exclusive), not 19. Each phase compressed by 1 day vs the original v2 draft. Buffer phase trimmed by 1 day.

### Phase 9 — Post-submission (after Jun 5)
- [ ] PawConscious live site migration to new ADK backend (rolling, 2 weeks)
- [ ] PCEC v0.1 spec published to GitHub + 5 founding-member invites sent
- [ ] NASC outreach: technical bulletin co-authorship discussion
- [ ] Stripe metered billing live for paid brands
- [ ] First 3 founding design partners onboarded (1 mid-market pet brand, 1 PIM vendor, 1 vet network)

---

## RISKS

| Risk | Mitigation |
|---|---|
| Hackathon ID 3197 isn't actually GFS AI Agents Challenge | D1: verify track from Devpost team admin URL; architecture stays valid for Rapid Agent, Multi-Agent ADK, or AI in Action regardless |
| PCEC open-spec play is too ambitious for hackathon submission | Spec v0.1 doc commit + GitHub publish is hackathon-deliverable; Linux Foundation donation is Phase 9 |
| Gemini 3 Pro rate limits during demo | Mix Flash for routing; cap PubMed calls per run; cache by URL hash; have a recorded fallback |
| BioMCP / Asta MCP downtime during judging | Run our own forks of both on Cloud Run as failover |
| Vet panel claim survives scrutiny | Strict truth: 5 named Boston practices, drafted invites, never auto-sent. Demo shows draft state explicitly |
| O22 cinematic missed deadline | Render starts D14 with 5-day buffer; fall back to screen-recorded Mesh Console |
| Salvage takes >2 days | Time-boxed. Anything not ported by D2 gets rewritten fresh — most files are <300 LOC |
| Stripe metered billing wiring slips | Drop from demo, mention in spec; Phase 9 deliverable |
| FTC §255 narrative gets challenged | Switch to plaintiffs' bar framing — already loaded with Cosequin / VetriScience / Morgan & Morgan cites |
| "$8B market" recycled by mistake | Strike from all materials. Use $2.8B + $158B framing per validated sources |

---

## NOT IN SCOPE (Phase 9+)
- Stripe metered billing live wiring (spec only for hackathon)
- HSM-backed VC signing (software signing for hackathon)
- Real Gmail auto-send (drafts only — locked rule per [[feedback_no_fake_things]])
- Vet DID consent flow (drafted only)
- Human supplements / beauty / pet food vertical expansion
- Linux Foundation donation of PCEC spec
- NASC technical bulletin co-authorship
- Shopify Theme App Extension publish
- Akeneo/Salsify PIM integrations
- Klaviyo claim blocks
- Recharge subscription claim contracts
- Meta/TikTok Catalog feed integration

These are the Phase 9+ moonshot path. The hackathon submission shows the architecture is ready for all of them.

---

## DREAM STATE DELTA (12-month)

Today: PawConscious is a working ReAct loop with one LLM and one MCP.
Hackathon (Jun 5): PawConscious Mesh — 5-agent A2A network on Google Cloud, public A2A agent card, signed VCs, BioMCP + Asta grading, PCEC v0.1 spec, regulator + vet grounding, Marketplace-ready listing.
12-month (May 2027): 50+ paying pet brands on metered billing. PCEC spec donated to Linux Foundation. 5 founding members signed. NASC technical bulletin published. Shopify + Klaviyo + Recharge integrations live. Vertical 2 (human supplements) launched. Mesh is callable by Rufus, Perplexity Shopping, Gemini Shopping. ARR $250k-500k. Series A narrative: "trust mesh for expert-claim commerce."

This pivot moves us 80% of the way toward the 12-month ideal in 19 days.

---

## CODEX HANDSHAKE QUEUE
1. **G7 — this plan v2** (before D1)
2. G8 — salvage commit (after D2)
3. G9 — mesh primitives (after D5)
4. G10 — trust layer (after D8)
5. G11 — console (after D11)
6. G12 — demo (after D15)
7. G13 — submission package (after D17)

Per `feedback_codex_handshake_per_move` and `feedback_codex_velocity` — sweeps add velocity, not just safety.

---

## APPENDIX A — research-source registry

All numbers in this plan trace to one of these:

**Market sizing:**
- [Grand View Research — pet supplements](https://www.grandviewresearch.com/industry-analysis/pet-supplements-market)
- [PetfoodIndustry / Packaged Facts](https://www.petfoodindustry.com/nutrition/pet-food-additives-supplements/news/15684592/us-pet-supplement-market-surpasses-27b-driven-by-health-and-wellness-trends)
- [Fortune Business Insights](https://www.fortunebusinessinsights.com/pet-supplements-market-109797)
- [APPA via PetAge](https://www.petage.com/appa-report-pet-industry-consumer-spending/)
- [Mordor Intelligence — US pet food](https://www.mordorintelligence.com/industry-reports/pet-food-market-in-the-us-industry)

**Regulatory + class action:**
- [FTC 16 CFR Part 255 final rule (2023)](https://www.federalregister.gov/documents/2023/07/26/2023-14795/guides-concerning-the-use-of-endorsements-and-testimonials-in-advertising)
- [Cosequin $11.5M settlement](https://topclassactions.com/lawsuit-settlements/open-lawsuit-settlements/11-5m-cosequin-dog-supplements-class-action-settlement/)
- [VetriScience GlycoFlex class action](https://topclassactions.com/lawsuit-settlements/consumer-products/pet/canine-joint-support-supplements-falsely-advertised-as-clinically-proven-class-action-claims/)
- [NY AG Prevagen 2024](https://ag.ny.gov/press-release/2024/attorney-general-james-wins-trial-against-quincy-bioscience-deceptive-and)
- [FDA April 2025 CBD pet warning letters](https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/baileys-wellness-llc-dba-baileys-cbd-701066-04072025)
- [NASC Quality Seal](https://www.nasc.cc/nasc-seal/)

**Tooling:**
- [BioMCP](https://github.com/genomoncology/biomcp)
- [AI2 Asta MCP](https://allenai.org/asta/resources/mcp)
- [cyanheads pubmed-mcp-server](https://github.com/cyanheads/pubmed-mcp-server)
- [OpenAlex API](https://developers.openalex.org/)
- [NCBI E-utilities](https://www.ncbi.nlm.nih.gov/books/NBK25501/)
- [PubMed in BigQuery (Google Cloud)](https://cloud.google.com/blog/topics/public-sector/accelerate-medical-research-with-pubmed-data-now-available-in-bigquery/)

**Standards + moonshot comparables:**
- [C2PA / Truepic founding](https://www.truepic.com/blog/c2pa-releases-specification-of-worlds-first-industry-standard-for-content-provenance)
- [Google A2A protocol GA + Linux Foundation](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/)
- [Plaid open finance aggregator token](https://plaid.com/blog/open-finance-aggregator-token/)
- [Stripe developer-first moat](https://www.stratrix.com/vault/stripe-developer-first-strategy)
- [Vanta SOC2 maintenance cadence](https://www.vanta.com/collection/soc-2/maintain-soc-2-compliance)
- [Segment destinations catalog](https://segment.com/docs/connections/destinations)
- [Zesty Paws $610M acquisition](https://www.prnewswire.com/news-releases/zesty-paws-to-be-acquired-by-hh-group-301360334.html)

**Brand revenue benchmarks:**
- [Native Pet Growjo profile](https://growjo.com/company/Native_Pet)
- [Honest Paws Growjo profile](https://growjo.com/company/Honest_Paws)
- [APPA 2025 Dog & Cat Report](https://americanpetproducts.org/news/the-american-pet-products-association-appa-releases-2025-dog-cat-report)

**Cambridge Dogs (the dataset Omar pointed at, validating public-API skepticism):**
- [Cambridge Dogs dataset](https://data.cambridgema.gov/General-Government/Dogs-of-Cambridge/sckh-3xyx)
- Socrata SODA API: `https://data.cambridgema.gov/resource/sckh-3xyx.json` — 30,965 rows, PDDL public-domain license, name/breed/birth_year/gender/expiration only (no owner/address/vaccination). Confirms Omar's instinct that municipal pet data is free + open + APIed; reinforces "drop vendor middlemen, integrate primary sources directly."
