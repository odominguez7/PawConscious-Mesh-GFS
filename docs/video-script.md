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

## CAPTURE PLAN — v0.10.1 LIVE HERO (locked 2026-05-21 per codex A-codex-11)

Move I capture against the rebuilt hero at https://mesh-api-40952019806.us-central1.run.app/. This section locks the live-shoot workflow so the video doesn't get derailed by Cloud Run cold-start or live-mesh timing variance.

### Pre-shoot warm-up (T-3min before recording starts)

1. Open a private terminal tab. Curl `/health` 3× with the budget below to defeat Cloud Run cold-start. The first hit blocks until cold-start completes (typically ~90-180s on `min-instances=0`); calls 2 and 3 land in <300ms each. **Capture must start ONLY after the third curl returns sub-second** — that's the proof the service is warm. Budget at least 3 minutes for the full warm-up cycle.

   ```bash
   # Run this 3+ minutes before recording. First call blocks; subsequent are fast.
   time curl -s -o /dev/null -w "1: %{http_code} %{time_total}s\n" \
     "https://mesh-api-40952019806.us-central1.run.app/health"
   sleep 5
   time curl -s -o /dev/null -w "2: %{http_code} %{time_total}s\n" \
     "https://mesh-api-40952019806.us-central1.run.app/health"
   sleep 5
   time curl -s -o /dev/null -w "3: %{http_code} %{time_total}s\n" \
     "https://mesh-api-40952019806.us-central1.run.app/health"
   ```

   Calls 2 and 3 must both return < 0.5s before you start recording. If they don't, wait 30s and retry from call 1.

2. Open the live URL in a fresh Chrome window at 1440×900 (NOT 1920×1080 — the hero's max-content reads cleaner at 1440, and matches the 16:9 frame Veo defaults to). Disable scroll bars (`overflow:hidden` on `<html>` via DevTools or use a clean profile).

3. Pre-click the URL input and confirm the JustFoodForDogs PDP URL is pre-filled (it is, as of v0.10.0c). DO NOT click Verify yet.

4. Hover the **Verify your product** button briefly — the 7-chip preview pulses for ~800ms. This is the "first 10 seconds" cue and should appear in the video's intro.

### Primary path — live JFFD audit (1:30 - 9:30 of wall-clock, ~7-9 min)

The live audit takes ~547s on a warm mesh. Real run produces real findings (2018 FDA Listeria recall via Second Opinion, weak L-Tryptophan evidence). Capture this end-to-end ONCE, then edit:

1. **0:00 - 0:05** — Static landing. Trust anchor visible above Verify. Hover Verify (preview chips flash) → click. Cyan perimeter starts pulsing immediately. **Stage 1 cinema card slides in from top-right.**

2. **0:05 - 5:30** — Live mesh polling. Stream emits 1-2 progress messages then heartbeat every ~9s. Cyan perimeter holds during the entire reasoning phase. The on-screen elapsed timer in the coverage line ticks up. **This section will be sped up 8× in editing**; the narrator beat fills the silence ("the agents are running real PubMed retrieval, real FTC §255 grounding…").

3. **5:30 - 5:45** — Backend transitions to signing. Live `progress_message` flips to "signed". **Moss-green dramatic flash on perimeter (~3s).** Stage 2 cinema card overlays centered: "SIGNING ✦ Ed25519 · canonical JSON · chain anchor → Firestore."

4. **5:45 - 9:15** — Stage 3 polling for Agent 6 + Agent 7. Cert composer delivers first (~4.6KB cert HTML). Second Opinion delivers next with the 4 stress tests. **Violet perimeter pulse · Stage 3 card top-left fills in test-by-test:** COURT ✓ SURVIVES · REGULATOR ⚠ NEEDS REVIEW (2018 Listeria recall) · CONSENSUS ⚠ NEEDS REVIEW (L-Tryptophan weak) · PUBLIC ⚠ NEEDS REVIEW.

5. **9:15 - 9:30** — Final state. Amber perimeter (FAIL/NEEDS REVIEW). Cert pane drops in with "JustFoodForDogs · Calming Efficacy & Ingredient Claims · FAIL" headline. Coverage line: "Verified 3 of 3 claims · NEEDS REVIEW · signed bundle below". Stage cinema cards cleared.

### Fallback — cached replay (if live stalls or errors mid-recording)

If the live audit stalls > 3 min without progress, OR if Cloud Run cold-start adds > 4 min to the wait:

1. Press F5 to reload the page.
2. Click **▶ Replay cached demo** (button in the coverage row). ~12s wall-clock cycle.
3. The cached cycle replays the verbatim JustFoodForDogs audit (same URN, same FAIL verdict, same Second Opinion findings). It is **honest theater**: the mode badge clearly says `▶ CACHED` (violet) and the coverage line says "Cached cycle running · pre-recorded data".
4. **Narrator must say**: "We're skipping the 9-minute wait with a pre-recorded replay — every byte you see here came from a real run, signed and chain-anchored, URN visible at the end."

### Aspect ratios + motion timing

- Desktop primary cut: **1440×900** (16:9). Captures the full hero grid + diagram + cert prominence.
- Vertical mobile cut: **720×1280** (9:16). The mobile breakpoint at 720px stacks the experience cleanly per codex A-codex-7 — diagram + cert visible without cropping.
- Motion: **stage cinema cards last ≥3 seconds each** so the video editor can extract clean clips. Verified in the v0.10.1c CSS (transitions @ 350ms enter/exit, dwell ~3000-4200ms per stage in cached cycle).

### Narration beats (v0.10.1 vocabulary, codex-cleared)

Replaces the v0.8.x narration block in this same doc above. Use these exact phrasings — they pass the honesty regression test in `tests/test_cert_honesty.py`:

- ❌ "the veterinary panel" → ✅ "the AI vet-rubric simulation"
- ❌ "vet panel runs a five-vet rubric" → ✅ "the AI vet-rubric simulation runs a five-vet rubric — Gemini role-playing five vets; v0.2 replaces this with licensed-DVM attestation"
- ❌ "verified citations exist" → ✅ "the Falsifier auditor cleared PMID-format checks on every citation"
- ❌ "FDA approved" → ✅ "FTC §255 substantiation check (Vertex AI Search grounded)"

### Capture checklist (run through this before hitting record)

- [ ] mesh-api `/health` returns < 300ms (pre-warmed)
- [ ] Chrome at 1440×900, scroll bars hidden
- [ ] URL input has the JFFD product URL pre-filled
- [ ] Stage cinema cards animations confirmed working (hover Verify → preview chips flash in sequence)
- [ ] /devex-review boomerang scorecard ≥ 7.5/10 (currently 8.0)
- [ ] Cached replay flow verified (fallback path) — `▶ Replay cached demo` button visible in coverage row
- [ ] Audio environment quiet (Lyria + VO mix done in post)
- [ ] OBS / ScreenFlow recording at 60fps minimum
- [ ] Backup browser tab on a different revision in case rollback needed mid-shoot

### What NOT to do during the live shoot

- Don't click anything else during the 60-180s wait — the coverage line + heartbeat is the entire visible state. Trust the visual.
- Don't refresh the page during a live run — task_store is in-memory on Cloud Run; refresh = lose the in-flight task ID.
- Don't try to verify a DIFFERENT URL during the shoot — JFFD is the locked demo URL because it FAILS with substantive findings (Listeria recall, weak evidence). A passing claim is a less compelling video.
- Don't shoot before /devex-review baseline reruns at 7.5+. If the v0.10.1+ hero ever regresses below that score, fix first.

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
