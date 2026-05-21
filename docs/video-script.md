# PawConscious Mesh — 3-minute demo video script

**For:** Google for Startups AI Agents Challenge 2026 submission
**Length target:** 2:55 (sub-3-min hard cap per hackathon rules)
**Production:** O22 pipeline (Veo 3.1 Fast for cinematic plates + Lyria 2 for music bed + ElevenLabs founder-voice VO + screen capture + Final Cut Pro / DaVinci Resolve assembly)
**Output:** YouTube unlisted, English, public link in Devpost submission

---

## SHOT-BY-SHOT (with VO and on-screen elements)

### 00:00 — 00:12 · COLD OPEN (cinematic plate + headline)

**VISUAL:** Veo 3.1 plate — slow push-in on a real Honest Paws hip-and-joint product on a kitchen counter, Labrador in soft focus background. Cuts to a static headline card:
```
"Cosequin paid $11.5 million in 2024.
 Plaintiff bar found pet supplements."
```

**VO:** "Pet supplements are a 2.8 billion dollar US category. In 2024, Cosequin paid 11.5 million dollars to settle a class action over joint-mobility claims they couldn't substantiate. Plaintiff bar is now templating these cases. Native Pet, Honest Paws, every DTC pet brand — same risk."

**MUSIC:** Lyria 2 opens — slow tension build, single piano motif.

### 00:12 — 00:30 · THE PRODUCT (paste URL → fan-out)

**VISUAL:** Screen capture — `mesh-api-40952019806.us-central1.run.app` portal. Cursor pastes the live Native Pet hip-and-joint PDP URL into the input box. Click "Validate." Mesh Console UI lights up — the orchestrator runs claim-extractor, then the three-way fan-out (evidence-grader · vet-panel · compliance) animates per claim, then auditor reviews the merged bundle.

**VO:** "PawConscious Mesh — seven agents on Google Cloud, callable by any AI shopping agent over A2A. A brand pastes a product URL. The mesh fans out, signs the evidence, and chains it."

**ON-SCREEN CALLOUTS:**
- Gemini 2.5 Pro / 2.5 Flash
- A2A v0.3
- Cloud Run
- Vertex AI Search
- BioMCP + Semantic Scholar
- Google ADK (Phase 4 scaffold)

### 00:30 — 01:10 · LIVE MESH TRAFFIC (pre-recorded for reliability per codex G7.3 P0.5)

**VISUAL:** Mesh Console live-traffic view. Each agent fills in as it completes:

- `claim-extractor` → "7 claims extracted from PDP"
- `evidence-grader` → "12 PubMed citations · top: 247 total / 18 influential (Semantic Scholar)"
- `vet-rubric` → "AI 5-vet rubric simulation: 4 of 5 claims pass at 4+/5; 1 claim flagged for escalation to v0.2 licensed-DVM attestation"
- `compliance` → "FTC §255 mapping: 2 violations flagged"
- `auditor` → "Adversarial pass: 1 PMID format mismatch flagged"
- `report-writer` → "Cert composed: signed Ed25519, chain-anchored"
- `second-opinion` → "Google Search grounded: FDA warning letter to Natural Native LLC + Cosequin $11.5M precedent — verdict flipped PASS → NEEDS REVIEW"

**VO:** "Claim extractor pulls every health claim from the PDP. Evidence grader queries PubMed live via BioMCP and grades citations by influence using Semantic Scholar. The AI vet-rubric simulation runs a five-vet rubric — Gemini role-playing five vets; the v0.2 release replaces this with licensed-DVM attestation. Compliance maps each claim to FTC two-five-five with snippet provenance. Auditor catches format mismatches. Then the second opinion — our adversarial agent — searches the live web for evidence that contradicts the brand's own conclusion. It finds an FDA warning letter and the Cosequin precedent, and flips the verdict to NEEDS REVIEW."

**MUSIC:** Lyria builds, drums enter.

### 01:10 — 01:40 · SIGNED CERT + CHAIN ANCHOR (the artifacts)

**VISUAL:** 

- Screen splits in two:
  - LEFT: signed JSON-LD cert appearing on the live page (PCEC v0.1 schema visible, wax-seal cert render, chain anchor sha256 hash visible)
  - RIGHT: click through to the public transparency log entry at `/pcec/v0/chain/head` — the cryptographic chain showing this bundle has been appended

**VO:** "Output: a signed evidence bundle in machine-readable PCEC format — the open spec we're proposing. Ed25519 over the canonical bundle JSON, anchored to a public Firestore transparency log. The brand can prove its evidence chain was issued at a specific moment and has not been silently replaced."

**ON-SCREEN CALLOUTS:**
- PCEC v0.1 (draft open spec, CC-BY-4.0)
- Ed25519 signed
- Public transparency log (Firestore append-only chain)

### 01:40 — 02:20 · THE LIVE A2A MOMENT (the verifiable live call, per codex G7.3 P0.5)

**VISUAL:** Cut to a SECOND browser tab opening — `shopper.pawconscious-mesh.run.app` (the public ShopperAgent service, source visible on GitHub). User types: "best joint supplement for senior labs."

