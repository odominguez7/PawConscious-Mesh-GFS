# ACP — Disciplined Business Doc

**Built post codex G7.2 BLOCK (absorbed in this doc). Date 2026-05-18. Status PROPOSED → pending codex G7.3 + Omar sign-off.**

This is the MIT-Aulet × Osterwalder × Google-ecosystem-native discipline layer on top of `BUSINESS_PLAN.md`. It is the doc you hand a Series A investor, the doc that survives YC partner review, and the doc that maps every claim back to a validation experiment.

---

## CRITICAL PIVOT (codex G7.2 absorbed)

**Before G7.2:** ACP is the verifiable claim infrastructure that *certifies* product claims.
**After G7.2:** ACP is the verifiable claim infrastructure that *powers accredited certifiers*. NSF / NASC / USP / state-licensed-vet-network keep the certifying authority and the E&O insurance and the ISO 17065/17025 accreditation. ACP gives them the agentic evidence engine that makes their cert 10× faster and 100× cheaper to issue.

Stripe doesn't issue credit cards. Visa and Mastercard do. Stripe is the rails. ACP is the rails. NASC is the Visa.

| Pre-pivot | Post-pivot |
|---|---|
| ACP signs certs as authority | NASC / NSF / partner vet body signs; ACP signs the agentic evidence bundle that backs it |
| Liability = ACP's | Liability = accredited certifier's; ACP carries E&O only on infra correctness |
| Compete with NASC | Partner with NASC (channel + co-branded cert) |
| "Regulator-grade" requires our accreditation (ISO 17065/17025, 12-18mo project) | "Regulator-grade" inherited from partner certifier; ACP's claim is "infrastructure that powers accredited certifiers" |
| Sales = brand → ACP | Sales = brand → accredited certifier (NASC, etc.) → ACP under the hood, OR brand → ACP-as-infra channel for the certifier |
| TAM compressed to "we replace certifiers" (impossible) | TAM expanded to "every cert issued by anyone uses our rails" (Stripe-like) |
| Series A red flag: liability + accreditation | Series A green: standard infra play with regulated-partner channel |

**Re-engineering effect:** PawConscious Mesh becomes "ACP for Pet — co-branded with NASC and a vet-school panel (Tufts Cummings target)." The vet panel attests; NASC accredits; ACP makes the evidence machine-readable and continuous.

This is the single most important change. Every other amendment below derives from it.

---

## NORTHSTAR v3 (sharpened)

**Every claim made on a commerce surface — about ingredients, efficacy, expertise, provenance, safety, or performance — becomes machine-verifiable evidence that any accredited certifier can sign, any AI agent can query, and any regulator can audit. ACP is the infrastructure. Accredited bodies are the trust faces. Pet is the proving ground.**

---

## BUSINESS MODEL CANVAS (post-G7.2)

