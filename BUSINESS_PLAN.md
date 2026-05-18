# ACP — Agentic Compliance Protocol
## Business Plan v1 — built with /plan-ceo-review rigor, pending codex G7.2 handshake

**Date:** 2026-05-18 · **Status:** PROPOSED → pending codex CLEAR · **Authors:** Omar (founder), Claude (drafting partner)

---

## NORTHSTAR (single guiding sentence, every decision tests against this)

**Every claim made on a commerce surface — about ingredients, efficacy, expertise, provenance, safety, or performance — becomes machine-verifiable, AI-agent-callable, and regulator-grade by default. Pet is the proving ground. AI-mediated commerce is the platform shift that makes it inevitable.**

---

## EXECUTIVE SUMMARY

ACP is the verifiable claim infrastructure layer for consumer goods. We sign, audit, and serve product claims as machine-readable bundles callable by any AI agent, readable by any regulator, and embeddable on any commerce surface.

We launch via **PawConscious Mesh** — the pet-supplement reference deployment — because pet is the least-regulated, most-fragmented, plaintiff-pressured consumer vertical where we can iterate fast without killing humans. The same protocol then expands to human supplements, beauty, functional food, wellness devices, and ultimately every product-claim surface AI agents will mediate by 2028.

**The business model is two-sided usage billing with a regulatory premium tier.** Brands pay per signed claim + per badge impression + per agent query. AI shopping platforms call us free. Retailers and insurers pay enterprise contracts. Regulators get the open protocol for free in exchange for endorsing it as the canonical evidence format.

**The moat is three-layer compounding:** the open standard (PCEC), the claim-to-evidence graph (12-month data accrual), and the agent-default integration depth (the protocol Rufus/Operator/Perplexity hit by default).

**Year-3 revenue target $15-30M ARR; Year-5 target $80-200M.** Exit comps: Vanta $2.5B (compliance infra), Plaid $13B (data API protocol), Truepic $150M (provenance standard).

**18-day hackathon deliverable:** working multi-agent A2A mesh on Google Cloud, real PubMed citations, signed certs, public A2A endpoint exercised by our own ShopperAgent, PCEC v0.1 spec published as draft proposal. Pet reference vertical. Protocol roadmap publicly committed.

---

## THE PROBLEM (sharper than v1)

**Every consumer-goods product page lies in tiny ways that compound into massive liability and consumer mistrust.** "Vet-formulated." "Clinically proven." "Dermatologist-tested." "Sustainably sourced." "Third-party tested." Most of these claims have no audit trail a regulator, plaintiff lawyer, retailer, or AI agent can resolve.

For the brand:
- Class actions land with no defense file (Cosequin paid $11.5M in 2024; Prevagen $165M judgment; Mid America Pet Food $5.5M; VetriScience GlycoFlex pending)
- Retailers (Chewy, Petco, Amazon, Faire) increasingly ask for substantiation files at vendor onboarding and category review
- New AI shopping agents (Rufus, Operator, Perplexity Shopping, Gemini Shopping) will ignore brands without machine-verifiable claims
- In-house compliance teams cost $200-500k/year; outside vet consultants charge $200/hour and produce static PDFs nobody can query

For the consumer:
- No way to distinguish "real vet panel" from "vet on payroll"
- Influencer endorsement substantiation is now FTC-regulated under §255 (2023 update) but unenforced consistently
- AI shopping answers will increasingly determine purchase — they need a trust signal

For the regulator:
- FTC §255 enforcement requires evidence; FTC currently subpoenas brands case-by-case
- AAFCO, state AGs, FDA-CVM each pull in different directions; no shared evidence format
- Plaintiff bar moves faster than agencies, but uses the same gap

The status quo across all three sides is **trust-by-vibes plus litigation-as-enforcement.** ACP replaces it with trust-by-signed-evidence plus continuous-verification-as-infrastructure.

---

## WHAT ACP ACTUALLY PRODUCES (4 outputs, each with a retention loop)

This was the question. Here's the complete answer.

