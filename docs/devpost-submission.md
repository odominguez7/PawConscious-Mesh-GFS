# Devpost Submission Draft — PawConscious Mesh

**For:** Google for Startups AI Agents Challenge 2026 (Devpost hackathon ID 3197 — verify track name)
**Submission deadline:** 2026-06-05 noon PT
**Status:** Draft (will iterate weekly through hackathon period)

---

## Project Name
**PawConscious Mesh — ACP for Pet**

## Elevator Pitch (140 char max per Devpost)
> Agentic compliance protocol for endorsement claims on pet supplements. 5 ADK agents on Google Cloud. Real PubMed. Live A2A. Pet first.

## Tagline (longer)
> The verifiable claim infrastructure for consumer goods. Built on Google ADK + Gemini 3 Pro + A2A. PawConscious Mesh is the pet-supplement reference deployment. Scales to every consumer vertical AI shopping will mediate.

## Cover image
Custom rendered: Honest Paws PDP with our "Verified by Vets" badge mounted, click-popover showing real PMIDs. Veo 3.1-generated background plate. 1280×640.

---

## Inspiration

Pet supplements are a $2.8B US category where TikTok endorsements, white-coat packaging, and the words "vet-formulated" do most of the selling. In 2024, Cosequin paid $11.5M to settle a class action over joint-mobility claims they couldn't substantiate. The Federal Trade Commission's 2023 update to 16 CFR §255 tightened expert-endorsement substantiation. Plaintiff bar is now templating cases against the rest of the category — VetriScience GlycoFlex is pending, Morgan & Morgan is building a multi-brand pet-food docket.

Meanwhile, AI shopping agents (Rufus from Amazon, Operator from OpenAI, Perplexity Shopping, Gemini Shopping) are about to become the dominant top-of-funnel for considered purchases. They will need callable trust oracles before they can answer "best joint supplement for senior labs."

We saw the same gap from two sides — the brand needs defense, the AI agent needs trust. Both forces drive the same buy. PawConscious Mesh is the infrastructure that closes the gap.

## What it does

A brand pastes a product URL into PawConscious Mesh. Five specialized AI agents fan out in parallel via the A2A protocol on Google Cloud:

1. **claim-extractor** pulls every health claim from the product detail page
2. **evidence-grader** queries PubMed live via BioMCP and grades each citation by influential-citation count using AI2 Asta
3. **vet-panel** runs a 5-vet rubric simulation per claim and flags any that need human-vet escalation
4. **compliance** maps each claim to FTC 16 CFR §255 endorsement substantiation requirements, AAFCO public-domain definitions, and NASC public-side seal program standards
5. **auditor** (adversarial) catches hallucinated citations and claim-direction mismatches