```
┌────────────────────────────────────┬────────────────────────────────────┬────────────────────────────────────┐
│ KEY PARTNERS                       │ KEY ACTIVITIES                     │ VALUE PROPOSITIONS                 │
│                                    │                                    │                                    │
│ • NASC (channel + accredited       │ • Run the multi-agent evidence     │ For BRANDS:                        │
│   certifier of record for pet)     │   engine on Google Cloud           │ • Continuous, machine-verifiable   │
│ • Tufts Cummings / Cornell /       │ • Maintain BioMCP, AI2 Asta,       │   substantiation that survives     │
│   UPenn vet schools (vet panel,    │   Firecrawl integrations           │   plaintiff discovery              │
│   academic credibility)            │ • Operate the public A2A endpoint  │ • Accredited-certifier-backed cert │
│ • Google (Cloud, ADK, Gemini,      │ • Steward PCEC draft proposal +    │   without in-house compliance hire │
│   A2A protocol, Marketplace)       │   coalition                        │ • Re-issuance auto-triggered on    │
│ • Shopify / Akeneo / Klaviyo /     │ • Standards governance ops         │   science/regulator/plaintiff diff │
│   Recharge (commerce-surface       │ • Audit-trail QA + appeals process │                                    │
│   integrations)                    │ • Renewal + retention ops          │ For CERTIFIERS (NASC, NSF, USP):   │
│ • Law firms (Kelley Drye,          │                                    │ • 10× faster cert issuance         │
│   Venable, Hogan Lovells) for      │                                    │ • Continuous re-verification        │
│   FTC ad-law positioning           │                                    │   without manual re-audit          │
│ • Accredited testing labs (NSF)    │                                    │ • Machine-readable evidence bundle │
│ • Insurers (Trupanion etc) for     │                                    │   that AI agents and regulators    │
│   claims-fraud feed in Y2-3        │                                    │   can query                        │
│                                    │                                    │                                    │
│                                    ├────────────────────────────────────┤ For AI SHOPPING AGENTS:            │
│                                    │ KEY RESOURCES                      │ • Free callable trust oracle       │
│                                    │                                    │ • A2A v0.3-compatible              │
│                                    │ • PCEC draft spec authorship +     │ • Real evidence, not vibes         │
│                                    │   coalition seats                  │                                    │
│                                    │ • Claim-to-evidence graph          │ For REGULATORS:                    │
│                                    │ • Vet/MD/expert DID network        │ • Standardized evidence-bundle     │
│                                    │ • Google Cloud infra credits       │   format for case files            │
│                                    │ • Founder reputation + MIT MBA     │ • Free reference impl              │
│                                    │   network                          │                                    │
│                                    │ • GUARDIAN / PawConscious /        │                                    │
│                                    │   O22 salvageable code             │                                    │
│                                    │                                    │                                    │
├────────────────────────────────────┴────────────────────────────────────┼────────────────────────────────────┤
│ CUSTOMER RELATIONSHIPS                                                    │ CUSTOMER SEGMENTS                  │
│                                                                           │                                    │
│ • Self-serve metered (SMB brands via Shopify App Store)                  │ Y1 H1:                             │
│ • Founder-led concierge (mid-market brands; 4-6 week sales cycle)        │ • Pet supplement brands SMB        │
│ • Enterprise sales (retailer/insurer; 6-12mo cycle, Y2+)                 │   ($1-10M ARR)                     │
│ • Coalition governance (PCEC founding members + LF observers)            │ • Pet supplement brands mid        │
│ • Free API + community (AI agent builders)                               │   ($10-50M ARR)                    │
│ • Regulator office hours (free advisory, build relationship pre-pilot)   │                                    │
│                                                                           │ Y2 H2 - Y3:                        │
├──────────────────────────────────────────────────────────────────────────┤ • NASC member brands (~300)        │
│ CHANNELS                                                                  │   via NASC co-brand               │
│                                                                           │ • Pet retailers (Chewy, Petco,     │
│ • Shopify App Store (PawConscious Mesh listing)                          │   Amazon Pet, Faire)               │
│ • Founder-led plaintiff-docket outbound                                  │ • Pet insurers (Trupanion,         │
│ • NASC channel partnership (300 audited member brands)                   │   Nationwide, MetLife Pet)         │
│ • Content marketing (canonical site for plaintiff dockets +              │                                    │
│   FTC §255 + AAFCO updates)                                              │ Y3+:                               │
│ • Conferences (Global Pet Expo Mar, SuperZoo Aug)                        │ • Human supplement brands          │
│ • A2A protocol discovery (when LF publishes registry)                    │   (chondroitin / omega-3 overlap)  │
│ • Vet school partnerships (Tufts/Cornell/UPenn)                          │ • AI shopping platforms            │
│ • Google Cloud co-marketing (post-hackathon-win path)                    │   (Perplexity Shopping first)      │
│                                                                           │ • Regulators (NY AG, CA AG,        │
│                                                                           │   FTC ESI Lab — "usage" not        │
│                                                                           │   endorsement per G7.2)            │
│                                                                           │ • Pharma white-label (Y4+)         │
├──────────────────────────────────────────────────────────────────────────┴────────────────────────────────────┤
│ COST STRUCTURE                              │ REVENUE STREAMS                                                  │
│                                             │                                                                  │
│ Marginal cost per cert:                     │ Hackathon-period pricing (SIMPLIFIED per G7.2 P0.2):            │
│ • Gemini 3 Pro reasoning: $0.02             │ • Free tier: 1 cert / 90 days (top-of-funnel for SMB brands)    │
│ • Gemini 2.5 Flash routing+audit: $0.005    │ • Starter: $99/mo per brand (5 active SKUs, monitoring on)      │
│ • BioMCP + AI2 Asta API: $0.001             │ • Pro: $499/mo per brand (25 active SKUs, vet attestations,     │
│ • Vertex AI Search: $0.02                   │   priority re-verification, audit-grade PDF export)             │
│ • Firestore + BigQuery + Cloud SQL: $0.10   │ • Enterprise (Y2+): platform fees $250k-$2M/yr (retailers,      │
│ • Cloud Run: ~$0                            │   insurers, NASC co-brand, certifier white-label)              │
│ • Vet/MD attestation time (per cert): $80   │                                                                  │
│   (NASC-aligned vet network, ~$200/hr,      │ Year 2 add (after retention proven):                            │
│   ~25 min per cert with agent assist)       │ • Metered AI-agent query (only if brand opts in): per-query    │
│ • Legal review periodic: ~$200/quarter      │   pricing $0.001-0.01 (NOT per-impression — G7.2 P0.2)         │
│   amortized per customer                    │                                                                  │
│ • Insurance (E&O, infra correctness only):  │ Year 3 add:                                                     │
│   ~$50/customer/year amortized              │ • White-label certifier infra (NSF, NASC, USP): $250k-2M one-   │
│                                             │   time + 15-20% rev share                                       │
│ Total marginal per cert ≈ $80               │ • Standards governance LF Steering Member fees: $50-250k/yr     │
│ Total annual fixed per Pro tier brand ≈     │                                                                  │
│ $260 (insurance + legal + onboarding)        │ NOT in base case (G7.2 P1.4 — removed):                         │
│                                             │ • Pharma data licensing (too speculative)                       │
│ Founder + ops: $0 (pre-seed self-funded     │ • Per-impression billing (won't be accepted by SMB pilots)      │
│   through Y1 H1)                            │                                                                  │
│ Post-seed (Y1 H2 onward): +1 eng, +1 GTM    │                                                                  │
│ → ~$30k/mo fixed                            │                                                                  │
└─────────────────────────────────────────────┴──────────────────────────────────────────────────────────────────┘
```

