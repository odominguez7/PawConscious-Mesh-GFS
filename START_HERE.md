# START HERE — PawConscious Mesh (ACP for Pet)
## The complete picture, in one doc, written for the founder at 1am

**You are here:** Day 0 of an 18-day push to ship a Google for Startups hackathon submission that doubles as the launchpad for a $100M+ business.
**Deadline:** June 5, 2026 noon PT.
**Status:** Plan absorbed 3 codex sweeps; ready to execute pending your sign-off.

---

## ONE SENTENCE FOR EACH THING

- **What it is:** A SaaS tool that turns a pet product URL into a signed, continuously-updated evidence bundle — citations, vet scores, FTC-mapping, audit verdict — that the brand can show plaintiffs, retailers, regulators, consumers, and AI shopping agents.
- **What we sell:** A subscription at $99/mo (Starter) or $499/mo (Pro) per brand, plus enterprise contracts for retailers and insurers.
- **Who pays first:** Pet supplement brand CMO / Head of Compliance / General Counsel at DTC brands $1-50M ARR who just got a plaintiff demand letter or a Chewy substantiation ask.
- **Why now:** Cosequin paid $11.5M in 2024. AI shopping agents (Rufus, Perplexity Shopping) need callable trust signals by 2027. Both forces drive the same buy.
- **The architecture:** 5 Google ADK agents on Vertex Agent Engine, A2A v0.3 protocol, Gemini 3 Pro reasoning, BioMCP for PubMed, Cloud Run deployment. Branded as **ACP — Agentic Compliance Protocol.**
- **The wedge:** Pet supplements (low regulation, fast cycles). Scales to human supplements, beauty, functional food, every consumer vertical AI will mediate.
- **The northstar:** Every claim made on a commerce surface becomes machine-verifiable evidence that any accredited certifier can sign, any AI agent can query, any regulator can audit. Pet is the proving ground.

---

## THE PRODUCT — what a brand owner sees on day 1

**Sarah is Head of Compliance at a $15M ARR DTC pet supplement brand.** She got a plaintiff demand letter Tuesday. By Friday she finds PawConscious Mesh through the Shopify App Store or a cold email from us.

**This is exactly what she sees:**

1. Goes to `mesh-api-40952019806.us-central1.run.app`, pastes her hip-and-joint product URL
2. ~90 seconds: 5 agents fan out in parallel (she watches the Mesh Console light up)
   - `claim-extractor` pulls the 7 health claims from her PDP copy
   - `evidence-grader` queries PubMed via BioMCP, returns 12 papers, AI2 Asta scores them (247 total citations, 18 influential)
   - `vet-panel` runs a 5-vet rubric simulation, flags 2 claims for human-vet escalation
   - `compliance` maps each claim to FTC 16 CFR §255 + NASC public-side language, flags 2 violations
   - `auditor` (the Falsifier) catches one citation that doesn't support the claim direction, forces a re-grade
3. She sees a screen with: 5 ✅ claims (substantiated), 2 ⚠️ claims (need attention), 0 ❌ claims (must remove)
4. She gets 4 outputs:
   - **Signed evidence bundle** (JSON-LD, the "ACP Verified" cert) she can show plaintiff lawyers
   - **Audit-grade PDF** (the file she hands her GC)
   - **Embed JS** she pastes on the PDP — consumers see a "Verified by Vets" badge with click-popover showing the real PMIDs
   - **Continuous monitoring** — every week, the Auditor re-runs against new PubMed papers + regulator updates; if anything changes, Sarah gets an alert + auto-re-issued cert
5. She pays $499/mo. After 30 days, she launches 3 new SKUs and re-runs the flow on each.

That's the product. Everything else in the repo is architecture and business plan around making this work and scale.

---

## THE 3 USER PERSPECTIVES

### Brand owner (Sarah) — pays us
Sees a SaaS portal. Pastes URLs. Gets verifications. Embeds badges. Monitors alerts. Renews monthly. Expands to more SKUs. Pays $99-499/mo (SMB) or $5k+/mo (mid-market).

### Vet panel member (Dr. Larsen at Tufts Cummings) — paid by us, attests for credibility
Reviews flagged claims weekly. Signs attestations through ACP's vet portal. Gets $200/hr for time spent. Builds a portable reputation through DID signatures. Vet schools eventually mandate ACP-signed work as part of CE credit (Y3-4 ambition).

