# PawConscious Mesh · Beast-Mode Submission Plan

**Locked:** 2026-05-22 (codex CLEAR)
**Deadline:** 2026-06-05 noon PT
**Days remaining:** 13
**Rule:** codex handshake after each section before moving on (Omar's directive)

---

## Why this plan exists

The 2026-05-21 submission audit (see `docs/SUBMISSION_AUDIT_2026-05-21.md`)
flagged: root page too dense (1,747 words), pricing scattered, no
single-agent-fails-mesh-corrects story, no Judge Mode overlay, Agent Engine
deployed but not in the default traffic path, no 3-min submission video.
Today's codex sweep confirmed the audit plus added: rewrite founder bio out
of the hero, make /agents curl actually runnable end-to-end with the
published demo key, add a Mandate Map table to /architecture.

## Rubric we are optimizing for (Track 3)

| Weight | Pillar     | What wins |
|--------|------------|-----------|
| 30%    | Tech       | Gemini + ADK + A2A + Cloud Run named explicitly, multi-agent collaboration shown |
| 30%    | Business   | B2B wedge clear, who pays, what they pay, why now |
| 20%    | Innovation | "Trust layer for agentic commerce" framing memorable in one sentence |
| 20%    | Demo       | 3-min video that a judge can comprehend without context |

Track 3 mandates (all required): B2B focus, Cloud Run runtime, Gemini,
A2A protocol. Already met.

Bonus the rules emphasize: multi-agent collaboration, Vertex AI Search +
Google Search grounding, cryptographic agent identity (Ed25519 + did:web,
already met), Agent Engine routing in traffic, Agent Simulation,
Observability, Marketplace listing posture.

## The single memorable sentence (codex 12-word headline)

> Signed proof for every product claim before any shopping agent recommends it.

(Older 17-word framing — "PawConscious is the check every AI shopping
agent should run before recommending a product to a human" — is
superseded. Codex picked the 12-word version for memorability under
Innovation 20%.)

## 13-day plan · 10 sections

Each section closes with a codex handshake (P0 findings block) before the
next section starts. After codex CLEAR, save a project memory entry per
Omar's "save memory per Move" rule.

### Section 1 · 2026-05-27 · `/` rewrite for judges

**Goal:** 1,747 words → 450-600 words. Top 20% = product proof + CTA.
Founder bio moves out of the hero band.

- Eyebrow rewrite: "Agentic Compliance Protocol" → "How AI shopping
  agents check a product claim"
- H1 stays: "The trust layer AI agents call before recommending a
  consumer product."
- Above the fold: H1 + sub + URL input + Verify CTA + signed-evidence
  trust line + 3 pills
- How-it-works step 02: trim from ~120 words to 2 sentences, link out
  to /architecture for depth
- Biz section: keep tier table + ROI single line; drop positioning
  prose block
- Delete: proof, moats, large founder section (these duplicate
  /architecture and /agents)
- Footer: keep + add compact founder credit + Track 3 badges

**Locked copy fixes (codex):**
- "Agentic Compliance Protocol" → "How AI shopping agents check a product claim"
- "Trust layer for agentic commerce" → "The check every shopping agent should run"
- "Powered by Gemini 2.5 Pro" → "Gemini 2.5 Pro runs the mesh"
- "Enterprise-grade" → "Built for teams that ship recommendations"

### Section 2 · 2026-05-28 · `/agents` curl actually runs

**Goal:** Developer can copy the curl block and get a real signed bundle
back using the published demo key `demo-key-2026-06`. End to end.

- Verify the curl example on the live URL with the published demo key
- Add a "deploy this on Gemini Enterprise" snippet that maps the agent
  card to Vertex AI Agent Engine
- Add Marketplace-listing posture line at the top of the page

### Section 3 · 2026-05-29 · `/architecture` Mandate Map

**Goal:** A Google ML engineer judge reads this and says "they get it."
Every Track 3 mandate maps to specific code in the repo.

- Add a Mandate Map table: mandate → file path → live endpoint
- 7-agent + 3-stage story already crisp; tighten any AI-marketing
  language per taste rules
- Wire the 7-agent diagram chips to deep-link into agents source

### Section 4 · 2026-05-30 · single-agent-fails-mesh-corrects scene

**Goal:** Rubric calls out "collaboration between agents leads to more
powerful and capable solution than a single agent could achieve."
Currently the demo cinematic narrates 4 agents in voice but does not
show the failure mode of a single Gemini call.

Example to script (codex locked):

> "Native Pet Calming Chews are vet-formulated and clinically proven to
> reduce anxiety by 60%."

- Single Gemini call: passes the claim through (no grounding, no FTC
  cross-check).
- Mesh path: evidence-grader fails to find a PubMed paper supporting
  the 60% number → vet-rubric scores 1/5 → compliance flags
  FTC §255.1 substantiation gap → auditor merges to FAIL → second-opinion
  surfaces FDA warning letter precedent.

Surface this directly in the demo scene 2 bento as a "single agent
shipped this. mesh blocked it" overlay.

### Section 5 · 2026-05-31 · Judge Mode overlay on `/demo`

**Goal:** A judge scrubbing the cinematic sees the tech stack labeled in
real time without leaving the page.

- Real-time labels on each scene 2 bento card:
  - claim-extractor card → "ADK LlmAgent"
  - evidence-grader card → "BioMCP → PubMed"
  - compliance card → "Vertex AI Search · FTC §255 corpus"
  - sign anchor → "Ed25519 + Firestore log"
  - cert-composer card → "Gemini 2.5 Pro"
  - second-opinion card → "Gemini + Google Search grounding"
- Toggle off by default; query param `?judge=1` turns it on.

### Section 6 · 2026-06-01 · Agent Engine in the traffic path

**Goal:** Currently `ACP_USE_AGENT_ENGINE=false`. Reasoning Engine is
deployed at
`projects/40952019806/locations/us-central1/reasoningEngines/1255381144908595200`
but not serving traffic. Flip it on for the demo path so the
`/health/agent-engine` badge reflects a live route.

- Wire the demo path to Agent Engine
- Keep the direct ADK path as the fallback for cost control
- Add observability: log span per agent call to Cloud Logging
- **Cold-start mitigation (codex Section 2 carry-over):** set
  Cloud Run `--min-instances=1` on `mesh-api` for the judging window
  (2026-06-04 evening to 2026-06-05 noon PT). Killed today's
  4-to-5-minute latency on cold paths.

### Section 7 · 2026-06-02 · 2:30 submission video

**Structure (codex final pick · live-demo-first):**
- 0:00–0:20 — Cold open. Real browser. Paste a URL. Real proof on screen
  (chain anchor + signed bundle).
- 0:20–0:45 — The collaboration wow. Single Gemini agent accepts the
  Native Pet 60% anxiety claim. Mesh blocks it: BioMCP species mismatch +
  FTC §255 flag on "vet-formulated" + "clinically proven". Signed verdict
  "Reject: not substantiated. Replace with 'Formulated with L-theanine.
  Evidence: limited.'" THIS is the wow scene.
- 0:45–1:30 — Continue live demo with Judge Mode overlays naming each
  tool as it fires (ADK, Vertex AI Search, Ed25519, A2A).
- 1:30–2:30 — Tech walkthrough. ADK + A2A + Cloud Run + Gemini + Vertex
  Search + Ed25519 + Firestore log named by name.
- 2:30 — B2B story + pricing + CTA.

**Production:**
- Real screen capture beats cinematic (judges want proof, not theater).
- Voice: real human if I record, else Antoni v2 settings.
- Music: minimal.
- 2:30 total. Forces discipline + harder to skip than 3:00.

**Failure mode at 0:30:** if a judge does not see Cloud Run + Gemini +
A2A on screen by second 30, they stop. The collaboration wow at 0:20
solves this AND lands Innovation 20%.

### Section 8 · 2026-06-03 · flip repo public + OSI license

**Goal:** Submission requires public open-source repo. Add OSI license,
polish README.

- Flip repo public
- MIT license at root
- README: hero diagram, quickstart with demo key, Track 3 mandate map,
  link to live URL + Devpost

### Section 9 · 2026-06-04 · Devpost text + credentials

- Devpost text description (feature, tech, data sources, findings)
- Login credentials: demo-key-2026-06 published on /agents
- Double-check live URL responds end to end

### Section 10 · 2026-06-05 · submit by noon PT

Final sweep:
- Live URL responds
- Repo is public
- Video is on YouTube/Vimeo public
- All team members listed on Devpost project
- Submit

## Deferred (write convincingly about, do not implement)

- Agent Simulation (Google-specific tool, called out in resource guide
  but not blocking)
- Agent Observability dashboards (mention Cloud Logging + per-agent
  spans in the README, do not build the dashboard)

## Surfaces audited today (codex)

| Page          | Words | Status                          |
|---------------|-------|---------------------------------|
| /             | 1,747 | Section 1 cuts to 450-600       |
| /agents       | 864   | Section 2 fixes curl + Marketplace |
| /architecture | 615   | Section 3 adds Mandate Map      |
| /demo         | n/a   | Sections 4 + 5 add fail-case + Judge Mode |

## Out of scope for the submission

- v2 personal teaser video (45s with Antoni + Lyria bed) — already
  shipped, kept for in-person pitches, NOT submitted
- /demo/shopper route — already deleted in v0.21.0
- Wellpaw + Goldenpaw mock brand jars — already shipped via gpt-image-1

## What gets handshake-reviewed by codex per section

- Code diff for the section
- Live URL screenshot after deploy
- Word count delta (Section 1) or rubric-pillar delta (Sections 2-9)
- Any taste violations: em dashes, AI marketing vocabulary, clinical
  jargon