---

## MIT DE 24 STEPS — full walkthrough with status

| # | Step | Status | What we have / what's TODO |
|---|---|---|---|
| 1 | Market Segmentation | ✅ DONE | 12 candidate verticals considered (pet supplements, human supplements, beauty, functional food, devices, athletic, baby, eco, regulatory disclosure, AI commerce trust). Selection rationale documented. |
| 2 | Beachhead Market Selection | ✅ DONE | US DTC pet supplement brands $1-50M ARR with active SKUs carrying health claims. Plaintiff-pressure subset. |
| 3 | Build End User Profile | 🟡 PARTIAL | CMO / Head of Compliance / General Counsel. Need to deepen demographics + psychographics (age, role-tenure, prior compliance background, content sources). |
| 4 | Calculate TAM | ✅ DONE | Beachhead: 200 brands × $6k avg = $1.2M ceiling. Pet vertical: $3-5M ARR cap as standalone. Cross-vertical: $50B+. |
| 5 | Profile the Persona | ❌ TODO | Write "Sarah, Head of Compliance, $25M ARR pet supplement DTC brand, 3 yrs in role, ex-Nutramax, panicking after Cosequin settlement" archetype document. |
| 6 | Full Life Cycle Use Case | 🟡 PARTIAL | Discovery → first cert → embed badge → monitoring → renewal → expansion to new SKU. Map exists; need to time each step in production data. |
| 7 | High-Level Product Spec | ✅ DONE | 5 ADK agents, PCEC draft schema, A2A v0.3 endpoint, embed JS, monitoring webhooks. See `docs/ARCHITECTURE.md`. |
| 8 | Quantified Value Proposition | ❌ TODO (G7.2 flag) | "ACP saves brand $X in plaintiff exposure (basis: avg Cosequin-class $5M settlement / 200 exposed brands = $25k/brand expected value at 1% probability) + $Y in compliance team time (8 hrs/cert × $150/hr × 12 certs = $14.4k/yr) + $Z in retailer onboarding cycle (2-week delay × $50k/wk lost wholesale = $100k saved). Total = $139k expected value vs $1.2-6k/yr cost = 20-100× value capture ratio." |
| 9 | Identify Next 10 Customers | ❌ TODO | Build named list: Native Pet, Honest Paws, Fera Pets, Finn, Pet Honesty, Front of the Pack, Wholistic Pet Organics, Pro Plan Vet Direct, Spot Farm, Open Farm. Find each compliance/GC contact. |
| 10 | Define Your Core | ✅ DONE (post-G7.2) | PCEC spec coalition + claim-to-evidence graph + agent-default integration depth + ACCREDITED-CERTIFIER PARTNERSHIP CHANNEL (new core post-pivot). |
| 11 | Chart Competitive Position | ✅ DONE | See `BUSINESS_PLAN.md` §"Competitive Landscape". |
| 12 | Determine the DMU | ❌ TODO | Champion: Head of Compliance. Economic buyer: GC (under $50M) or CMO (under $10M). End user: marketing/legal team. Influencers: NASC, outside vet consultants, brand legal counsel. Gatekeeper: procurement (mid+). |
| 13 | Map Process to Acquire a Paying Customer | ❌ TODO | Discovery (Shopify App Store organic + plaintiff-docket outbound) → trial (free 1-cert) → first cert (Starter $99/mo) → expansion (Pro $499/mo) → renewal cycle aligned with NASC biennial audit. Document specific touchpoint flow. |
| 14 | Calculate TAM of Follow-On Markets | ✅ DONE | Human supplements $60B, beauty $90B, functional food $300B, devices $100B, athletic $50B. See `BUSINESS_PLAN.md`. |
| 15 | Design a Business Model | ✅ DONE | BMC above + simplified per-cert + monitoring tier + enterprise contracts. |
| 16 | Set Your Pricing Framework | ✅ DONE | Free → $99/mo → $499/mo → Enterprise. Per-AI-agent-query opt-in Y2. |
| 17 | Calculate the LTV of an Acquired Customer | 🟡 PARTIAL → tightened below | See CAC:LTV section. |
| 18 | Map the Sales Process | 🟡 PARTIAL → tightened below | See Funnel section. |
| 19 | Calculate the CAC | 🟡 PARTIAL → tightened below | See CAC:LTV section. |
| 20 | Identify Key Assumptions | ✅ DONE | Top 5: (a) plaintiff catalyst sustains buying urgency, (b) accredited-certifier partnership materializes (NASC), (c) brands accept ongoing monitoring vs one-time cert, (d) Google A2A becomes default for at least 1 AI shopping agent, (e) solo founder can ship pilot in 18 days. |
| 21 | Test Key Assumptions | ❌ TODO → mapped to 6 experiments below | See "Dogs Eat The Food" section. |
| 22 | Define the MVBP | ✅ DONE-ISH | Hackathon submission IS the MVBP for pet. Add: pricing page live, Shopify App Store listing scaffold. |
| 23 | Show That Dogs Will Eat the Dog Food | ❌ TODO → 3 paying pet brands by Q4 2026 | Validation gate. |
| 24 | Develop a Product Plan | ✅ DONE | See `PLAN.md`. |

