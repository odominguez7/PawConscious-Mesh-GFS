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

**VISUAL:** Screen capture — `mesh-api-40952019806.us-central1.run.app` portal. Cursor pastes the live Honest Paws hip-and-joint PDP URL into the input box. Click "Validate." Mesh Console UI lights up — five A2A agent cards animate in parallel.

**VO:** "PawConscious Mesh — built on Google's Agent Development Kit. A brand pastes a product URL. Five specialized agents fan out via the A2A protocol on Google Cloud."

**ON-SCREEN CALLOUTS:**
- ADK 2.0
- Gemini 3 Pro
- Vertex AI Agent Engine
- A2A v0.3
- Cloud Run

### 00:30 — 01:10 · LIVE MESH TRAFFIC (pre-recorded for reliability per codex G7.3 P0.5)

**VISUAL:** Mesh Console live-traffic view. Each agent card fills in as it completes:

- `claim-extractor` → "7 claims extracted from PDP"
- `evidence-grader` → "12 PubMed citations · top: 247 total / 18 influential (AI2 Asta)"
- `vet-panel` → "5-vet rubric: 4 of 5 claims pass at 4+/5; 1 claim flagged for escalation"
- `compliance` → "FTC §255 mapping: 2 violations flagged"
- `auditor` → "Adversarial pass: 1 citation flagged as claim-direction mismatch — forcing re-grade"

**VO:** "Claim extractor pulls every health claim from the PDP. Evidence grader queries PubMed live via BioMCP and scores citations by influence using AI2 Asta. Vet panel runs a five-vet rubric simulation. Compliance maps each claim to FTC two-five-five. And the auditor — adversarial — catches a citation that doesn't support the claim direction. It forces a re-grade."

**MUSIC:** Lyria builds, drums enter.

### 01:10 — 01:40 · SIGNED CERT + EMBED (the artifacts)

**VISUAL:** 

- Screen splits into three: 
  - LEFT: signed JSON-LD cert appearing (PCEC v0.1 schema visible)
  - MIDDLE: audit-grade PDF being rendered
  - RIGHT: embed JS snippet, then cut to the Honest Paws PDP with the "Verified by Vets" badge mounted bottom-right

**VO:** "Output: a signed evidence bundle in machine-readable PCEC format — that's the open spec we're proposing. An audit-grade PDF the brand's GC can hand a plaintiff lawyer. And an embeddable badge — consumers click, they see the real PMIDs and the named expert attestations."

**ON-SCREEN CALLOUTS:**
- PCEC v0.1 (draft open spec)
- Ed25519 signed
- Continuous monitoring (re-issues on new science / regulator update)

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

**VISUAL:** Cinematic plate — close-up on a vet's hands signing an attestation tablet (Veo 3.1 generated). Cut to the Google Cloud stack logos in sequence: ADK 2.0, Gemini 3 Pro, Vertex AI Agent Engine, Vertex AI Search, A2A v0.3, Cloud Run, BioMCP.

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

**END CARD:** Three Google Cloud logos (ADK · Gemini · A2A) + MIT license badge.

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
