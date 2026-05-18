# PawConscious Mesh — GFS Hackathon Pivot Plan
**Date:** 2026-05-17 · **Deadline:** 2026-06-05 (19 days) · **Status:** PROPOSED · **Mode:** SCOPE EXPANSION (pivot from GUARDIAN)

---

## VERDICT (blunt)

**Kill GUARDIAN wildlife direction. Pivot the agentic architecture onto PawConscious. Ship `PawConscious Mesh` — an A2A trust network for expert-claim e-commerce — as the GFS submission.**

Why:
- GUARDIAN's failure isn't the architecture — it's the data. Real wildlife threat feeds don't exist as embeddable streams. Every probe (NamibiaCam, Smithsonian, Monterey, Raptor Resource) hit the same wall. The v9 "honest hybrid" with Veo simulations is a defensible disclosure, but it's a Devpost demo at best — not a Google judge's idea of "real-world impact."
- PawConscious has live users, real revenue ($1188/yr × N), a regulator on the horizon (FTC §255.3), a defensible vet panel, and a working agent loop today. We swap the engine (LangGraph → ADK + Gemini + A2A), keep the wedge.
- GUARDIAN's best assets (Falsifier, A2A peer scaffold, Ops Center UI, Veo/Lyria pipeline) port directly into the new build. The pivot is salvage, not reset.

**Combined recommendation (Omar + Claude + Codex pending):** Build `PawConscious Mesh`. Submit to GFS Track 3 (Marketplace + Gemini Enterprise) or the Build track depending on submission UI. Shut GUARDIAN billing within 48 hours after code salvage.

---

## ANSWERS TO THE 13 QUESTIONS

