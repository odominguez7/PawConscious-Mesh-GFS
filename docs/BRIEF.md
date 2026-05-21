# PawConscious — Brief

*One-pager. 90-second read.*

---

## What it is

**PawConscious is the trust layer AI agents call before recommending a consumer product.**

A B2B protocol that lets brands prove their endorsement claims are evidence-graded, regulator-mapped, and adversarially audited. Output: a cryptographically signed bundle a shopping agent can verify offline in milliseconds.

Live today at [`mesh-api-oasa5mxega-uc.a.run.app`](https://mesh-api-oasa5mxega-uc.a.run.app).

---

## The problem

AI shopping agents are about to make most consumer purchase decisions. They will surface "best supplement for senior dog joint pain" the way Google surfaces blue links. The agent doesn't read the label. It doesn't check the science. It picks whichever brand the model was most exposed to in training.

Brands have no machine-readable way to tell an agent: *our hip-and-joint claim is backed by three real PubMed papers, maps to AAFCO PF7 substantiation, and would survive an FTC §255 audit*. So agents either recommend everyone equally (bad for the good brands) or hallucinate trust signals (bad for everyone).

Today the verification work happens after a complaint files, in court, retroactively. PawConscious moves it up the funnel: every claim gets signed before the agent ever sees the product page.

---

## The product

A seven-agent mesh runs on Google Cloud against any product detail page:

1. **claim_extractor** — pulls every health/efficacy claim from the PDP
2. **evidence_grader** — searches PubMed via BioMCP, grades paper relevance and direction
3. **vet_rubric** — scores 0–5 on a panel-quality rubric, escalates ambiguous claims to a human vet
4. **compliance** — maps the claim to FTC §255 / AAFCO / NASC standards, grounded in a Vertex AI Search corpus
5. **auditor** — adversarial pre-sign pass, fails the bundle if citations don't exist or direction doesn't match
6. **report_writer** — composes a human-readable certificate
7. **second_opinion** — independent Google-Search-grounded adversarial review after signing

The bundle is signed with Ed25519, anchored to a `did:web`, and appended to a Firestore transparency log with a hash chain. Any agent can verify the signature without calling our API.

The output spec — **PCEC v0.1, the Pet Claim Endorsement Credential** — is open and CC-BY licensed. Anyone can run their own mesh. We expect to be the reference implementation, not the only one.

---

## Why this is a real product, not a demo

| Surface | Status |
|---|---|
| 7-agent mesh on Cloud Run | Live |
| Ed25519 signatures from GCP Secret Manager | Real, not stubbed |
| Vertex AI Search corpus (FTC §255 + AAFCO + NASC summaries) | 7 docs indexed, returning real snippets |
| A2A v0.3 dual-shape envelope | Both flat and Linux Foundation standard accepted |
| PCEC transparency log with hash chain | Public at `/pcec/v0/chain/head` |
| Live JustFoodForDogs verification | Reproducible cached demo on landing page |
| Shopper-agent A2A round trip | Live at `/demo/shopper` |
| ADK eval baseline | 3/3 pass on eligible cases (DTC catalog churn note attached) |

---

## Who pays

Pet brands with shelf-stable supplement SKUs facing the FTC §255 endorsement guides rewrite and AI agent procurement.

Pricing teaser: $499/mo Pro, custom Enterprise. Real pricing tied to claim volume + audit cadence post-pilot.

---

## Who it's for next

- **DTC pet supplement brands** that already substantiate claims privately and want machine-readable proof
- **Agent platforms** (shopping copilots, voice ordering, autonomous procurement) that need a defensible recommendation signal
- **Vet schools and clinical reviewers** participating in the substantiation process (post-pilot panel rotation)

---

## Team

- **Omar Dominguez Mondragon** — CEO and Founder. MIT MBA 2026. Engineer by training. Boston Marathon, Ironman 70.3. Builds production systems.
- **Jennifer Fremont Smith** — COO. MIT Sloan Lecturer. Two prior exits: Smarterer (acquired by Pluralsight) and WECO (acquired by Feast & Fettle, Nov 2025).

Won 1st place at Natoma + Subconscious hackathon 2026-05-13. Submitted to Google for Startups AI Agents Challenge Track 3 (Marketplace + Gemini Enterprise), deadline 2026-06-05.

---

## The bigger picture

The endorsement layer in retail has always been mediated by humans: pharmacists, vets, certifying bodies, lawyers. AI agents are about to compress that mediation to milliseconds. Someone has to build the substrate that lets a $50M brand prove its evidence stack to a $0.001-margin agent call.

That substrate is the protocol. PawConscious is the first reference deployment, the first published spec, and the first signed bundle on a public chain. The protocol works for pet supplements first because the regulatory shape is clean and the brand pain is acute. Same architecture extends to human supplements, OTC pharma, cosmetics, and food.

---

## Links

- **Live product:** https://mesh-api-oasa5mxega-uc.a.run.app
- **Architecture:** https://mesh-api-oasa5mxega-uc.a.run.app/architecture
- **Agents reference:** https://mesh-api-oasa5mxega-uc.a.run.app/agents
- **Demo:** https://mesh-api-oasa5mxega-uc.a.run.app/demo/shopper
- **Agent card (A2A discovery):** https://mesh-api-oasa5mxega-uc.a.run.app/.well-known/agent-card.json
- **DID document:** https://mesh-api-oasa5mxega-uc.a.run.app/.well-known/did.json
- **Transparency chain head:** https://mesh-api-oasa5mxega-uc.a.run.app/pcec/v0/chain/head
- **PCEC v0.1 spec:** [docs/PCEC-v0.md](./PCEC-v0.md)
- **Source:** github.com/odominguez7/PawConscious-Mesh-GFS *(public Day 24 — 2026-05-28)*