**SCREEN CAPTURE:** ShopperAgent logs stream in real-time:
1. `GET https://mesh-api-40952019806.us-central1.run.app/.well-known/agent-card.json` → 200 OK
2. `POST /a2a/v1/tasks/send` `{skill: "verify_claim", sku: "honest-paws-hip-joint", claim: "supports joint mobility"}`
3. Streaming response over SSE: trust score 0.78, bundle URN `urn:pcec:claim:01HZ...`, 6 papers cited

Cut to the ShopperAgent UI showing the ranked answer with trust scores attached to each brand.

**VO:** "This is the moment that proves the architecture. A second program — our ShopperAgent, source on GitHub — discovers our mesh through the standard A2A agent card, then calls verify_claim. This is a real network call. Real response. This is what every AI shopping agent — Rufus, Perplexity Shopping, Gemini Shopping — will need by 2027. Today we control the calling agent. The protocol is open from day one."

**MUSIC:** Lyria peaks.

### 02:20 — 02:45 · THE THESIS (closing card)

**VISUAL:** Cinematic plate — close-up on a vet's hands signing an attestation tablet (Veo 3.1 generated). Cut to the Google Cloud stack logos in sequence: Gemini 2.5, A2A v0.3, Cloud Run, Vertex AI Search, BioMCP, Google ADK (Phase 4 scaffold).

**VO:** "ACP — the Agentic Compliance Protocol. Verifiable claim infrastructure for consumer goods. Pet supplements are the proving ground. Human supplements, beauty, functional food — same protocol, mechanical expansion. We built this on Google Cloud because A2A is the substrate AI commerce will run on. PawConscious Mesh is the reference deployment. We're shipping the protocol open and partner-ready from day one."

### 02:45 — 02:55 · CTA + CREDITS

**VISUAL:** Static card with three URLs:

```
mesh-api-40952019806.us-central1.run.app         — live mesh
github.com/odominguez7/PawConscious-Mesh-GFS  — MIT open source
pcec.dev (coming soon)         — protocol spec
```

**VO:** "PawConscious Mesh. Built solo for Google for Startups by Omar Dominguez, MIT MBA 2026."

**MUSIC:** Lyria resolves, falls to single piano outro.

**END CARD:** Google Cloud stack (Gemini · A2A · Cloud Run · ADK scaffold) + MIT license badge.

---

## TECHNICAL PRODUCTION NOTES

**Voiceover:**
- ElevenLabs founder-cloned voice OR Omar live recording
- Pace 165 wpm sustained
- Slight emphasis pause before "real PMIDs," "the protocol is open," "shipping the protocol open"

**Music:**
- Lyria 2 generated bed at 75 BPM (so VO sits cleanly)
- Genre prompt: "modern cinematic minimalist piano + subtle synths + light percussion building from 1:00 onward"

**Plates (Veo 3.1 Fast):**
- 0:00 — Honest Paws on counter with Labrador (12s, 1080p, slow push-in)
- 2:20 — Vet hands signing tablet (10s, 1080p, soft focus)
- Cost target: $1-2 total for both plates

**Screen captures:**
- Mesh Console fan-out animation captured at 60fps, OBS or QuickTime
- ShopperAgent log stream captured live with terminal recorder (asciinema → mp4 conversion if needed)

**Editing:**
- Final Cut Pro or DaVinci Resolve (free)
- Hard cut on every section boundary; no cross-fades
- Color grade: warm Honest Paws → cool tech screen → warm vet hands

**Subtitles:**
- Generate via Whisper from final mix
- Burn-in English subtitles per hackathon rules
- Place at bottom-center, white text + 60% black background bar

**Render targets:**
- 1080p H.264 30fps for YouTube unlisted
- File size <2GB for upload reliability

---

## DEMO NARRATIVE INTEGRITY (per codex G7 / G7.2 / G7.3 lessons)

What this video does NOT claim:
- ❌ Perplexity Shopping is integrated (it's not — the ShopperAgent we built calls our mesh; Perplexity is the *use case* not the *current integration*)
- ❌ NSF / NASC has signed off (no LOI yet)
- ❌ Linux Foundation has accepted the spec (it's a draft proposal)
- ❌ Founding-member coalition exists (post-hackathon work)
- ❌ Regulator-grade (we're an "automated draft evidence bundle" per the script)

What this video DOES prove:
- ✅ A working multi-agent system on Google Cloud against real PDP URLs
- ✅ Real PubMed citations retrieved, real grading
- ✅ A2A v0.3 protocol with a verifiable live external call
- ✅ Open source spec + MIT code
- ✅ A clear vision for the protocol's scale

---

## REVIEW GATES BEFORE SHIPPING THE VIDEO

- Stranger test: 2 non-technical viewers watch, can they explain back the product in one sentence?
- Codex G12 sweep on the final cut
- Outside-voice review on the Devpost text description
- Final compliance check: no third-party logos (per rules), no offensive content, no fabricated claims