| Output | Format | Who consumes it | Retention loop |
|---|---|---|---|
| **1. Signed claim bundle** | JSON-LD (PCEC v0 schema) | AI agents, retailers, regulators, our own resolver API | EVERY query is a metered API call. As AI-shopping traffic grows, brand's monthly bill grows. |
| **2. Audit-grade PDF** | Human-readable evidence pack | Brand's legal counsel, FTC inquiries, plaintiff defense, retailer onboarding files, M&A diligence | Re-issued on schedule (cert TTL = 12 months); replaced every time science / regulator / claim text changes. |
| **3. Live badge with click-popover** | Embed JS + verifiable status | Consumers on PDP, retail product detail pages, ad-tech, AI agent responses | Metered per impression (analogous to Cloudflare/Twilio per-1k pricing). Removing it drops conversion + AI-agent ranking. |
| **4. Continuous monitoring + alerts** | Webhook + dashboard | Brand compliance/legal team | **THIS is the Vanta loop.** Daily diff against new PubMed papers, regulator updates, plaintiff theories. Brand can't go a quarter without us. |

The brand doesn't buy a one-time check. **The brand buys ongoing verifiable status.** A cert without continuous monitoring is the same as a SOC2 report from 18 months ago — worth nothing.

---

## WHY BRANDS KEEP PAYING (the retention answer — 12 reasons)

Omar's concern: "What if they verify, then fix, then stop paying?" Direct response.

