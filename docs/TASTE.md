# PawConscious taste rule-book

**Source:** Sarah Tavel, ["Taste"](https://saranormous.substack.com/p/taste). **Authored:** 2026-05-21. **Status:** v0. Every rule below has been earned in a shipped commit, not asserted.

Taste, in Tavel's framing, is *"the relentless, almost painful ability to know what should exist, what shouldn't, and where quality matters."* It compounds. Features can be copied; the feeling of using something built with intention cannot. This document encodes our point of view so every future change tests against it.

These rules apply to PawConscious Mesh code, copy, visual surfaces, demo, and any external surface a judge or buyer will encounter.

---

## The rules

### 1. No silent failures.

Every fallback surfaces in the API response or the rendered UI. `chain_anchor_status` is `"appended" \| "unavailable"`. `second_opinion` carries an `overall_verdict` and per-stress-test `tests[].verdict`. `/health/*` probes return the real failure mode. The user, or the downstream agent, never reads a null as success.

**Why:** Tavel: *"real taste hurts."* Hiding failures is the cheap path. Surfacing them is the disciplined one.

### 2. Internal honesty before external polish.

We say the orchestrator is `asyncio.gather`. We say 4-of-7 on ADK, not 7-of-7. We say the runtime stays asyncio while the ADK topology is the declared shape. We name the wedge as US DTC pet supplements before naming the platform vision.

**Why:** If the polish lands before the honesty, the work reads as hype. The order is honesty first. Then polish.

### 3. One primary CTA per page.

Product (`/`) = Verify your product. Developers (`/agents`) = Submit A2A task. Architecture (`/architecture`) = View a signed bundle in action. Demo (`/demo/shopper`) = Ask. No competing buttons. The U6 pass was this rule made code.

**Why:** Tavel: coherence over completeness. A page with three primary buttons has none.

### 4. Every claim points at a file, a URL, or evidence.

"4/7 on ADK" → [`/health/mesh-shape`](https://mesh-api-40952019806.us-central1.run.app/health/mesh-shape). "Real Ed25519" → [`/pcec/v0/chain/head`](https://mesh-api-40952019806.us-central1.run.app/pcec/v0/chain/head). "22 of 72 NIST RMF Playbook actions" → [`docs/NIST_AI_RMF_ASSESSMENT.md`](NIST_AI_RMF_ASSESSMENT.md). If a claim can't point at evidence, it goes in [`docs/FOLLOWUP_pre_flag_on.md`](FOLLOWUP_pre_flag_on.md) until it can.

**Why:** Tavel: *"respect your audience's intelligence."* A judge with three minutes does not read; they click.

### 5. Adversarial review before the next change.

Every change clears an adversarial review before the next one starts. Blocking findings must be resolved; lower-severity findings are absorbed or argued. The review is on the diff that exists, not the diff that is promised. Memory and reviews lag the code; only the diff itself is reviewable.

**Why:** Tavel: *"track delight debt alongside technical debt."* Adversarial review catches both. This is also our highest-leverage discipline. Eight rounds of adversarial reviews drove the 4/7 ADK split, the timeout absorption, the chain_anchor_status field, the BioMCP json-parse fix, the verifiability blanket-claim trim.

### 6. Dogfood the demo before a judge does.

Before any new `/demo/shopper` change ships, we run it end-to-end with the actual SKU in the URL bar. We watch the activity feed. We verify the bundle. If something feels off, we fix it before push. Same for `/architecture`, `/agents`, `/`. We are the first user.

**Why:** Tavel: *"use your product like customers do."* The B2B buyer will not. The judge will. The downstream agent will.

### 7. The behind-the-monitor pane is always visible.

We don't hide the calls. The A2A traffic feed, the bundle hash, the chain anchor, the topology JSON: judges and integrators see the wires. This is a pro-transparency posture, not a debug artifact. We are the kind of trust infrastructure that wants to be inspected.

**Why:** Tavel: *"coherence."* A trust mesh that hides its calls is incoherent with its own pitch.

### 8. Quality lives in the unsigned details.

`/agents` Errors table is accurate to actual handlers, not aspirational. `progress_message` phrasing distinguishes "appended" from "unavailable." The 422 row is reserved for FastAPI validation; the 400 row for semantic error. The eval runner treats anti-bot 406 as eligible because the page exists. The 4xx hard-dead codes (404 / 410) get skipped. These are the small things readers never notice and never forget.

**Why:** Tavel cites Stripe's plain-English error copy, Spotify's engineered randomness, Notion's hover-only drag handles. Taste reveals itself in the bottom 20% of the surface.

### 9. Same vocabulary across every surface.

ADK 4/7. asyncio.gather runtime. A2A v0.3 at the edge. PCEC v0.1 spec. did:web Ed25519. If `/`, `/agents`, `/architecture`, `/demo/shopper`, README, and Devpost disagree on a number or a name, we fix all of them in one commit. The R5 honest-language pass was this rule applied retroactively. We don't do it twice.

**Why:** Tavel: *"coherence compounds."* Inconsistency reads as carelessness even when it's just stale state.

### 10. No em dashes. No "thrilled." MIT founder voice.

Already locked in `feedback_writing_style`. Repeating here because taste lives in voice and a single em dash anywhere on a judge-visible surface breaks the spell. (See: this document's voice for the live example.)

**Why:** Tavel: error messages, loading states, voice. Generative AI is the most common source of em dashes in 2026. They tell on us.

### 11. Respect the judge's intelligence.

A judge has roughly three minutes per project. We do not bury the demo key in paragraph four. We do not make them grep for the curl. The README Quickstart runs in 30 seconds with one command. The Track 3 mandate map maps every mandate to a verifiable URL. The NIST RMF assessment opens with "Verdict in three sentences." We pay attention to where attention lands first.

**Why:** Tavel: *"respecting your audience's intelligence while remaining shameless about volume."* Aggressive distribution is fine. Wasting the recipient's first 30 seconds is not.

### 12. When in doubt, remove before adding.

The U4 pass collapsed 9 sections to 5 on `/`. A later pass compressed the Devpost copy from 2,462 words to 1,115. The "On the word mesh" paragraph kills a hype framing before it leaves us. Another pass moved 10 internal planning docs out of the repo root into `docs/internal/`. Subtraction is taste.

**Why:** Tavel: *"real taste is saying no to features that would triple your TAM."* Saying yes is the cheap mode of operation.

---

## Application order

When a new feature or surface is proposed, run the rules in this order:

1. **Mockup before code.** If the surface is visual, the brief and the render come before the HTML. Founder edits early or kills early.
2. **Honesty first.** Rule #2. Then internal review against #4 (every claim points at evidence).
3. **Coherence audit.** Rule #9. Does this new word, number, or pattern match every other surface that says the same thing? If no, fix all of them together.
4. **Subtraction pass.** Rule #12. Can this surface lose 25% of its words / sections / buttons and still hit the same point?
5. **Adversarial review.** Rule #5. Adversarial review before push.
6. **Dogfood pass.** Rule #6. Run it ourselves end-to-end with the canonical SKU.

If any step fails, back to step 1 with a sharper brief.

---

## Where this lives

This document is referenced from the repo guidelines so every contributor reads it. New rules land here only after they have been earned on a shipped change. Rules that turn out to be wrong get edited, not deleted; the original is preserved as a strikethrough so the history of judgment is legible.

Tavel's closing line is the standing brief: *"the feeling of using something crafted with intention, that's irreplaceable."* Everything in this repo is held to that.
