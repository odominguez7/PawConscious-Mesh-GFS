# Devpost Submission — PawConscious Mesh

**Google for Startups AI Agents Challenge 2026 · Track 3 (Refactor for Marketplace + Gemini Enterprise) · Deadline 2026-06-05 5 PM PT**

This is the final submission copy. ~700 words across the 9 Devpost form fields. Product and architecture claims are verifiable against the live URL or the public repo; market-size and case-law citations link to their public sources inline.

---

## Project Name

PawConscious Mesh — ACP for Pet

## Elevator Pitch (140 char max)

The trust layer AI shopping agents call before recommending a pet supplement. Signed evidence bundles. Public A2A v0.3. 4/7 on Google ADK.

## Tagline

Verifiable claim infrastructure for consumer goods. Built on Gemini 2.5 + Google ADK + Vertex AI Agent Engine + A2A v0.3 + Cloud Run. Pet supplements are the wedge; the protocol scales to every consumer vertical AI shopping will mediate.

## Inspiration

Pet supplements are a $2.8B US category where "vet-formulated" packaging does most of the selling. In 2024, Cosequin's manufacturer paid $11.5M to settle a class action over joint-mobility claims they could not substantiate. The FTC's 2023 update to 16 CFR §255 tightened expert-endorsement substantiation. Plaintiff bar is now templating cases against the rest of the category.

Meanwhile, AI shopping agents (Amazon Rufus, OpenAI Operator, Perplexity Shopping, Gemini Shopping) are becoming the dominant top-of-funnel for considered purchases. They need callable trust oracles before they can answer "best joint supplement for senior labs." The brand needs defense, the agent needs trust. Both forces drive the same buy. We built the infrastructure that closes the gap.

## What it does

A brand pastes a product URL. Seven specialized agents run on Google Cloud and return a signed PCEC v0.1 evidence bundle in 60-90 seconds. The bundle is callable from any A2A v0.3 client, verifiable offline against a `did:web` Ed25519 key, and chain-anchored to a public Firestore transparency log.

The seven agents: `claim_extractor` (httpx + Firecrawl fallback), `evidence_grader` (BioMCP → PubMed + Semantic Scholar citation grading), `vet_rubric` (5-vet rubric simulation; real DVM attestation is v0.2), `compliance` (Vertex AI Search over FTC §255 + AAFCO + NASC corpus with snippet provenance), `auditor` (PMID format + claim-direction Falsifier), `report_writer` (HTML cert), `second_opinion` (Gemini + Google Search adversarial 4-stress test).

Four of seven agents are wired as real Google ADK `LlmAgent` + `FunctionTool` declarations inside a `SequentialAgent` + `ParallelAgent` topology. Judges can introspect the topology at `/health/mesh-shape` without invoking the LLM.

## How we built it

**Track 3 mandates, all satisfied in shipped code:**

- **Gemini.** 2.5 Pro for six reasoning agents; 2.5 Flash for the auditor.
- **Cloud Run.** Two services (`mesh-api`, `shopper-agent`), us-central1, scale-to-zero.
- **A2A v0.3 (Linux Foundation).** Public agent card at `/.well-known/agent-card.json`; dual-shape envelope (standard + flat); a separate ShopperAgent service in this repo demonstrates the round trip.
- **Google ADK.** `claim_extractor`, `evidence_grader`, `compliance`, `auditor` declared as `LlmAgent`s with `FunctionTool` wrappers around BioMCP search and Vertex AI Search retrieval. Topology at `/health/mesh-shape`. `vet_rubric`, `report_writer`, `second_opinion` stay outside ADK by design (panel simulation, post-sign rendering, independent adversarial review).
- **Vertex AI Agent Engine.** Reasoning Engine deployed; routing flag (`ACP_USE_AGENT_ENGINE`) with rolling p95 latency gate and per-request timeout. State observable at `/health/agent-engine` + `/health/agent-engine-traffic`.

**Other Google Cloud.** Firestore append-only transparency log with `sha256(bundle_hash + ":" + prev_hash)` chaining. Cloud Build CI deploys both services.

**MCP / open ecosystem.** BioMCP for biomedical retrieval; Semantic Scholar Graph API for citation influence; Google Search grounding for second_opinion.

**Signing.** Real Ed25519 software signing from GCP Secret Manager (no stubs). HSM-backed signing is on the v0.2 roadmap.

## Challenges we ran into