1. **Claims change with every product launch.** DTC pet brands launch 3-12 new SKUs/year, 3-7 health claims per SKU. Each claim = re-verification cycle. Bigger brands = more SKUs = more revenue per account year-over-year.
2. **Ingredients change with every supplier lot.** Switch chondroitin source from Argentina to Mongolia? Re-verify substantiation. Re-issue cert.
3. **PubMed adds ~3 million papers per year.** A 2026 cert with 6 supporting papers may have 10 supporting + 3 contradicting by 2027. Auditor flags this on the daily diff. Cert revalidation required.
4. **Regulator landscape moves quarterly.** FTC §255 update 2023, AAFCO ingredient definitions annually, NASC seal requirements annually, state-by-state Prop 65 expansions, NY Prevagen precedent rippling. Brand needs continuous compliance mapping, not one-time.
5. **Plaintiff playbook evolves.** Cosequin's 2024 theory becomes the template for 2026 cases. Brand's audit log must demonstrate "as of the most-recent plaintiff theory, your claims still pass." Moving target.
6. **Retailer compliance asks evolve.** Chewy adds new vendor requirements every quarter. Amazon Pet adds new substantiation requirements. Petco Buyer changes asks. Brand needs to ship updated cert with every recategorization.
7. **AI-agent traffic is metered.** Every Rufus / Operator / Perplexity Shopping / Gemini Shopping `verify_claim` query bills the brand. As AI-mediated commerce grows from 0% to 20%+ of considered purchases by 2028 ([emerging consensus](https://www.gartner.com/en/newsroom)), brand's per-query revenue line grows linearly.
8. **Badge impressions are metered.** Every PDP view = badge load = billable. Retailer pages, ad-tech, AI agent answers — all trigger impressions. Brand traffic up = brand bill up.
9. **Insurance and underwriting integration.** Trupanion, Nationwide, MetLife Pet using ACP for claims-fraud detection means brand needs valid cert to keep retail distribution and consumer trust. Stop paying = lose claims-fraud protection = lose distribution.
10. **The Vanta cycle.** Biennial NASC audit recommits to ACP as substantiation-of-record. Annual brand legal review recommits. Every Series A round and M&A diligence requires fresh substantiation. The audit cadence IS the retention mechanism.
11. **Expert DID network lock-in.** Vets who've signed attestations through ACP have portable reputations. Brand leaving = losing access to the vet panel for new SKUs. Same dynamic that locked merchants into Stripe Connect.
12. **Cross-vertical expansion.** Brand expands from dog to cat. From supplements to functional treats. From pet to human (chondroitin overlap). From US to EU (EFSA compliance). Each expansion = expanded ACP footprint, never contraction.

**Net retention math:** If average brand starts at $5k/year and adds 30% new claim surface annually (SKUs + ingredient changes + AI agent query growth + impression growth), net retention is 130%+. Vanta and Plaid's models confirm — once the protocol is woven into operational + regulatory + AI-agent layers, churn is structurally low (industry-typical 5-8% gross, 100-130%+ net).

---

## BEACHHEAD VERTICAL — Pet (PawConscious reference deployment)

Why pet first:

| Dimension | Pet | Human supplements | Beauty | Functional food |
|---|---|---|---|---|
| Regulatory pressure | Light (FDA-CVM warning-letter level) | Heavy (FDA + FTC) | Moderate (FDA cosmetics + FTC) | Heavy (FDA + USDA) |
| Plaintiff catalyst | Real (Cosequin $11.5M) | Very real (Prevagen $165M) | Real (Sunday Riley) | Real (Hill's, Stella & Chewy's) |
| Liability if claim wrong | Low (no humans get hurt) | High | Moderate | High |
| Sales cycle | Weeks (DTC) | Months | Months | Months |
| Existing ecosystem ready for adoption | Yes (NASC primed market) | Partially | No | Partially |
| Founder advantage | PawConscious live, vet relationships | None | None | None |

Pet wins on every speed-to-iterate dimension. We perfect the agent workflow + signing + continuous monitoring in pet, then expand to human supplements (shared ingredients), then beauty, then functional food.

**Pet beachhead TAM math:**
- Universe: ~150-300 US DTC pet supplement brands ($1M-$50M ARR) per triangulation
- Year 1 target: 50 brands × avg $5k ARR = $250k
- Year 2 target: 200 brands + 1 retailer + 1 insurer pilot = $2-4M ARR (pet alone)

**Pet expansion lever:** retailers (Chewy, Petco, Amazon Pet) and insurers (Trupanion, Nationwide, MetLife Pet) pay 10-100× per-brand contracts once we have catalog coverage. This is where pet alone supports a $20-50M ARR business.

---

## SCALE PATH — Pet → Human → Every Consumer Vertical → AI Commerce

```
2026 Q2 (HACKATHON)         2027                          2028                          2029-2030
─────────────────────       ──────────────────────       ──────────────────────        ──────────────────────
Pet supplements             Human supplements             Beauty / cosmetics           Functional food
$2.8B US                    $60B US                       $90B US                      $300B+ US
                            (chondroitin / omega-3 /      (FDA-light, FTC-heavy        (FDA + USDA + claims-heavy
                             MSM ingredient overlap        retinol / SPF / "clean        "organic" / "grass-fed"
                             makes the leap mechanical)    beauty" claims)                / "non-GMO" / "regenerative")
                                                          
                            Pet retailers (Chewy)         AI commerce protocol         Wellness devices
                            + pet insurers                (Rufus, Operator,            $100B+ US
                            (Trupanion, Nationwide,        Perplexity, Gemini           (HSA-eligibility, FDA
                             MetLife Pet)                   Shopping default-call)       claims, "longevity")
                            
                                                                                       Athletic / performance
                                                                                       $50B+ US

                            $250k → $4M ARR              $4M → $30M ARR               $30M → $200M ARR
                            (pet wedge)                  (human extension)             (every consumer vertical)
```

The transition pet → human is **mechanical, not strategic**: the same ingredients (chondroitin, glucosamine, MSM, omega-3, probiotics, fish oil, turmeric, ashwagandha) appear in both pet and human supplements. Same PubMed corpus. Same evidence-grading logic. Same vet/MD attestation pattern. We add an MD network and ship.

---

## BUSINESS MODEL — Two-sided usage billing + regulatory premium

**Primary revenue (60-70% of mix at Y3):**
- Per signed claim issuance: $5-25 per claim (free tier ≤50 SKUs)
- Per 1k badge impressions: $0.50 (free tier ≤100k impressions/mo)
- Per AI-agent `verify_claim` API query: $0.001-0.01 (free tier ≤10k queries/mo)

**Enterprise revenue (25-35% at Y3):**
- Retailer platform fee (Chewy, Petco, Amazon Pet, Faire): $250k-$2M/year — bulk catalog verification + vendor screening
- Insurer enterprise (Trupanion, Nationwide, MetLife Pet, Embrace): $500k-$3M/year — claims-time lookup + underwriting feed
- Brand enterprise tier (>$50M ARR brands): $50k-$250k/year — dedicated SLA + custom integrations

**Protocol governance revenue (5-15% at Y3 onward):**
- Linux Foundation Steering Member fees (post-donation): $50k-$250k/year per member
- White-label PCEC reference implementations: $250k-$2M one-time + maintenance
- Regulator integration grants: $100k-$1M per regulator

**Data licensing (post-Y3):**
- Claim-to-evidence graph licensed to research orgs, M&A diligence firms, pharma discovery: $250k-$5M/year per licensee

The combination of high-volume metered usage + enterprise platform contracts + governance fees is Vanta's playbook stacked with Plaid's playbook stacked with C2PA's playbook. No single line carries the business.

---

## ECONOMIC BUYER LADDER (specific, named, sized)

| Phase | Buyer title | Vertical | Pain → budget line | Contract size |
|---|---|---|---|---|
| Y1 H1 | CMO / Head of Compliance | Pet brand $1-10M ARR | Plaintiff exposure + retailer ask → marketing + legal | $2-12k/year |
| Y1 H2 | General Counsel | Pet brand $10-50M ARR | Same + GC owns budget | $25-100k/year |
| Y2 | VP Trust & Safety / VP Vendor Management | Pet retailer (Chewy, Petco, Amazon Pet, Faire) | Catalog liability, counterfeit detection | $250k-$2M/year platform fee |
| Y2 | VP Claims / Chief Underwriting Officer | Pet insurance (Trupanion, Nationwide, MetLife Pet) | Claims fraud, ingredient adulteration | $500k-$3M/year |
| Y2-3 | Same titles | Human supplement brand $5-100M ARR | Prevagen precedent, FTC §255 | $25-500k/year |
| Y3 | VP AI Trust & Safety | AI shopping platform (Rufus/Amazon, Operator/OpenAI, Perplexity, Gemini Shopping) | Need callable trust oracle | $0 free + data-licensing back-flow |
| Y3+ | Director of Enforcement Tools | FTC, FDA-CVM, NY AG, CA AG | Audit query interface for active cases | $100k-$500k or grant-funded |
| Y4+ | Director of Substantiation, R&D | Pharma (Pfizer, Merck, GSK) for shared-ingredient supplements (chondroitin, omega-3) | White-label substantiation infra | $500k-$5M/year |

The buyer ladder is REAL because each tier already has an existing budget line we map to (legal, compliance, vendor management, trust & safety, underwriting, enforcement tools). We don't create new budget categories.

---

## UNIT ECONOMICS (Y2-3 model)

**Per pet-brand SMB customer:**
- ACV: $5,000/year average (mix of $2k-$25k tiers)
- Gross margin: 85%+ (Cloud Run + Gemini API + minor vet/contract costs)
- CAC: $200-800 via founder-led outbound + Shopify App Store + content marketing
- Payback: <3 months
- Net retention: 120-140% (claim surface grows, impressions grow, AI agent query volume grows)

**Per enterprise retailer/insurer:**
- ACV: $1M average
- Gross margin: 90%+ (mostly platform fee, low marginal cost)
- CAC: $50-150k (founder-led 6-month sales cycle)
- Payback: <2 months
- Net retention: 110%+ (catalog grows, query volume grows)

**Per per-impression / per-query metered call:**
- Marginal cost: $0.0001 (BioMCP + Gemini Flash routing)
- Marginal revenue: $0.0005-$0.01
- Gross margin: 80-99%

**Aggregate Y3 model (illustrative):**
- 250 SMB brands × $5k = $1.25M
- 50 mid brands × $50k = $2.5M
- 3 retailer platforms × $1M = $3M
- 2 insurer platforms × $1M = $2M
- 10 human-supplement brands × $50k = $500k
- Metered impressions/queries cross-brand = $1M
- Protocol governance + grants = $250k
- **Total ~$10M ARR Y3 base case, $20-30M ARR Y3 high case**

---

## COMPETITIVE LANDSCAPE — incumbents + adjacent + AI-future

### Direct incumbents (pet supplement substantiation specifically)
- **NASC (National Animal Supplement Council)** — quality seal for manufacturing GMP + adverse-event reporting + label compliance. ~300 member brands. ~$5-15k/year/brand. **Critical: NASC does NOT verify clinical efficacy or endorsement claims.** They're complementary, not competitive. We should partner via a co-authored technical bulletin "Acceptable digital substantiation formats."
- **In-house compliance teams** at larger brands (Nutramax, VetriScience, Zesty Paws after acquisition). $200-500k/year fully-loaded. We give them better tools.
- **Outside vet consultants writing substantiation memos.** $200/hour, static PDFs, no continuous monitoring, not AI-callable. We replace this with structured, signed, queryable infra.
- **"Do nothing."** The dominant competitor today. Most DTC brands have NO substantiation system. The plaintiff bar is what creates the buy.

### Adjacent trust/verification infra
- **Trustpilot ($2B mkt cap)** — consumer reviews. Different layer. No claim verification, no AI-agent-callable.
- **Truepic (~$150M)** — C2PA-aligned image provenance. Different vertical (images, not claims). Founding member of C2PA. **A potential acquirer.**
- **NSF International, USP, ConsumerLab** — third-party testing labs. Slow (weeks), human-driven, $200-1500/test, not AI-callable. Adjacent but not competitive.
- **Labdoor** — consumer-facing supplement ratings. B2C, not B2B substantiation infra.
- **C2PA** — open standard, Adobe-led, image provenance. **Architectural inspiration, not competitor.** We model PCEC after C2PA's governance.

### Compliance-infra incumbents (SaaS-vertical)
- **Vanta ($2.5B)** — SOC2/ISO/HIPAA compliance for SaaS. Different vertical (B2B SaaS, not consumer goods). Adjacent model, different surface. **Real risk: Vanta could extend to consumer products in 2-3 years.** Defense: standards-body moat moves first.
- **Drata, Secureframe** — same.
- **OneTrust ($5B+)** — privacy compliance (GDPR, CCPA). Different vertical. Less likely to pivot.
- **AssurX, TrackWise, MasterControl, EtQ Reliance, ETQ Compliance** — quality management for FDA-regulated manufacturers (pharma, medical devices). Heavy enterprise. Not consumer DTC.

### AI-agent infra
- **No one is building "trust oracle for AI commerce agents" yet.** This is the white space. LangChain, Arize, WhyLabs, HuggingFace — all adjacent but none doing claim verification.
- **A2A protocol itself** (Linux Foundation, donated by Google April 2026) — we plug into it; we don't compete with it.

### Future entrants (24-36 month risk)
- **Vanta extending to consumer products** — possible, slow. Defense: PCEC standards governance + regulator endorsement.
- **Truepic extending from images to claims** — possible. Defense: PCEC as a separate spec, partnership-friendly.
- **A LLM lab building agent identity** (Anthropic, OpenAI Operator team) — competes on the AI-agent-callable layer, not the human-readable cert layer. Both layers needed.
- **Big-3 consultancies (Deloitte, EY, KPMG)** — already do substantiation memos as services. Not productized. Could partner with us as channel.

**Defensive strategy:** ship PCEC v0.1 in 18 days, sign first 3 founding members in 90 days, donate to Linux Foundation in 12 months. By the time Vanta notices, the standard has 12+ members and 3 regulator endorsements. Game over for fast-followers.

---

## THE MOAT — three layers compounding

1. **The standard (PCEC governance).** Owning the spec the way Adobe owns C2PA, Stripe co-owns OpenID Connect for commerce, Plaid shaped Open Banking. Standards-body chair seats are not for sale; they're earned by first-mover credibility + reference implementation depth. We become the canonical answer; Vanta/Truepic/anyone else has to fork or adopt.

2. **The claim-to-evidence graph.** Every signed claim links to: source papers (PMID), expert DIDs, SKUs, brands, withdrawal events, conversion lift, AI-agent query patterns. After 12 months across 5,000 SKUs and 500 vet/MD DIDs, no entrant can replicate without re-soliciting every signature and re-grading every paper. **This is Plaid's aggregator-token equivalent.**

3. **Agent-default integration depth.** When Rufus/Operator/Perplexity/Gemini Shopping default to calling `verify_claim` on our public A2A endpoint because (a) we shipped first, (b) the protocol is open, (c) the brand catalog is on us, displacing us requires coordinated migration of N AI agents + M brands + K regulators. That's the Stripe/Twilio/Visa lock-in.

Each layer compounds the others. Standard credibility makes brand adoption easier → brand adoption grows the data graph → data graph makes AI-agent integration the obvious choice → AI agent depth makes standard governance unkillable. Flywheel.

---

## GO-TO-MARKET (year by year)

### Year 0 — Hackathon (May-June 2026)
- Submit PawConscious Mesh to GFS hackathon by June 5
- PCEC v0.1 draft published as open spec on GitHub
- Public A2A endpoint live with ShopperAgent reference consumer
- Build content: "How Cosequin's $11.5M settlement happened and what changed" + "What an AI shopping agent will need from your PDP by 2027"

### Year 1 H1 (June-Dec 2026)
- 10 pet supplement brand pilots (Native Pet, Honest Paws, Fera Pets, Finn, Pet Honesty, Front of the Pack, Wholistic Pet Organics + 3 others)
- Open Shopify App Store listing (PawConscious badge)
- Cold outbound to plaintiff-targeted brands (use Topclassactions.com docket as lead list)
- NASC conversation opens
- PCEC v0.1 → v0.2 with 2-3 founding-member inputs

### Year 1 H2 (Jan-June 2027)
- 50 paying pet brands ($250k ARR)
- First retailer pilot (Chewy or Petco vendor onboarding integration)
- First insurer pilot (Trupanion claims-fraud feed)
- Co-authored NASC technical bulletin published
- Series A: $5-10M at $30-50M post

### Year 2 (mid-2027 to mid-2028)
- 200 pet brands + 1 enterprise retailer + 1 insurer = $2-4M ARR
- Launch human supplement vertical (chondroitin overlap)
- 10 human supplement brand pilots
- PCEC v0.3 with 6 founding members signed; Linux Foundation conversation
- First AI shopping platform integration (Perplexity Shopping or Operator)

### Year 3 (mid-2028 to mid-2029)
- $15-30M ARR
- Launch beauty vertical (FDA-light, FTC-heavy)
- PCEC donation to Linux Foundation
- First regulator endorsement (likely NY AG or FTC ESI Lab)
- Series B: $25-50M at $200-400M post

### Year 4-5
- $80-200M ARR
- Functional food + wellness device + athletic verticals open
- Multiple regulator integrations
- AI-agent ecosystem default routing
- M&A interest: Verisign, Persona, Truepic, Adobe, DigiCert, S&P Global

---

## RISKS + FAILURE MODES (CEO-review section)

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Vanta/OneTrust pivot to consumer products | Med (2-3 yr) | High | Standards-body governance first; donate spec to LF in 12mo |
| Truepic extends from images to claims | Low | Med | Partner-friendly architecture; potential acquirer not competitor |
| AI shopping agents fizzle / take longer than expected | Med | Med | Business survives on brand/retailer/insurer revenue without AI-agent layer; AI layer is upside |
| Pet vertical doesn't generate enough proof to expand | Low | High | 18-day hackathon → pilots in Q3 → if no pilot traction by Q4 2026, reassess |
| Plaintiff bar over-discounts ACP cert ("just self-serving") | Med | High | Founding members include outside experts (vet schools, law firms); audit chain is cryptographically attested |
| Brand churn after first cert issued ("we're fixed now") | High | High | 12 reasons in §"Why Brands Keep Paying" — must explicitly demonstrate retention in pilot data by Q4 2026 |
| Gemini 3 / ADK / A2A protocol shifts breaking our stack | Low | Med | Stay close to Google releases; maintain alternative backends (Anthropic/OpenAI/OSS) for non-hackathon production |
| Cosequin-type catalyst doesn't repeat (plaintiff bar moves to other category) | Med | Med | Catalyst is multiplied by AI commerce platform shift; doesn't require continuous plaintiff news |
| Regulator picks a different standard | Med | High | Get to regulator FIRST. NY AG + FTC ESI Lab are achievable Y1-2 targets. |
| Solo founder burnout | High | Critical | Hire technical co-founder by Y1 H2 with seed funds |
| GFS hackathon doesn't pick us | Med | Low for biz, Med for narrative | Submission still produces working public infra + open spec; momentum continues even without award |
| Cloud spend runs over budget | Low | Med | Cloud Run scales to 0; Vertex AI billed per-use; cap Gemini 3 Pro to demo windows |

---

## 5-YEAR ARC

```
2026 — Hackathon submission. PCEC v0.1 open spec. PawConscious Mesh live.
       10 pilot pet brands. $250k ARR. Founder solo, MIT advisor network.

2027 — Series A. $5-10M raised. Co-founder hired. Human supplement vertical opens.
       50 paying pet brands + 1 retailer + 1 insurer. NASC bulletin co-authored.
       6 PCEC founding members. $2-4M ARR.

2028 — Series B. $25-50M raised. Beauty + functional food verticals.
       PCEC donated to Linux Foundation. First regulator endorsement.
       First AI shopping platform integration (Perplexity Shopping likely first).
       $15-30M ARR.

2029 — Cross-vertical infrastructure. Devices + athletic + wellness verticals.
       AI shopping default routing live across 3+ platforms. $80-150M ARR.
       Series C consideration vs strategic partnership with Verisign/Truepic/Adobe.

2030 — Acquisition path opens at $1.5-4B (10-15x ARR for protocol infra comps).
       OR continue independent toward S-1 (>$300M ARR threshold).
```

---

## VALIDATION MILESTONES (per /plan-ceo-review test section)

| Milestone | Date | Pass/fail signal |
|---|---|---|
| Hackathon submission live | June 5, 2026 | Devpost listing + public A2A endpoint + ShopperAgent calls + open spec |
| First 3 paying brand pilots | Aug 31, 2026 | $15-30k contract value, signed via Shopify App Store or direct |
| First retention proof | Dec 31, 2026 | Y1 cohort still paying + claim surface grew |
| Co-authored NASC bulletin | March 31, 2027 | Published doc with NASC byline |
| First retailer pilot | June 30, 2027 | $100-500k contract with Chewy/Petco/Amazon Pet |
| First insurer pilot | Sep 30, 2027 | $250k-1M contract with Trupanion/Nationwide/MetLife Pet |
| First human-vertical brand | Dec 31, 2027 | $25-50k contract value, ingredient overlap path validated |
| PCEC v0.3 with 6 founding members | June 30, 2028 | Public commitments + standards-body activity |
| First regulator endorsement | Dec 31, 2028 | NY AG / FTC ESI Lab / FDA-CVM public reference |

If any 2 consecutive milestones miss by >90 days, trigger reassessment.

---

## HACKATHON STRATEGY (specific to GFS June 5 deadline)

**The hackathon submission frames ACP as a thesis being PROVEN by PawConscious Mesh, not as PawConscious Mesh standalone.**

Devpost description structure:
1. Hook: "Pet supplements ship $11.5M class actions because there's no audit trail. AI shopping agents will arrive before regulators fix this. ACP is the verifiable claim infrastructure both sides need."
2. What we built: working multi-agent A2A mesh on Google Cloud, real PubMed citations, signed certs, public A2A endpoint with external ShopperAgent consumer
3. The protocol: PCEC v0.1 published as draft open spec
4. The vertical proof: PawConscious Mesh production-running on real pet supplement PDPs
5. The Google stack: ADK 2.0 + Gemini 3 Pro + Vertex Agent Engine + Vertex AI Search + Cloud Run + A2A v0.3 + BioMCP + MCP
6. The future: pet today, every consumer vertical tomorrow, AI commerce trust pipes when agents take over discovery

This frames us as **infrastructure builders, not app builders.** Judges from Google have spent 18 months pushing ADK + A2A. They reward submissions that demonstrate platform-shift readiness. ACP is that.

---

## FOUNDER + WHY-ME

Omar Dominguez. MIT MBA 2026. Engineer by training. Built PawConscious (live, paying-customer-adjacent) + GUARDIAN (Google for Startups hackathon prep, full multi-agent A2A architecture v3-v9) + O22 (Veo cinematic pipeline). Multiple hackathon wins including PawConscious first-place at Subconscious 2026-05-13. Solo founder of AgentsArmy.

Unique advantages:
- Already built the agentic A2A architecture in GUARDIAN — 6 weeks of code that ports directly to ACP
- Already have a live pet brand (PawConscious) + Boston vet network drafted
- Already have Google Cloud credits + GFS hackathon access
- Already have O22 cinematic pipeline for demo + sales collateral
- MIT MBA network for go-to-market + Series A introductions
- Track record of compressing 12-day plans into 1.3 calendar days when needed (GUARDIAN D1-D15 in <2 days)

---

## FUNDING PATH

| Round | Size | Valuation | Use of funds | Timing |
|---|---|---|---|---|
| Pre-seed (current) | Self-funded + GFS credits | n/a | Hackathon ship + first 3 pilots | now |
| Seed | $1-2M | $8-15M post | Hire 1 eng + 1 GTM, 10 pilots | Q4 2026 |
| Series A | $5-10M | $30-50M post | Scale to 200 brands + 1 retailer + 1 insurer | Q2 2027 |
| Series B | $25-50M | $200-400M post | Cross-vertical expansion + AI-agent integrations | Q4 2028 |
| Series C / strategic | $50-150M | $1-2B post | Geographic expansion, M&A bolt-ons | 2030 |

Investor archetype: enterprise infra investors who get standards-as-moat (a16z infra, Index, Greylock, USV). NOT pet-vertical investors.

---

## OPEN QUESTIONS FOR CODEX G7.2

1. Is the retention story (12 reasons) credible enough that pilots will demonstrate it in Q3-Q4 2026, or is "brands fix and leave" still the dominant risk?
2. Does the Vanta comp ($2.5B for B2B SaaS compliance) translate cleanly to consumer-products compliance, or are the buyer dynamics structurally different in ways that compress TAM?
3. Is the AI-shopping-agent platform shift the load-bearing assumption? If Rufus/Operator/Perplexity Shopping don't take off by 2028, what's the fallback narrative that still gets us to $100M ARR?
4. Is "regulator endorsement" achievable in 24-30 months realistically, or is that a 5-year project that we're front-loading?
5. Does PCEC have a real chance of being adopted as a standard, or is "standards body moat" a vanity goal a solo founder can't pull off?
6. Should PawConscious stay the brand or should we adopt an ACP-parent name from day 1?
7. What's missing from this plan that a $50M Series A investor would immediately flag?

---

## RELATED DOCS
- `PLAN.md` — engineering roadmap (18-day hackathon execution)
- `docs/PCEC-v0.md` — draft protocol spec
- `docs/A2A-AGENT-CARD.md` — public A2A agent card design
- `docs/ARCHITECTURE.md` — system architecture
- `reviews/codex-G7-verdict.txt` — codex first-round critique (absorbed)
- `archive/PLAN_v1_unvalidated.md` — preserved for lineage