### Consumer (someone shopping Honest Paws on Chewy or asking Perplexity Shopping for "best joint supplement") — sees the badge, never pays us
On PDP: clicks the "Verified by Vets" badge → popover shows real PMIDs + signed vet names + last-updated date. Trust signal.
On Perplexity Shopping: Perplexity called our public A2A endpoint `verify_claim(sku, claim)` before answering. The answer says "Native Pet's joint supplement has 4 RCTs supporting the chondroitin claim; Honest Paws has 2; Brand X has 0." Consumer never sees ACP — but trusts the answer because Perplexity grounded it.

---

## ECONOMIC BUYERS — the ladder with names and dollar amounts

| Phase | Buyer (named title) | Vertical | Pain | What they pay |
|---|---|---|---|---|
| **Y1 H1** | CMO / Head of Compliance | Pet brand $1-10M ARR | Plaintiff demand letter, Chewy substantiation ask | **$99/mo** Starter |
| **Y1 H2** | General Counsel | Pet brand $10-50M ARR | Same + GC owns budget | **$499/mo** Pro or **$5k/mo** Enterprise |
| **Y2** | VP Trust & Safety, VP Vendor Management | Pet retailer (Chewy, Petco, Amazon Pet, Faire) | Catalog liability, counterfeit detection | **$250k-$2M/yr** platform fee |
| **Y2** | VP Claims, Chief Underwriting | Pet insurance (Trupanion, Nationwide, MetLife Pet) | Claims fraud, ingredient adulteration | **$500k-$3M/yr** |
| **Y3+** | Same titles, human-supplement brands | Human supplements ($60B US TAM) | Prevagen precedent, FTC §255 | **$25-500k/yr** |
| **Y3+** | VP AI Trust & Safety | AI shopping platforms (Perplexity, then Rufus/Operator/Gemini Shopping) | Need callable trust oracle | **$0 free** (asymmetry — they pay nothing, brands pay the metered backflow) |
| **Y3+** | Director of Enforcement | Regulators (NY AG, CA AG, FTC ESI Lab) | Audit query interface | **$0-$500k** or grant-funded |

Aulet DE step: every buyer's budget already exists (legal, compliance, vendor mgmt, claims ops, enforcement). We don't create new budget categories — we map to existing ones.

---

## WHY PATH B IS THE WINNING PLAN

Codex G7.2 forced us to consider "ACP as infrastructure for accredited certifiers" (pure rails). Codex G7.3 then said we over-corrected — pure rails makes us totally dependent on partner LOIs we don't yet have.

The 4 alternatives laid out:

| | A. Pure infra | **B. Program manager + evidence infra (RECOMMENDED)** | C. Pure compliance SaaS | D. Retailer mandate |
|---|---|---|---|---|
| Who issues the cert? | NASC / NSF (partner only) | **ACP issues "ACP Verified" using its own vet panel. Partners optional upside.** | Brand issues their own; ACP is just engine | Retailer mandates ACP cert on brands |
| Demo works June 5 without partner LOI? | **No — story breaks** | **Yes — we ARE the certifier, vet panel attests** | Yes | No — nothing in 18 days |
| Founder-led brand sales velocity | Slow (partner gates everything) | **Fast (direct brand sales day 1)** | Fastest (commodity tool) | Zero in 18 days |
| Pricing power | Low (partner takes margin share) | **High (we keep full margin)** | Medium | Low (retailer takes share) |
| Series A defensibility | Strong (regulated channel) | **Strong (multiple paths visible)** | Weak (commodity tooling) | Strong (mandatory channel, slow) |
| Liability | Bounded (partner carries) | **Bounded (vet attestation carries E&O; ACP infra-correctness only)** | Brand carries | Bounded |
| What if NASC says no? | **Dead** | **Fine — we still have a working business** | N/A | Dead |
| Day 1 conversation with Native Pet / Honest Paws | "Wait until our partner says yes" | **"$99/mo, free 30-day pilot, our vet panel signs. Want a demo?"** | "Buy our tool, you do the work" | "Talk to Chewy first" |

**B wins because it keeps us shipping no matter who else moves.** We're not blocked on NASC. We're not blocked on Chewy. We're not waiting for Series A. We ship the product, we sell to brands, we use the partner channel as a flywheel — not a gate.

The day-120 kill criteria (codex G7.3 P0):
- If 1+ accredited certifier signs an LOI to be certifier-of-record by **September 15, 2026** → we expand toward A (true infrastructure)
- If zero LOI by then → we pivot positioning to C (pure SaaS) or D (retailer mandate); the demo + product + revenue continues

Path B is "founder-controlled, partner-optional." That's why it wins.

---

## HOW THIS ALIGNS WITH CURRENT PAWCONSCIOUS