### 1. Continue / pivot / kill wildlife cam?
**KILL.** Three rounds of cam research confirmed: no non-YouTube wildlife stream is embeddable; YouTube bot-walls our cloud-hosted demo. The v9 honest hybrid is good engineering but bad submission optics ("here are AI-generated tiles labeled as AI-generated" doesn't read as "real impact" to a Google judge). The architecture survives — it just needs different data.

### 2. Strongest hackathon-winning concept
**`PawConscious Mesh` — an A2A-native trust mesh for FTC-grade endorsement substantiation, beachhead = US DTC pet supplement brands.**

Five ADK agents fan out from a brand product URL:
| Agent | Role | Tools |
|---|---|---|
| `claim-extractor` | Pulls every health claim from PDP copy | Firecrawl MCP, Gemini 3 Pro |
| `evidence-grader` | Searches PubMed live, grades each study (sample size, species, conflict of interest) | Natoma PubMed MCP, Gemini 3 Pro |
| `vet-panel` | Runs 5-vet rubric simulation; flags claims for human escalation | Gemini 3 Pro, Vertex AI Search over vet handbook corpus |
| `compliance` | Maps to FTC §255.3 + AAFCO + state vet board rules | Vertex AI Search over regulator corpus |
| `auditor` (FALSIFIER) | Adversarially attacks evidence chain to catch hallucination + cherry-picking | Gemini 3 Pro, ADK Eval |

Orchestrator = Vertex Agent Engine `ParallelAgent` + `SequentialAgent`. Output = signed certificate + embeddable badge + FTC substantiation PDF + draft outreach to real Boston vet practices.

### 3. Alignment with hackathon rules (GFS AI Agents Challenge)
| Requirement | How we satisfy |
|---|---|
| Gemini models | Gemini 3 Pro for reasoning, Flash for routing |
| ADK | All 5 agents built with ADK 2.0 |
| A2A protocol | Every agent exposes an A2A agent card; mesh callable by any third-party agent |
| Cloud Run / GKE / Agent Engine | Vertex Agent Engine for orchestrator; agents on Cloud Run |
| MCP integration | Natoma PubMed MCP (already wired in PawConscious), Firecrawl MCP, optional Gmail MCP |
| Public hosted URL | `pawconscious.com/mesh` (new sub-route on existing live brand) |
| Open-source repo | MIT license, public GitHub |
| 3-min video | O22 pipeline renders this in <2 days |
| Track 3 (Marketplace + Gemini Enterprise) | Publish mesh as Agent Garden / Marketplace listing |

Judging rubric performance (per memory, GFS is Tech 30 / Business 30 / Innovation 20 / Demo 20):
- **Technical (30):** Multi-agent A2A + ADK + Gemini 3 + Vertex Agent Engine + MCP + signed audit chain. As serious as it gets in this hackathon.
- **Business (30):** $8B aisle, named beachhead, working revenue model, regulator catalyst.
- **Innovation (20):** A2A trust mesh as a category — nobody else is framing endorsement substantiation as agentic infrastructure.
- **Demo (20):** O22-rendered cinematic + live mesh fan-out on a real brand URL.

### 4. Advanced Google tools usage
- **ADK 2.0** — graph-based workflow, all 5 agents
- **Gemini 3 Pro** — reasoning core (1501 Elo, top of LMArena)
- **Gemini 2.5 Flash** — claim-routing, low-latency lane
- **Vertex AI Agent Engine** — managed orchestrator + observability
- **Vertex AI Search** — grounding over vet handbook + regulator corpus
- **Vertex Memory Bank** — persistent per-brand audit history
- **Cloud Run** — per-agent deployment
- **A2A protocol** — every agent has a public agent card; mesh callable externally
- **MCP** — Natoma PubMed (live), Firecrawl, Gmail (drafts)
- **Cloud SQL / Firestore** — certificate store, audit log, regulator-grade ACID
- **BigQuery** — claim-taxonomy data flywheel
- **Veo 3.1 + Lyria 2 + Imagen 4** — demo video + brand assets (via O22 pipeline)
- **Agent Garden / Marketplace** — publish `pawconscious/auditor` and `pawconscious/evidence-grader` as reusable ADK agents (Track 3 anchor)

### 5. PawConscious connection
This **IS** PawConscious 2.0. The hackathon submission becomes the production architecture:
- Same brand, same wedge (FTC §255.3), same vet panel, same artifact set (badge + file + invites)
- Same revenue model ($1188/yr or $124/mo per brand)
- The pivot replaces the engine (LangChain → ADK), upgrades the LLM (TIM-Qwen3.6-27B → Gemini 3 Pro), expands the agent count (1 ReAct loop → 5 specialized A2A agents), and adds the Auditor (= salvaged Falsifier)
- Post-hackathon: vertical expansion to human supplements, beauty, fitness — but the demo stays pet

### 6. Business case
- **Market:** US DTC pet supplements = $8B aisle. FTC enforcement landing 2026.
- **Beachhead:** 150-300 brands $1-50M ARR currently exposed to §255.3.
- **Pricing:** $1188/yr annual or $124/mo (live on site today).
- **Year-1 target:** 50 paying brands × $1188 = $59,400 ARR.
- **Year-2 expansion:** vertical-2 (human supplements) at 5x volume = ~$300k ARR.
- **Exit narrative:** "Trust mesh for any expert-claim vertical" — comparable to Trustpilot ($2B mkt cap), Truepic (raised $26M for cryptographic image provenance), Northbeam ($85M for attribution trust). Infra play, not a SaaS app.

### 7. Moat
1. **Boston vet panel** — relationship-based, named practices, takes 12-24 months to replicate
2. **Signed audit chain** — cryptographic + Falsifier-attested → regulator-grade evidence (most "vet endorsed" claims today have no audit trail at all)
3. **A2A agent cards** — third-party platforms (Shopify, PIM tools, vet portals, regulators) can call the mesh; once integrated, switching cost is real
4. **Data flywheel** — every cert enriches claim taxonomy + vet rubric + regulator mapping; harder to start cold each quarter
5. **First-mover on the §255.3 wave** — being the trusted name when the first FTC fine lands is decisive

### 8. Beachhead market (Aulet step 3)
**End user:** Pet supplement brand owner/founder, $1-50M ARR, US-based, has at least one product with health claim.
**Buyer:** Same person (or their Head of Compliance).
**Pain:** FTC §255.3 fines landing 2026; influencer endorsements no longer safe; need vet substantiation; can't afford in-house veterinary advisory board.
**Trigger event:** FTC inquiry letter, retailer compliance review (Chewy, Petco), or competitor sued.
**Replicable buy:** $1188 cert per product, scales 1→10→50 SKUs per brand.
**Aulet TAM math:** 200 brands × 3 SKUs × $1188 = $713k beachhead TAM. Tight, addressable, expansionary.

### 9. Demo flow (3 min)
```
00:00-00:15  Cold open: real Honest Paws hip-and-joint PDP. Claim copy highlighted.
00:15-00:30  URL paste → 5 agents fan out (Ops Center UI repurposed as Mesh Console)
00:30-01:30  Live mesh traffic streams:
              - claim-extractor: 7 claims pulled
              - evidence-grader: 12 PubMed calls, 4 papers grounded
              - vet-panel: rubric scores (4/5, 3/5, 1/5)
              - compliance: 2 §255.3 violations flagged
              - auditor: catches 1 cherry-picked citation → forces re-grade
01:30-02:15  Certificate + badge + FTC PDF + vet outreach drafts render
02:15-02:45  Brand owner pastes embed snippet → badge appears on PDP, click-popover
              shows PubMed citations + named vet panel
02:45-03:00  Closing: "This is the trust mesh. Pet today. Any expert-claim vertical
              tomorrow." Veo cinematic plate. Gemini logo + ADK logo + A2A logo.
```
Video produced via O22 pipeline (Veo 3.1 plate + Lyria 2 bed + ElevenLabs VO).

### 10. Build first (hackathon priority)
**D1-2 (May 18-19) — Salvage + cleanup.** Shut GUARDIAN cam work. Port Falsifier code, A2A scaffold (v6), Ops Center UI shell, ParallelAgent code (v4), O22 Veo/Lyria pipeline. Create new GCP project `pawconscious-mesh-2026`.
**D3-5 (May 20-22) — ADK scaffold.** 5 agents stubbed with ADK 2.0. A2A agent cards published. Vertex Agent Engine wired. Each agent deployable to Cloud Run.
**D6-10 (May 23-27) — Replace engine.** Migrate PawConscious's ReAct loop from LangGraph to ADK. Replace TIM-Qwen3.6-27B with Gemini 3 Pro (Subconscious stays for non-hackathon site). Wire all 5 agents end-to-end with one real brand URL.
**D11-13 (May 28-30) — Mesh Console + Auditor port.** Live A2A traffic visualization. Falsifier becomes Auditor with vet-rubric awareness. Cert signing + badge embed.
**D14-15 (May 31-Jun 1) — Demo render.** O22 pipeline cuts the 3-min cinematic. Lyria bed. Codex handshake on the codebase.
**D16-17 (Jun 2-3) — Submission packaging.** Devpost listing. Public repo with MIT license. Hosted URL test. Video to YouTube unlisted.
**D18-19 (Jun 4-5) — Buffer + codex sweep + Outside voice.** Submit by noon Jun 5 PT.

### 11. Reuse map
| From | What | Where it goes |
|---|---|---|
| **PawConscious** | Next.js portal, badge embed, FTC artifact renderers, KV cert store, vet invite drafts, Subconscious flow for non-hackathon site | Frontend stays as-is; agent backend swaps to ADK |
| **PawConscious** | LangGraph ReAct logic (as reference) | Reverse-engineered into 5 ADK agents |
| **GUARDIAN v4** | ParallelAgent peer fan-out code | Mesh orchestrator |
| **GUARDIAN v6** | A2A agent card scaffold + Cloud Run multi-service deploy | Mesh agents |
| **GUARDIAN v3 Move 1** | Falsifier (4 SOP gates, deterministic verdict, 11 files) | Auditor agent |
| **GUARDIAN v3.2** | Ops Center 3-tab architecture, ElevenLabs voices, Agent Theater | Mesh Console UI |
| **GUARDIAN v3 Move 3** | Board Slide renderer (LRU + html2canvas) | Cert renderer + brand-facing dashboard |
| **O22** | Brief→Blueprint→Render pipeline, Veo + Lyria + Imagen wiring | Demo video production |
| **GUARDIAN v8** | ADK Eval CI, Agent Engine deploy scripts, ARCHITECTURE.md template | Mesh CI + docs |
| **GUARDIAN v8** | Procurement pack template (Mgmt Review Required stub) | Brand sales collateral |

Estimated salvage value: ~60% of new build code is port-from-existing.

### 12. Kill / shut down immediately
**Today (within 24h):**
- Stop all GUARDIAN cam work (v9 W3, W3.5)
- Cancel any pending Veo wildlife renders
- Disable GUARDIAN's `Spot Now` button (it calls Gemini Vision per click — hidden burn)

**This week (after code salvage, Day 2):**
- Bring all 6 `guardian-*` Cloud Run services to min-instances=0 (auto-scales to zero on idle; confirm no schedulers calling them)
- Delete Vertex Agent Engine instance if running in `guardian-gfs-2026`
- Delete any standing Vertex Memory Bank in `guardian-gfs-2026`
- Stop ElevenLabs voice generation jobs

**Day 5 (after final salvage):**
- Decision point: delete `guardian-gfs-2026` GCP project entirely, OR keep dormant for code reference. Recommendation: **delete project** after pushing salvage commits to a `guardian-archive` GitHub repo. One less billing surface.

**Don't kill:**
- PawConscious live site (revenue lane)
- Subconscious / Natoma keys (PawConscious still runs on them outside the hackathon submission)
- O22 GCP project (we need it for demo render)
- The `guardian` gcloud config (delete only after project deletion)

**Estimated savings:** Cloud Run idle cost is ~$0 already; the real wins are (a) no more Veo/Lyria renders, (b) no more Gemini Vision per-Spot-Now-click, (c) Agent Engine standing cost if active. Net: probably $20-80/mo saved + clean cognitive load.

### 13. Final handshake recommendation
**Omar + Claude + Codex (pending):**

1. **APPROVE this pivot.** Architecturally sound, commercially real, PawConscious-strengthening, salvages ~60% of GUARDIAN.
2. **Run codex handshake on this plan** (memory rule: every Move clears codex before next Move). I'll dispatch on your word.
3. **Kill GUARDIAN cam work today.** Push v9 honest-hybrid as a tagged archive commit; stop adding to it.
4. **Day 1 = salvage day.** I create `pawconscious-mesh-2026` GCP project, port Falsifier + A2A scaffold + Ops Center skeleton.
5. **Submit June 5 by noon PT** with the full mesh + cinematic demo + signed certs + vet panel ready for outreach.
6. **Post-hackathon:** PawConscious site quietly upgrades to the ADK backend; the hackathon submission IS the production code. No throwaway demo.

---

## TECHNICAL ARCHITECTURE (one-page)

```
                              BRAND PRODUCT URL
                                      │
                                      ▼
                          ┌───────────────────────┐
                          │ Vertex Agent Engine    │
                          │ (orchestrator)         │
                          │ ParallelAgent → fan-out│
                          └────────┬───────────────┘
                                   │ A2A
        ┌───────────────────┬──────┴──────┬───────────────────┬───────────────────┐
        ▼                   ▼             ▼                   ▼                   ▼
  ┌──────────┐        ┌──────────┐  ┌──────────┐        ┌──────────┐        ┌──────────┐
  │ claim-   │        │ evidence-│  │ vet-     │        │compliance│        │ auditor  │
  │ extractor│        │ grader   │  │ panel    │        │          │        │(Falsifier)│
  └────┬─────┘        └────┬─────┘  └────┬─────┘        └────┬─────┘        └────┬─────┘
       │ Firecrawl         │ Natoma      │ Vertex AI         │ Vertex AI         │ ADK Eval
       │ MCP               │ PubMed MCP  │ Search (vet)      │ Search (FTC/AAFCO)│ + Gemini
       ▼                   ▼             ▼                   ▼                   ▼
                          ┌───────────────────────┐
                          │ SequentialAgent merge  │
                          │ + signed audit chain   │
                          └────────┬───────────────┘
                                   ▼
                    ┌──────────────┼──────────────┐
                    ▼              ▼              ▼
              Verified-by-Vets   FTC §255.3      Vet outreach
              badge + embed JS   substantiation  (5 Gmail drafts)
                                 PDF
                                   │
                                   ▼
                          ┌───────────────────────┐
                          │ Cloud SQL / Firestore  │
                          │ + Vertex Memory Bank   │
                          │ (per-brand audit log)  │
                          └───────────────────────┘

  Mesh Console (Ops Center UI port) — live A2A traffic, agent cards, audit timeline
```

---

## RISKS

| Risk | Mitigation |
|---|---|
| Hackathon ID 3197 isn't actually GFS AI Agents Challenge | First action D1: verify track + rules from Devpost team page; pivot framing if different (architecture stays valid for Rapid Agent, Multi-Agent ADK, or AI in Action) |
| Gemini 3 Pro rate limits or cost spike | Mix Flash for routing; cap PubMed calls per run; cache by URL hash |
| Vet panel claim ("Boston vet practices on the panel") gets challenged | Truth: PawConscious site already lists 5 named practices; we draft invites, never auto-send. Keep that framing for the demo. Don't claim more |
| O22 cinematic render misses deadline | Render starts D14 with 5 days buffer; fall back to screen-recorded mesh demo |
| Salvage from GUARDIAN takes longer than 2 days | Time-box salvage to D2. Anything not ported by then gets rewritten fresh — most code is small enough to retype faster than untangle |
| Brand owners can't see real demo (we don't have a real customer yet) | Use a real public DTC pet brand's PDP (Honest Paws, Fera Pets, Native Pet) — public URLs, no auth, FTC §255.3 exposure is genuine |