**Score: 11 DONE / 6 PARTIAL / 7 TODO out of 24.** Of the 7 TODO, 4 are hackathon-blocking (5, 8, 9, 12) — must be drafted in repo before D1. The other 3 (13, 18, 19) are tightened below.

---

## CAC:LTV per buyer tier (with G7.2 cost amendments)

Codex G7.2 P0.4: prior unit economics ignored expert time, legal review, insurance. Adding now.

### Tier 1: Pet brand SMB ($1-10M ARR, Starter $99/mo or Pro $499/mo)

| Metric | Value | Source |
|---|---|---|
| ACV avg | $3,000/yr (mix of Starter 60% + Pro 40%) | Pricing model |
| Marginal cost per cert | $80 (Google APIs $4 + vet attestation $80 - amortized $4) | Cost structure above |
| Annual marginal cost per brand | $240 (3 certs avg × $80) | |
| Annual fixed cost per brand | $260 (insurance E&O + legal review amortization + onboarding) | |
| Gross margin per brand | ~83% | $3k - $500 / $3k |
| Channel mix | 40% Shopify App Store organic + 30% plaintiff-docket outbound + 20% NASC referral + 10% content/SEO | |
| CAC (blended) | ~$500 (founder time $300 + Shopify listing fee + light paid acquisition $200) | |
| Payback | 2-3 months | |
| Gross churn (annual) | 10-15% (Y1 cohort, will improve) | Industry typical SaaS |
| Net retention | 110-130% (expansion via more SKUs + Pro tier upgrade) | If retention story holds |
| 5-yr LTV (Pro upgrade path) | $12-18k | Discounted cash flow |
| **LTV:CAC** | **24-36×** | Healthy by infra benchmark (3:1+) |

### Tier 2: Pet brand Mid ($10-50M ARR)

| Metric | Value |
|---|---|
| ACV avg | $25,000/yr (Pro + add-ons + light enterprise feature unlock) |
| Annual marginal cost | $480 (6 certs × $80) |
| Annual fixed cost | $1,500 (more expert time, dedicated CSM-light) |
| Gross margin | ~92% |
| CAC | $5,000-$10,000 (founder-led 6-week sales cycle, conference + intro) |
| Payback | 3-5 months |
| Net retention | 115-125% (more SKUs + vet-attestation premium + retailer-requested upgrades) |
| 5-yr LTV | $90-130k |
| **LTV:CAC** | **15-25×** |

### Tier 3: Pet retailer (Chewy, Petco, Amazon Pet, Faire — Y2+)

| Metric | Value |
|---|---|
| ACV avg | $1,000,000/yr (catalog-level platform fee) |
| Annual marginal cost | $20,000 (bulk verification, vet panel ops) |
| Annual fixed cost | $50,000 (dedicated CSM + dedicated infra + procurement responses) |
| Gross margin | ~93% |
| CAC | $75,000-$150,000 (6-12 month enterprise sales cycle, founder + CTO-level support, conference circuit) |
| Payback | 1-2 months once closed |
| Net retention | 110-115% (catalog grows, query volume grows) |
| 5-yr LTV | $6-8M |
| **LTV:CAC** | **40-80×** |

### Tier 4: Pet insurer (Trupanion etc — Y2-3)

Similar to retailer. ACV $500k-$2M. LTV:CAC 30-60×.

### Aggregate model: realistic vs aggressive

| Scenario | Y3 ARR | Brand count | Enterprise count | Notes |
|---|---|---|---|---|
| **Aggressive (BUSINESS_PLAN base case)** | $15-30M | 250 SMB + 50 mid | 3 retailers + 2 insurers | Requires all assumptions firing |
| **Realistic (G7.2-adjusted)** | $6-10M | 200 SMB + 30 mid | 1 retailer pilot + 1 insurer pilot | Most assumptions fire; AI-agent metering off; human vertical pushed to Y3 H2 |
| **Conservative (G7.2 fallback)** | $3-5M | 150 SMB + 10 mid | 0 enterprise yet, just LOIs | Plaintiff catalyst fades; retention proves to 110% not 130% |