In ~90 seconds, the brand gets back:
- A signed evidence bundle in machine-readable PCEC v0.1 format (the draft open spec we're proposing)
- An audit-grade PDF for legal counsel + plaintiff defense
- An embeddable trust badge for the product page with click-popover showing real PMIDs
- Continuous monitoring: every week, the auditor re-runs against new PubMed papers and regulator updates, re-issues the cert if anything changes

The mesh exposes a public A2A v0.3 agent card at `/.well-known/agent-card.json` with three skills any AI agent can call: `verify_claim(sku, claim_text)`, `fetch_substantiation_bundle(claim_id)`, `attest_expert(expert_did)`. We ship a separate ShopperAgent service (open source MIT alongside the mesh) that demonstrates the external A2A call against a real Honest Paws SKU.

## How we built it

**The stack is Google-native:**

- **Google ADK 2.0** — all 5 specialized agents + orchestrator built with the Agent Development Kit
- **Gemini 3 Pro** for the reasoning core (claim extraction, evidence grading, vet-rubric simulation, compliance mapping)
- **Gemini 2.5 Flash** for routing and the adversarial audit pass
- **Vertex AI Agent Engine** as the managed orchestrator with ParallelAgent fan-out + SequentialAgent merge
- **Vertex AI Search** over our public-redistributable corpus (FTC 16 CFR §255 federal text, AAFCO public docs, NASC public-side seal program docs)
- **A2A v0.3 protocol** (Linux Foundation, donated by Google April 2026) for the public agent card and the ShopperAgent integration
- **MCP integrations:** BioMCP for PubMed + Europe PMC + Semantic Scholar (one of the strongest open-source biomedical MCP servers, 21 tools, MIT, actively maintained), AI2 Asta MCP for citation-influence grading, and Gemini grounding with Google Search for situational context
- **Cloud Run** for per-agent deployment (auto-scales to zero, cost-efficient)
- **Firestore** for the append-only transparency log of issued certs
- **Cloud SQL** for the ACID-compliant cert registry
- **BigQuery** for the claim-to-evidence data flywheel + analytics
- **Cloud Storage** for raw PDP captures and generated audit PDFs
- **Secret Manager** for MCP API tokens
- **Cloud Build** for the CI pipeline

**Signing:** Ed25519 software signing for hackathon v0.1; HSM-backed signing on the post-hackathon roadmap.

**PCEC v0.1 spec:** drafted as a public proposal on GitHub (CC-BY-4.0), single trust root (`did:web:mesh-api-40952019806.us-central1.run.app`) for this version, with explicit "not a standard, draft proposal" framing per our independent reviewer's guidance.

## Challenges we ran into

1. **Cam-data direction was a dead end.** We started this work as a wildlife multi-agent project. Three rounds of cam-source research confirmed that no embeddable real-wildlife video stream exists at hackathon scale (YouTube bot-walls cloud-hosted demos; non-YouTube alternatives use MSE-tokenized HLS that won't play on third-party origins). We pivoted the agentic architecture onto a vertical with infinite, public, unconstrained input data: pet supplement product pages.

2. **Self-certifying was wrong.** Our first draft positioned the mesh as the certifier. An adversarial review pointed out that without ISO 17065/17025 accreditation and E&O coverage, we become the liability target. We pivoted to "program manager + evidence infrastructure" — the mesh issues evidence, an accredited body (NASC, NSF, vet-school panel) signs the cert. Partners optional in v0.1 with vet panel attestation as the credibility layer; partner channel as the long-term moat.

3. **Real biomedical retrieval has options and tradeoffs.** PubMed E-utilities are free but return raw XML with no relevance ranking. Natoma is an enterprise MCP gateway with no biomedical specialization. Vertex AI Search Healthcare is FHIR-shaped and overkill for pet evidence. BioMCP (open-source, MIT, 508 stars) won out with 21 biomedical tools and a single-line install. AI2 Asta MCP added the citation-influence grading on top.

4. **"AI shopping agents will call our endpoint" is an assumption.** Walled-garden behavior from Rufus + ChatGPT is plausible. We built our own ShopperAgent (source on GitHub MIT alongside the mesh) to demonstrate the external A2A call without fabricating integrations we don't have.

## Accomplishments we're proud of

- Multi-agent ADK orchestration with 5 specialized agents fanning out in parallel via A2A
- BioMCP + AI2 Asta MCP integration producing real PMIDs with citation-influence grading
- Public A2A v0.3 agent card with three callable skills
- Our own external ShopperAgent demonstrating the protocol end-to-end (not a fake "powered by Perplexity" claim)
- PCEC v0.1 draft open spec — first attempt at a verifiable claim infrastructure protocol for consumer commerce
- ~60% code salvage from prior agentic projects (compressed 6 weeks of work into 18 days)
- Built solo by an MIT MBA founder in 18 days

## What we learned

1. **Structural independence is the moat.** Trust infrastructure that's captured by the parties being verified (Trustpilot, Yelp, in-house retailer trust marks) erodes credibility over time. ACP is third-party: brands pay per claim, retailers pay platform fees, neither side can alter the rubric, the audit trail is public, the vet panel is academic. See `docs/INDEPENDENCE.md`. This is the answer to Series A capture risk and to regulator evidence-grade questions.

2. **Scraping is the bridge, not the destination.** httpx + Firecrawl together cover ~95% of US pet supplement BRAND PDPs directly. Major retailers (Chewy, Amazon, Petco) actively block all scraping at the Akamai/PerimeterX layer — even Firecrawl stealth proxies. The Y2 enterprise path: retailers PUSH catalog to us via authenticated API as part of $500k-2M/yr platform contracts, motivated by competitive pressure once 20%+ of their supplement category is ACP-verified at the brand source.

3. **The infrastructure positioning matters more than the product features.** Being "the agentic engine" is a $20-50M ARR ceiling. Being "the verifiable claim infrastructure for consumer goods" is the path to $100M+. Pet is the wedge; the protocol is the moonshot.

2. **Pet → human → every consumer vertical is mechanically defensible.** The same JSON-LD schema, the same agent architecture, the same Cloud Run stack works for human supplements (chondroitin/omega-3/MSM ingredient overlap is literal), then beauty (dermatologist-tested = same claim shape as vet-formulated), then functional food, then wellness devices.

3. **Codex/Gemini/Claude adversarial reviews compound.** Every major commit went through a brutal independent reviewer pass. Three rounds of BLOCK verdicts forced us to (a) drop the "regulator-grade" overclaim, (b) collapse partner dependency, (c) cut PCEC to honest v0.1 scope, (d) replace Perplexity-fabrication with our own ShopperAgent. Each round made the submission stronger.

## What's next for PawConscious Mesh

**Day 18-120 (post-hackathon):** Send first 10 pet brand outreach. Land 3 paid pilots. Secure 1 accredited certifier LOI (NASC or vet-school program). Co-author NASC technical bulletin discussion opens.

**Y1 H2 (Q4 2026):** 50 paying pet brands at $99-499/mo. Seed round $1-2M.

**Y2 (2027):** 200 brands + first retailer pilot (Chewy/Petco/Amazon Pet) + first insurer pilot (Trupanion). $2-4M ARR. Series A $5-10M.

**Y3 (2028):** Human supplements vertical opens (chondroitin/omega-3 mechanical ingredient overlap). PCEC v0.3 with 6 founding members signed.

**Y4-5:** Beauty + functional food + wellness device verticals. PCEC donated to Linux Foundation. AI-agent ecosystem default routing. $80-200M ARR. M&A interest from Verisign / Truepic / Adobe / S&P Global at $1.5-4B comparable to other protocol infra exits.

---

## Built with (Devpost tech-list)

- Google Cloud
- Google ADK 2.0
- Gemini 3 Pro
- Gemini 2.5 Flash
- Vertex AI Agent Engine
- Vertex AI Search
- A2A Protocol v0.3
- Cloud Run
- Firestore
- Cloud SQL
- BigQuery
- Cloud Storage
- Secret Manager
- Cloud Build
- BioMCP
- AI2 Asta MCP
- MCP (Model Context Protocol)
- Python 3.14
- FastAPI
- Next.js (Mesh Console UI)
- JSON-LD
- Ed25519 (signing)
- PCEC v0.1 (proposed open spec)

## Try it out (links to populate)

- **Live mesh:** `mesh-api-40952019806.us-central1.run.app` (populate after Phase 5 Cloud Run deployment)
- **ShopperAgent:** `shopper.pawconscious-mesh.run.app` (populate after Phase 4)
- **Public A2A card:** `mesh-api-40952019806.us-central1.run.app/.well-known/agent-card.json` (populate after Phase 4)
- **GitHub MIT:** `github.com/odominguez7/PawConscious-Mesh-GFS` (PUBLIC flip before submission; currently PRIVATE during build)
- **3-min demo video:** YouTube unlisted link (populate after Phase 6 render)
- **PCEC v0.1 draft spec:** `pawconscious.com/pcec/v0` or repo `docs/PCEC-v0.md`

## Project Members

Omar Dominguez (sole founder)

## Submission Disclosure

PawConscious Mesh is a new build for this hackathon, created during the contest period. The live consumer site at pawconscious.com/portal runs a separate prior codebase (Next.js + LangGraph + Subconscious TIM-Qwen3.6-27B + Natoma MCP) from a different hackathon (Subconscious + Natoma 2026-05-13, won first place). That codebase is not part of this submission.

---

**Final pre-submission checklist (June 4):**

- [ ] Hosted URL working + verified on real Honest Paws PDP
- [ ] 3-min video uploaded to YouTube unlisted with English subtitles
- [ ] GitHub repo flipped from PRIVATE → PUBLIC
- [ ] MIT license visible at top of repo
- [ ] All team members (just me) listed on Devpost project page
- [ ] No third-party logos in the video (only Google + MCP + A2A)
- [ ] Devpost text under 2000 char (above is draft, will tighten)
- [ ] Stranger test passed: 2 non-tech viewers can explain it back in one sentence
- [ ] Final codex G13 + outside-voice review