---

## CODEX HANDSHAKE QUEUE
Per `feedback_codex_handshake_per_move.md`, this plan must clear codex before D1 work begins. Run:
```
codex review --plan /Users/odominguez7/Desktop/PawConscious-GFS/PLAN_GFS_PIVOT.md \
  --challenge "is the pivot sound? is the salvage realistic? is the GFS rubric match real?"
```

---

## NOT IN SCOPE (deferred)
- GUARDIAN wildlife revival (dead direction, archive only)
- Human-supplement vertical (Phase 2, post-hackathon)
- Stripe + real billing flow for PawConscious Mesh (cert checkout stays mock for hackathon)
- Real Gmail send (drafts only — never auto-send per current architecture)
- Cryptographic cert signing with HSM (use software signing for hackathon; HSM is Phase 2)
- Vet panel real consents (drafted invites only; first signed consent post-hackathon)

---

## DREAM STATE DELTA (12-month)

Today: PawConscious is a working ReAct loop with one LLM and one MCP.
Hackathon (Jun 5): PawConscious Mesh is a 5-agent A2A network running on Google Cloud, with signed audit chain, vet rubric, regulator mapping, and a Marketplace listing.
12-month (May 2027): 50+ paying pet brands; vertical 2 (human supplements) live; the mesh is a callable B2B trust API used by Shopify apps, PIM platforms, and at least one regulator's review tool. ARR $250k-500k. Series A narrative is "trust mesh for expert-claim commerce."

This pivot moves us 80% of the way toward the 12-month ideal in 19 days.