**Series A target ARR: $2-4M at $30-50M post.** Realistic scenario clears this; conservative scenario clears narrowly.

---

## BEACHHEAD MARKET (Aulet step 3, sharpened)

> **The brand at the center of this beachhead is:**
> US DTC pet supplement company, $1M-$50M ARR, with at least one product carrying a health claim, that has either (a) received a plaintiff demand letter or notice of intent to sue in last 12 months, (b) been asked for substantiation by Chewy/Petco/Amazon Pet vendor management in last 6 months, or (c) launched a new SKU in last 90 days. The compliance work currently sits with the General Counsel or Head of Compliance, who has no dedicated tooling and relies on outside vet consultants ($200/hr) writing static PDFs.

Triangulated count: **150-300 brands.** Top 50 known by name:

Native Pet, Honest Paws, Fera Pets, Finn, Pet Honesty, Front of the Pack, Wholistic Pet Organics, VetriScience, Nutramax, Spot Farm, Open Farm, The Honest Kitchen, Stella & Chewy's, Primal Pet Foods, Steve's Real Food, ZIWI, Vital Essentials, Earth Animal, Pet Wellness Labs, Zesty Paws, Rover.com brands, Chewy private label, Petco WholeHearted, Wellness Pet, PetMD, Pet Releaf, Nutri-Vet, Vet's Best, Tomlyn, Naturpet, Earth Buddy, King Kanine, Dr. Mercola Pets, Susan G Komen Pet (charity-adjacent), Plato Pet Treats, Wellness Concepts, Diamond V, Bayer Animal Health DTC line, MyCabin, Better Choice, Animals Like Us, Lord Jameson, Bear & Lion, Polkadog, Bone Appetit, BareBones, BlackwoodPet, NutriSource, Solid Gold, Acana...

**Pilot-target shortlist (first 10):** Native Pet, Honest Paws, Fera Pets, Finn, Pet Honesty, Front of the Pack, Wholistic Pet Organics, Open Farm, Earth Animal, Pet Wellness Labs. Reasoning: all DTC-native, all in $1-25M ARR band, all have prominent health claims on PDPs (joint, calm, immune, gut).

---

## UNIT ECONOMICS — deep dive (post-G7.2 amendments)

Per SMB customer (Pro tier $499/mo):

| Line | Annual amount | Notes |
|---|---|---|
| Revenue | $5,988 | |
| Marginal: Google APIs (Gemini + BigQuery + Search + Run) | $50 | 6 certs × ~$8 each |
| Marginal: BioMCP + AI2 Asta API | $20 | Per-cert + monitoring |
| Marginal: vet attestation time | $480 | 6 certs × $80 (vet ~25min × $200/hr) |
| Fixed: E&O insurance amortized | $50 | $50k policy / 1000 customers |
| Fixed: legal review amortized | $150 | Quarterly review × per-customer share |
| Fixed: onboarding (one-time annualized) | $60 | 1 hr founder time × $200/hr |
| **Total cost** | **$810** | |
| **Gross profit per customer** | **$5,178** | |
| **Gross margin** | **86%** | (was 99% pre-G7.2 — G7.2 P0.4 corrected) |

Customer-level economics still strong. Margin compression from 99% to 86% is honest cost accounting, not red flag.

---

## HOW TO FEED THE FUNNEL (10 demand-gen mechanics)

| # | Mechanic | First step | Cost | Quality of lead |
|---|---|---|---|---|
| 1 | Shopify App Store listing | Submit `PawConscious Mesh` app D17 | $99/yr Shopify fee | High intent (brand search) |
| 2 | Plaintiff-docket outbound | Scrape Topclassactions.com weekly; LinkedIn the brand GC | Founder time | Very high intent |
| 3 | Content marketing | Weekly post on plaintiff dockets + regulator updates | Founder time + AI writing | Medium intent, builds authority |
| 4 | NASC channel partnership | Email NASC ED (Bill Bookout) D5; pitch co-authored bulletin | Founder time | Very high intent (audited members) |
| 5 | Vet school partnerships | Tufts Cummings + Cornell + UPenn cold intro Q3 2026 | Founder time + MBA network | Medium intent (long-term) |
| 6 | A2A protocol registry | Submit to LF A2A registry D20 | Free | Inbound only |
| 7 | AI shopping agent outreach | Cold intro Perplexity Shopping (most open) D30 | Founder time | Speculative but free |
| 8 | Conferences | Global Pet Expo Mar 2027, SuperZoo Aug 2027 | $5-15k/conference | High intent (in-person) |
| 9 | Google Cloud co-marketing | Hackathon win → Google Cloud customer story request | Founder time | Big distribution boost |
| 10 | "Mock Cosequin defense file" content drop | Publish what Cosequin's defense file SHOULD have looked like | Founder time | High virality among GCs |

**Y1 H1 priority: 1, 2, 4, 10.** Cheap, high-quality, fast. Stack on 3 (content) for compound effect.

---