| | Current PawConscious (live today) | PawConscious Mesh (hackathon build) |
|---|---|---|
| URL | `pawconscious.com/portal` | `mesh-api-40952019806.us-central1.run.app` (new sub-domain) |
| Codebase | `~/Desktop/PawConscious/` (Next.js + LangGraph + Subconscious TIM-Qwen3.6-27B + Natoma MCP) | `~/Desktop/PawConscious-GFS/` (Next.js + Google ADK + Gemini 3 Pro + BioMCP) — **NEW REPO** |
| Hosted on | Vercel | Google Cloud Run (hackathon requirement) |
| LLM | Subconscious TIM-Qwen3.6-27B | Gemini 3 Pro (hackathon requires Google-only) |
| MCP | Natoma PubMed | BioMCP + AI2 Asta MCP |
| Status | Production, 1 paid hackathon demo (Subconscious + Natoma 2026-05-13 first place) | Brand new, ships June 5 |
| Brand name customers see | PawConscious (Verified by Vets) | PawConscious Mesh — powered by ACP |
| Use in hackathon submission | NOT submitted (separate codebase, separate LLM, separate MCP — disclosed in Devpost) | THE submission |

**Both stay alive during the hackathon:**
- Current PawConscious keeps running for any existing demo traffic + Subconscious follow-ups
- PawConscious Mesh is the new ADK product on Google Cloud

**Post-hackathon (Q3 2026):** Current PawConscious gets sunset and customers migrate to PawConscious Mesh. Same brand name, same vet panel, same wedge — better infrastructure underneath.

For the GFS submission: 100% of repo content is newly written during contest period (May 5 - June 5 per Rapid Agent rules; verify GFS dates). Disclosed in Devpost: "PawConscious Mesh is a new build for this hackathon. The live consumer site pawconscious.com/portal uses a separate codebase from a prior Natoma+Subconscious hackathon."

---

## CAN PATH B TALK TO ANY D2C BRAND TODAY?

**Yes. More cleanly than any other path.** Here's the cold email I send Native Pet on Day 1 morning:

> Subject: Plaintiff exposure on chondroitin claims — defense file in 90 seconds
>
> Hi [Native Pet GC],
>
> Cosequin paid $11.5M last year for chondroitin substantiation gaps. VetriScience GlycoFlex's class action is pending on the same theory. Plaintiff bar is templating these cases.
>
> I built PawConscious Mesh — your team pastes a product URL, our 5-agent system runs PubMed citations + a 5-vet rubric + FTC §255 mapping + adversarial audit, and you get a signed evidence bundle in 90 seconds. $499/mo for 25 SKUs; free 30-day pilot.
>
> Shipping to Google for Startups AI Agents hackathon June 5, but you can pilot now. Demo this week?
>
> Omar
> mesh-api-40952019806.us-central1.run.app (live by 5/20)

That's a real ask, real product, real price, real pilot. No "wait for NASC." No "buy a SOC2 first." No "let me explain the protocol." Just a SaaS pitch backed by real architecture.

The brand says yes or no based on whether the pain is acute. With Cosequin and the active plaintiff dockets, the pain is acute for a measurable subset of the 200-300 US DTC pet supplement brands.

That's the entire Y1 sales motion. Founder-led outbound to brands with active legal exposure, $99-499/mo, scale up as we land 50 brands by EOY.

---

## THE WINNING PLAN — 18 days condensed

```
WEEK 1 (May 18-24) — DEMO FOUNDATION
  Mon  GCP project + billing + APIs; salvage GUARDIAN code; SEND 10 EMAILS
  Tue  ADK 5-agent scaffold; orchestrator fan-out works
  Wed  BioMCP wired; first real PMID end-to-end
  Thu  PubMed-in-BigQuery + Vertex AI Search (Google-first parallel path)
  Fri  ParallelAgent fan-out on real Honest Paws URL
  Sat  A2A v0.3 card live; verify_claim returns real result
  Sun  PCEC v0.1 schema + resolver + Ed25519 signing → CODEX G8

WEEK 2 (May 25-31) — POLISH + CREDIBILITY SIGNAL
  Mon  ShopperAgent built + deployed; external A2A round-trip verified
  Tue  Mesh Console UI port from GUARDIAN
  Wed  Auditor + cert issuance + embed snippet
  Thu  Public-corpus ingest (FTC §255 + AAFCO + NASC public side)
  Fri  Vet-panel rubric + Memory Bank; SECURE 1 CREDIBILITY QUOTE
  Sat  O22 brief; Veo + Lyria start rendering
  Sun  Demo recording: full flow + live A2A moment → CODEX G9

WEEK 3 (Jun 1-5) — SUBMISSION
  Mon  Demo video final cut
  Tue  Devpost packaging; YouTube upload
  Wed  Hosted URL test; stranger test → CODEX G10
  Thu  Buffer; outside-voice review; final polish
  Fri  SUBMIT BY NOON PT
```