**Trust-but-verify on every claim we make about ourselves.** Eight rounds of adversarial code review flagged overclaims (`regulator-grade` → softened, "AI2 Asta MCP" → replaced with the real Semantic Scholar Graph API, `5 ADK agents` → corrected to the honest 4/7 split). Each block made the submission stronger.

**Honest ADK migration.** Day 19 the ADK story was "scaffold for Phase 4." Days 20-21 we wired four real `LlmAgent`s + `FunctionTool`s + `SequentialAgent` + `ParallelAgent` topology. Runtime stays `asyncio.gather` for determinism, but the ADK objects are real and introspectable.

**DTC catalogs churn weekly.** 15 of our 20 original eval URLs returned 404 between hackathon kickoff and submission week. We refreshed to 16 live URLs + a synthetic-fixture eval track and taught the runner to treat anti-bot codes (403/406/429) as eligible.

## Accomplishments we're proud of

- Seven-agent A2A mesh end-to-end with real PubMed retrieval, real Semantic Scholar citation grading, real Ed25519 signatures, and a real chain-anchored transparency log. Sample signed bundle captured in `demo/captures/live-mesh-call-2026-05-18-native-pet.json` for offline replay.
- Adversarial `second_opinion` agent (Gemini 2.5 Pro + Google Search grounding) runs four stress tests against every signed bundle: court-of-law, regulator, scientific consensus, public skepticism. The grounding has surfaced FDA warning letters and class-action precedents the in-mesh auditor did not see. Outputs are nondeterministic by design; each run is its own evidence trail.
- 4-of-7 on Google ADK with `/health/mesh-shape` introspection (no LLM invocation required to verify).
- Vertex AI Agent Engine deployment behind a rolling-p95 gate and per-request timeout.
- PCEC v0.1 draft open spec proposing verifiable claim infrastructure for consumer commerce.

## What we learned

Structural independence is the moat. Trust infrastructure captured by the parties being verified erodes credibility. PCEC ships MIT licensed; anyone can run their own mesh.

Adversarial reviews compound. Every commit went through an independent codex review. Three BLOCK verdicts forced us to drop "regulator-grade" overclaim, collapse partner dependency, and replace fabricated retailer integrations with our own ShopperAgent.

Honest framing beats hype. The 4-of-7 ADK split and the `asyncio.gather` runtime path are surfaced explicitly in the README, the `/architecture` page, and this Devpost. Judges can verify every claim by clicking a URL.

## What's next for PawConscious Mesh

ADK Runner runtime path behind the same feature-flag pattern as the Reasoning Engine routing. `attest_expert` A2A skill for real licensed-DVM attestation. HSM-backed signing. Per-key rate-limiter + `429 / Retry-After`. PCEC v0.2 with a second issuer signing into the chain to prove the spec is multi-implementer.

---

## Built with (Devpost tech-list)

google-cloud · google-adk · gemini-2-5-pro · gemini-2-5-flash · vertex-ai-agent-engine · vertex-ai-search · a2a-protocol · cloud-run · firestore · cloud-build · biomcp · semantic-scholar · python · fastapi · ed25519 · pcec-v0-1

## Try it out

- **Live mesh:** https://mesh-api-40952019806.us-central1.run.app/
- **Try the curl in 30 seconds:** https://mesh-api-40952019806.us-central1.run.app/agents
- **Architecture diagram (interactive):** https://mesh-api-40952019806.us-central1.run.app/architecture
- **ADK topology JSON (no LLM call):** https://mesh-api-40952019806.us-central1.run.app/health/mesh-shape
- **Agent Engine traffic state:** https://mesh-api-40952019806.us-central1.run.app/health/agent-engine-traffic
- **Public A2A agent card:** https://mesh-api-40952019806.us-central1.run.app/.well-known/agent-card.json
- **ShopperAgent round-trip demo:** https://mesh-api-40952019806.us-central1.run.app/demo/shopper
- **GitHub (MIT):** https://github.com/odominguez7/PawConscious-Mesh-GFS
- **PCEC v0.1 draft spec:** [`docs/PCEC-v0.md`](https://github.com/odominguez7/PawConscious-Mesh-GFS/blob/main/docs/PCEC-v0.md)
- **3-min demo video:** YouTube unlisted (link populated post-render)

Demo API key for judges: `demo-key-2026-06`.

## Project Members

Omar Dominguez Mondragon — Founder. MIT MBA 2026.

## Submission Disclosure

PawConscious Mesh is a new build for this hackathon, created during the contest period. The live consumer site at `pawconscious.com/portal` runs a separate prior codebase from a different hackathon (Subconscious + Natoma, 2026-05-13, won 1st place). That codebase is not part of this submission.