## DOGS EAT THE FOOD — 6 validation experiments (Aulet step 21+23)

Codex G7.2 P0.2 + P0.5: must prove demand AND prove retention, not assume. Six experiments with explicit pass/fail.

| # | Experiment | Target date | Pass signal | Fail signal | Cost |
|---|---|---|---|---|---|
| 1 | Hackathon ShopperAgent publishes 100 daily queries against real Honest Paws / Native Pet / Fera Pets PDPs | June 5 → ongoing | Inbound interest from at least 1 of the 3 brands within 30 days asking "what is this?" | Zero inbound = AI-agent visibility theory weak | $0 (uses existing infra) |
| 2 | 10 cold outbound emails to top-10 shortlisted pet brand GCs | Q3 2026 (July) | 3 meetings booked + 1 paid pilot at $99/mo or $499/mo within 60 days | <1 meeting = pricing or message wrong | Founder time |
| 3 | NASC outreach for co-authored bulletin | Q3 2026 (July) | NASC accepts call + green-lights joint white paper draft within 30 days | Decline = partner-channel theory weak | Founder time |
| 4 | "Mock Cosequin defense file" content drop | Q3 2026 (Aug) | Top 10 search ranking for "Cosequin substantiation" within 60 days + at least 3 inbound brand inquiries | Zero virality = content-as-channel weak | Founder time |
| 5 | Pricing test on 30 inbound leads | Q4 2026 | Conversion: Free → Starter ≥30%, Starter → Pro ≥15% | Conversion <half target = pricing wrong | Founder time |
| 6 | Pilot retention check on first 10 paying brands | Q4 2026 / Q1 2027 | At least 8 still paying after 90 days; at least 5 expanded SKU coverage | <6 retention = "fix and leave" risk confirmed → urgent business-model rethink | Founder time |

If experiments 2, 3, and 6 all fail: **kill the standalone product thesis and pivot to white-label-only for accredited certifiers.** That's the codex G7.2 fallback to $100M ARR — full retailer/insurer/large-brand mandatory contracts, no SMB self-serve.

---

## GOOGLE STRATEGIC FIT (7 alignments — why GFS judges + Google Cloud BU want ACP to win)

| Google strategic agenda | How ACP serves it |
|---|---|
| 1. **A2A protocol adoption** | ACP is the strongest pull-through commerce-vertical use case for A2A v0.3 (LF donation Apr 2026). Google pushed A2A to LF specifically to drive ecosystem adoption; ACP delivers the first real cross-org use case |
| 2. **ADK 2.0 platform validation** | ACP is a 5-agent ADK deployment in production. Every successful ACP brand is a case study Google uses against LangChain / AutoGen |
| 3. **Vertex AI Agent Engine billable surface** | ACP consumes Reasoning Engine + Gemini API + Vertex AI Search + Cloud Run per cert. Scales 1000:1 if cross-vertical hits. Google Cloud revenue accelerator |
| 4. **Gemini 3 Pro citation-grounded reasoning showcase** | ACP's evidence-grader is the canonical citation-grounded reasoning use case. Reference architecture material |
| 5. **MCP ecosystem play** | ACP publishes evidence-grader and auditor as Agent Garden / Marketplace ADK agents. Drives MCP adoption |
| 6. **Counter to OpenAI / Anthropic agent stacks** | OpenAI Operator + Anthropic Computer Use both have agent identity stacks coming. Google wants public-protocol alternative (A2A + ACP) live before they do |
| 7. **Gemini Shopping competitive defense** | Rufus + Perplexity Shopping + ChatGPT Shopping are eating Google Shopping share. Gemini Shopping needs a trust oracle to differentiate. ACP-on-A2A is that oracle if it ships first |

GFS judges aren't just picking the most technically impressive submission. They're picking the submission that advances Google's strategic agenda. ACP advances 7 of them. That's the leverage.

---

## HACKATHON COMPLIANCE MAP (rule-by-rule)

GFS AI Agents Challenge (or Rapid Agent — to be verified against hackathon ID 3197):

| Rule | How we satisfy | Where |
|---|---|---|
| Gemini models | Gemini 3 Pro (reasoning) + Gemini 2.5 Flash (routing + audit) | All 5 agents |
| ADK 2.0 | All 5 agents + orchestrator built with ADK | `agents/` |
| A2A protocol v0.3 | Public mesh agent card at `/.well-known/agent-card.json` + ShopperAgent consumer | `docs/A2A-AGENT-CARD.md` |
| Cloud Run / GKE / Agent Engine | Cloud Run per agent + Vertex AI Agent Engine for orchestrator | All deployments |
| MCP integration | BioMCP (primary) + AI2 Asta MCP (grading) + Firecrawl MCP (PDP scrape) | `evidence-grader`, `claim-extractor` |
| Newly created during contest period (May 5 - June 11 for Rapid Agent; verify GFS dates) | PawConscious Mesh repo created 2026-05-17 (post-May-5 ✓); PawConscious live site is separate codebase, disclosed in Devpost | Git history |
| Public OSI-licensed repo, license at top | MIT, badge in README | `LICENSE` |
| Hosted URL | `mesh.pawconscious.com` (or `pawconscious-mesh.run.app` fallback) | Cloud Run domain |
| 3-min video, English, YouTube/Vimeo public | O22 pipeline production | Phase 6 |
| All team members on Devpost | Solo founder | Submission form |
| Original work | Architecture-inspired by GUARDIAN but new build | Git history + commit messages |
| No competing cloud platforms | GCP only | Repo |
| No competing AI tools | Gemini-family only for hackathon submission code | Repo |
| Devpost text description | Feature / tech / data sources / findings | Phase 7 |