**Single gating milestone for hackathon win:** stable demo + crisp narrative + 1 credibility signal (quote from accredited body or academic vet).

**Single gating milestone for the business by Day 120 (Sep 15):** 1 accredited certifier LOI OR pivot to Plan C/D.

---

## TOMORROW MORNING (Day 1, June 18) — exact first 6 hours

**06:00-10:00 — Build day-1 demo skeleton.**
- `gcloud projects create pawconscious-mesh-2026`
- `gcloud beta billing projects link pawconscious-mesh-2026 --billing-account=014E26-090236-16FFE3`
- `gcloud config configurations create pawconscious-mesh && gcloud config configurations activate pawconscious-mesh`
- Enable APIs: Vertex AI, Agent Engine, Cloud Run, BigQuery, Vertex AI Search, Cloud Storage, Secret Manager, Cloud Build
- Scaffold ADK project structure
- Build 1 working agent (claim-extractor with Firecrawl MCP + Gemini 3 Pro)
- Deploy to Cloud Run with public hosted URL
- Test against the real Honest Paws hip-and-joint PDP

**10:00-11:00 — Send 10 cold emails:**
- 3 accredited certifiers: NASC Bill Bookout, NSF International supplements lead, ConsumerLab director
- 5 vet-school nutrition programs: Tufts Cummings (Dr. Jennifer Larsen), Cornell (Dr. Joseph Wakshlag), UPenn (Dr. Kathryn Michel), UC Davis, NC State
- 2 pet-brand GC outreach: Native Pet, Honest Paws

**11:00-12:00 — Draft 3-min demo narrative.**
- Cold open: Honest Paws PDP + Cosequin $11.5M context
- Paste URL → 5 agents fan out
- Real PMIDs returned, vet panel scores, Auditor catches issue
- Signed cert + embed appears
- ShopperAgent calls our A2A card live
- Close: "ACP Verified. Pet today. Every consumer vertical tomorrow."

**Afternoon:** Continue Day 1 plan (codex G8 fires Sunday on the week's work).

---

## WHERE TO READ MORE (only when you want depth)

| File | What it is | When to read |
|---|---|---|
| `START_HERE.md` (this doc) | **One-doc consolidated view** | Read first, always |
| `PLAN.md` | Engineering roadmap — 18-day build plan | When you want to verify the daily build steps |
| `BUSINESS_PLAN.md` | Full business plan — moat, competitive landscape, 5-yr arc, validation | When you want strategic depth |
| `DISCIPLINED_BUSINESS.md` | BMC + DE 24-step + CAC:LTV per tier + Google fit + hackathon compliance | When you want MIT-Aulet × Osterwalder rigor |
| `docs/PCEC-v0.md` | Draft protocol spec (the open-spec long-game) | When you want the standards-play depth |
| `docs/A2A-AGENT-CARD.md` | Public agent card design (the AI-agent-callable surface) | When you want the A2A implementation depth |
| `docs/ARCHITECTURE.md` | System architecture — 5 agents, data layer, deployment | When you want the technical depth |
| `reviews/codex-G7-verdict.txt` | First codex sweep BLOCK (absorbed) | If you want to see how the plan got sharpened |
| `reviews/codex-G7.2-verdict.txt` | Second codex sweep BLOCK (forced the infra-vs-certifier pivot) | If you want to see why we pivoted |
| `reviews/codex-G7.3-verdict.txt` | Third codex sweep BLOCK (forced Alternative B + stop-list) | If you want to see why path B is recommended |

**You don't need to read the others to make the go/no-go decision. This doc has the full picture.**

---

## THE DECISION I NEED FROM YOU

1. **Read this doc top to bottom.** Does the picture click?
2. **Approve Path B** (program manager + evidence infra; founder-controlled, partner-optional).
3. **Approve GitHub push** of repo as `PawConscious-Mesh-GFS` public MIT.
4. **Approve D1 execution** tomorrow morning per the 6-hour block above.

Say "GO" and I:
- Commit this doc + update README to point to START_HERE.md
- Push the repo to GitHub public
- Begin Day 1 work tomorrow 6am

Or tell me what's still unclear and I'll sharpen further.