Disclosure needed in Devpost: PawConscious live site (pawconscious.com/portal) uses Subconscious + Natoma — that's a separate codebase, not in the hackathon repo. `mesh.pawconscious.com` is the new hackathon-period build.

---

## OPERATING MODEL (solo founder discipline)

**Daily:** 4 hrs deep build · 2 hrs sales/support · 1 hr writing/content · 1 hr metrics review.

**Weekly:** Codex sweep on every major commit (Friday). Demo to advisor (MIT prof, Boston vet, GC friend). Friday afternoon strategic-review hour: read week's data + adjust.

**Monthly:** Revenue review + retention cohort + churn analysis + codex+claude+gemini cross-model strategic review. Monthly investor update (even pre-seed — builds discipline + paper trail).

**Quarterly:** YC-partner-style review (3 questions: what worked, what didn't, what's the bet for next quarter). External advisor 1:1s (MIT, vet network, GC).

**Mindset bias:** build like a hacker, ship like a startup, sell like a senior consultant, think like a YC partner, govern like a standards-body chair.

---

## PCEC STANDARDS COALITION — 90-day checklist (codex G7.2 P0.5)

Codex base rate for solo-founder-led standards adoption is ~0%. To beat that:

| Day | Milestone |
|---|---|
| 0 (today) | PCEC v0.1 draft published in public repo with explicit "not a standard, draft proposal" disclosure |
| 14 | Outreach to 3 institutional targets: NASC (Bill Bookout, ED), Tufts Cummings (Dr. Jennifer Larsen, nutrition), Kelley Drye (Christie Grymes Thompson, ad-law partner) |
| 30 | First call with NASC + decision on co-authored bulletin track |
| 45 | Outreach to Cornell Vet (Dr. Joseph Wakshlag) + UPenn (Dr. Kathryn Michel) + Chewy CISO/CTO office (David Stark) |
| 60 | Hackathon submission published (PCEC v0.1 visible to judges) |
| 75 | NASC bulletin co-authorship discussion + 1 LOI signed |
| 90 | 3-5 institutional co-founders signed (target: NASC + Tufts + Kelley Drye + Chewy observer + insurer observer); governance/IP policy v0.1 published; 2 LOIs to implement |

If 90-day milestone misses by >30 days: PCEC stays an internal spec, no Linux Foundation pursuit. The product still works — the standards-body moat becomes "preferred internal evidence format" not "open standard."

---

## LIABILITY + ACCREDITATION PATH (codex G7.2 P0.1 + Series A flag)

Post-pivot, ACP does NOT carry certifier liability. We carry **infrastructure-correctness E&O only** ($50k policy ~$1.5k/yr). The certifier (NASC, NSF, USP, or partner vet body) carries the cert liability.

Accreditation roadmap:
- **Y1:** No ACP-side accreditation. Partner with NASC for pet vertical (NASC is the de facto pet supplement certifier). Brand sees "NASC Cert powered by ACP infrastructure."
- **Y2:** Pursue ISO 17025 (testing labs) reference impl in partnership with one accredited lab. ACP infra becomes "ISO-17025-aligned" via partner.
- **Y3:** Optional pursuit of ISO 17065 (certification body) if independent path emerges; otherwise stay partnership-only forever (Stripe doesn't need a banking license; ACP doesn't need 17065).

E&O insurance:
- Y1: $50k policy ($1-2k/yr) — covers infrastructure correctness (mesh returns wrong cert ID, transparency log corrupted, etc.)
- Y2+: Scale to $1M policy as enterprise contracts open
- Cert-issuance liability stays with accredited partner

Series A diligence response:
- "We are not a certifier. We are the infrastructure that accredited certifiers use to issue and continuously re-verify their certs. Liability for cert correctness stays with the accredited partner per contract. Our liability is bounded to infra correctness, covered by E&O."

---

## RISK REGISTER v2 (post-G7.2)

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| NASC doesn't agree to partnership | Med | High | Approach Tufts Cummings + Cornell as alternative academic certifier; or build ACP-Pet Council as new accredited body w/ vet schools |
| "Fix and leave" dominant in 2026 data (G7.2 confirmed weak retention reasons) | High | High | Front-load Pro tier with monitoring + auto-re-verify so brand sees ongoing value in month 2 |
| Simplified pricing ($99/$499) underprices vs Cosequin defense value | Low | Med | Add Enterprise tier $5k/mo for >$25M ARR brands needing white-glove |
| Vanta extends to consumer products | Med (24-36mo) | High | Standards coalition + accredited-partner channel both create switching cost Vanta can't easily replicate |
| AI shopping agents stay walled-garden | Med | Med | Fallback business survives on brand+retailer+insurer mandatory contracts (G7.2 confirmed path to $100M ARR without AI-agent flywheel, but at slower pace) |
| Solo founder burnout | High | Critical | Hire technical co-founder by Y1 H2 with seed funds; advisor board for emotional/strategic support |
| Cosequin-class plaintiff catalyst doesn't repeat | Med | Med | Multiple catalysts (Prevagen precedent + retailer asks + AI commerce shift) — multi-factor demand, not single-factor |
| Regulator picks different standard | Med | High | Be first in front of NY AG / FTC ESI Lab / CA AG — get to "usage" status (not endorsement) in 24-30 months |
| GFS hackathon doesn't pick us | Med | Low for biz / Med for narrative | Submission still produces working public infra + open spec; can still pursue Google Cloud customer-story path even without award |
| Cloud spend overruns | Low | Med | Cloud Run scales to 0; cap Gemini 3 Pro to demo windows; aggressive caching for AI-agent queries |

---

## CODEX G7.2 AMENDMENTS TABLE (this doc absorbs all)

| G7.2 finding | Where absorbed in this doc |
|---|---|
| Strongest rec: "stop self-certifying, partner with accredited body" | "CRITICAL PIVOT" at top + Liability + BMC Key Partners |
| P0.1: regulator-grade false without accreditation | Pivot + Liability section + scrub language across docs |
| P0.2: two-sided billing over-engineered | BMC Revenue Streams (simplified to flat per-cert + monitoring tier); per-impression and per-query OFF hackathon scope |
| P0.3: PCEC treated like adopted standard | This doc, BUSINESS_PLAN.md, docs/PCEC-v0.md all carry "DRAFT PROPOSAL not standard" |
| P0.4: unit econ ignore expert/legal/insurance | Unit Economics section with new cost lines (vet $80/cert, insurance $50/yr, legal $150/yr) |
| P0.5: GTM sequencing infeasible | Conservative scenario added; Y1 = SMB ONLY; retailer/insurer pushed to Y2 H2 — Y3 |
| P0.6: "pet → human mechanical" wrong | Human vertical pushed to Y3+; clinical evidentiary standards explicit; +12-18mo timeline |
| P0.7: AI platforms walled-garden | Fallback narrative documented; AI-agent metering OFF hackathon scope; Perplexity Shopping as first realistic integration target |
| P1.1: certification boundary undefined | Pivot section makes explicit: ACP asserts infra-correctness; experts assert claim-rubric; accredited partner asserts cert |
| P1.2: governance artifact missing | 90-day coalition checklist with named targets |
| P1.3: who pays for AI-agent queries | Brand opt-in only; off Y1 scope; Y2 as add-on if brand wants AI-agent traffic monetization |
| P1.4: Y3 protocol governance + pharma data licensing speculative | Removed from base case; aggressive scenario only |
| P1.5: SOC2 + audit logs + retention before retailer outreach | Added to Y1 H2 roadmap |
| Open Q1: retention story weakest 3 | Documented; pilot retention exp focuses on strong 4 reasons (#1, 2, 4, 5) |
| Open Q2: Vanta comp doesn't translate | Acknowledged; TAM compressed in realistic + conservative scenarios |
| Open Q3: AI-agent platform shift load-bearing | Fallback narrative explicit (retailer/insurer mandatory contracts $500k-2M ACVs) |
| Open Q4: regulator endorsement 5+ yr | Reframed as "usage" not "endorsement" for 24-30mo |
| Open Q5: PCEC standards play near-zero base rate | 90-day coalition checklist beats base rate or doesn't |
| Open Q6: PawConscious vs ACP-parent | Adopt ACP-parent NOW; PawConscious Mesh = pet vertical product |
| Open Q7: Series A red flags | Liability section + accreditation roadmap + Y1 H2 SOC2 + appeals process + renewal economics proof gate |

---

## NEXT: CODEX G7.3 + DECISION

Codex G7.3 fires on this doc to challenge:
1. Is the ACP-as-infra (not certifier) pivot the actual right pivot, or are we now optimizing for codex's framing instead of the founder's instinct?
2. Is the 90-day coalition checklist achievable for a solo founder, or are we setting up for failure?
3. Does the simplified pricing ($99 / $499 / Enterprise) leave money on the table that a Stripe-style metered model would capture?
4. Is the partner-channel risk (NASC says no) so high we need a Plan B for the certifier-partner before any D1 work begins?
5. Anything else this drafting AI is still over-optimistic about?

After codex G7.3: Omar picks alternatives vs week-by-week hack-winning plan. Then push to GitHub. Then D1.
