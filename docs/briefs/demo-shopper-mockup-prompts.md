# `/demo/shopper` mockup prompts (gpt-image-1)

**Purpose:** Generate three UI mockup variants for the redesigned `/demo/shopper` per `docs/briefs/demo-shopper-redesign.md`. Founder picks one before any HTML is touched.

**Model:** `gpt-image-1`. **Size:** `1536x1024` (matches 3:2 desktop viewport). **Quality:** `high`. **Cost:** ~$0.25 per render, 3 renders, $0.75 total. Well inside the $5 cap.

**Shared constraints** (applied to all three prompts):

- Dark theme. Background `#0A0B0D`. Surface `#111316`. Border `rgba(255,255,255,0.08)`. Ink `#EDEEF1`. Electric cyan accent `#00D4FF`.
- Sans-serif `Geist` for body. Monospace `JetBrains Mono` for code, JSON, hashes.
- A2A traffic pane is **always visible** (taste rule #7).
- One primary CTA: the `Ask` button. Everything else is secondary or chip-sized.
- Product context: Native Pet Hip+Joint Inflammatory Care.
- No em dashes in any visible label or copy.
- No fake browser chrome at the top. Real PawConscious global nav (the four-item nav we ship on every page: Product, Developers, Architecture, Demo).

---

## Variant A: "Terminal" — minimal change, maximum polish

> A clean dark UI mockup for a product page titled "PawConscious /demo/shopper." Two-pane horizontal layout. **Left pane (55% width):** an AI shopping copilot chat conversation. Header reads "Shopping copilot - powered by Gemini." Two messages visible: a user bubble on the right asking "Should I buy this for my senior dog with hip pain?" and an AI bubble on the left synthesizing a recommendation that mentions "PawConscious verdict: MIXED", "3 claims extracted", "3 FTC §255 flags", and ends with a short chain anchor hash like "sha256:27565e820d…" plus a tiny link "verify offline." Below the messages, three pre-baked example chips: "Senior dog with hip pain?", "Claims backed by evidence?", "Any FTC §255 issues?". At the bottom, a chat input field with placeholder "Ask anything about this product…" and a primary cyan `Ask` button. To the left of the Ask button, a small secondary outlined button "▶ Watch in voice mode (30s)." **Right pane (45% width):** a behind-the-monitor live A2A traffic console with the title "PAWCONSCIOUS MESH ACTIVITY — live A2A traffic." Lines of monospace text streaming, each prefixed with a timestamp like "21:46:24" in dim text, then a colored arrow ">" in cyan, then content like "POST /a2a/v1/tasks/send", "X-API-Key: demo-key-2026-06", "body: { tool: 'verify_claim', ... }", "HTTP 202 task_id=task-a9be7156…", "orchestrator: 7 agents on Cloud Run", "claim extraction (path=inline)", "evidence: BioMCP returned 8 papers", "second opinion delivered", "bundle_signature=Ed25519…", "chain_anchor=sha256:27565e…", "signed PCEC v0.1 bundle in Firestore." Subtle scanline texture. Bottom-right corner status: "task complete • verify on chain ↗". Top of page: the PawConscious global nav with four items (Product, Developers, Architecture, Demo) with Demo highlighted in cyan, and a "GITHUB ↗" button on the right. Aesthetic: enterprise developer console, taut, no clutter, terminal-grade. Reference: Linear settings page meets Stripe API docs.

---

## Variant B: "Conversation-first" — chat takes center stage, traffic pane is a collapsible drawer

> A modern AI assistant UI mockup for a product page titled "PawConscious /demo/shopper." **Top 65% of viewport:** a clean Gemini-style chat panel, centered, max-width 720px. The avatar is a soft cyan dot. Two messages visible: a user bubble (right, semi-transparent dark) asking "Should I buy this for my senior dog with hip pain?" and a Gemini-styled response (left, lighter dark with subtle gradient border) that says: "I checked the claims on this listing with PawConscious — they're an independent A2A trust mesh. **Verdict: MIXED.** Three claims extracted. Three FTC §255 flags raised. Some hold up, others are softer than the label suggests. I'd buy cautiously. Signed evidence anchor sha256:27565e820d… verify offline." Below the messages, three pre-baked chips: "Senior dog with hip pain?", "Claims backed by evidence?", "Any FTC §255 issues?". A chat input below with placeholder "Ask anything about this product…" and one primary cyan `Ask` button. To the right of the Ask button, a small secondary `▶ Watch voice mode (30s)`. **Bottom 35% of viewport:** an expandable drawer titled "PAWCONSCIOUS MESH ACTIVITY · live A2A traffic" already in expanded state, showing the same streaming monospace log as Variant A: timestamps in dim, arrows in cyan, A2A POST headers, task_id, orchestrator topology, claim extraction, second opinion delivered, bundle hash, chain anchor. A small chevron icon in the top-right of the drawer suggests it can collapse. Top of page: the PawConscious global nav (Product, Developers, Architecture, Demo) with Demo active in cyan, plus a "GITHUB ↗" button on the right. Aesthetic: cleaner and more consumer-facing than Variant A. Conversational primary, technical receipt secondary. Reference: ChatGPT inspector panel below the conversation.

---

## Variant C: "Stage" — chat is the spotlight, traffic pane is a side-rail that activates when the tool fires

> A cinematic dark UI mockup for a product page titled "PawConscious /demo/shopper." Three-zone layout. **Center stage (60% width):** a chat conversation rendered with extra padding and breathing room, like a stage. Title above the chat reads "Shopping copilot — Gemini calls PawConscious through A2A v0.3" (use a colon instead of an em dash). Two messages: user bubble right ("Should I buy this for my senior dog with hip pain?") and an AI bubble left synthesizing the recommendation with the same content (MIXED verdict, 3 claims, 3 FTC §255 flags, chain anchor hash, verify-offline link). Three example chips below. Chat input + cyan `Ask` button at the bottom of the center column. Secondary `▶ Watch voice mode (30s)` button. **Right side-rail (28% width):** the A2A traffic log, narrower than in A or B, with a slight glow effect on the active line being streamed. Title "MESH ACTIVITY · A2A v0.3" in small caps. Monospace lines as before. The glow effect on the most recent line makes it feel live. **Left side-rail (12% width):** a thin Track 3 mandate strip showing six small badges stacked vertically — "Gemini ✓", "ADK 4/7 ✓", "A2A v0.3 ✓", "Cloud Run ✓", "Vertex AI ✓", "Ed25519 ✓" — each with a tiny check icon. Top of page: the global nav (Product, Developers, Architecture, Demo) with Demo highlighted, "GITHUB ↗" right. Aesthetic: spotlight on the chat, evidence on both sides. The traffic pane is a transparent receipt running in the background, not a debug terminal. Reference: Apple keynote slide showing a product running with metadata floating around it.

---

## Founder edit prompt

When you (Omar) see the three renders, evaluate against:

- **Taste rule #7** (behind-the-monitor pane always visible — all three satisfy)
- **Taste rule #3** (one primary CTA — all three put Ask as the only primary)
- **Taste rule #12** (subtraction — Variant C adds the left mandate strip; is that earning its space or clutter?)
- **Taste rule #11** (respect judge intelligence — which one is most readable at first glance for a 3-minute judge?)

Pick one. Or kill all three and tell me what was wrong; I rebrief.

---

## Cost log

- Attempted: gpt-image-1 with restricted-scope `OPENAI_API_KEY` → 401, scope missing `api.model.images.request`. Zero spend.
- Fallback: Vertex AI Gemini via ADC. Tried `gemini-3-pro-image-preview` and variants (all 404 NOT_FOUND in our project/region). Fell back to `gemini-2.5-flash-image` (Nano Banana). 3 renders generated successfully. Sub-cent spend per render against the Vertex billing.
- Cap remaining: $5 effectively untouched. The $0.75 budget envelope for gpt-image-1 stays available for a future re-render once a wider-scope key is provisioned.

## Founder pick (2026-05-21)

**Variant B selected.** Rationale (graded against `docs/TASTE.md`):

- Wins **rule #11** (judge intelligence): top-down conversation-first layout reads in 10-15 seconds. Variant A asked the eye to ping-pong across panes (~30s for a tech judge, longer for a non-tech one). Variant C asked it to triangulate three zones (~40s+).
- Wins **rule #3** (one primary CTA): Ask button isolated, no competing visual elements. Variant C's left mandate-badges rail competed for visual attention.
- Ties **rule #12** (subtraction) with A at 2 zones; C's 3-zone layout failed.
- The "shoiper" typo in the mockup is a Nano Banana rendering artifact, not a design flaw. Disappears in HTML.
- C's wins on rule #8 (glow on active line) and rule #9 (most accurate header) are taken as inspiration for the implementation, not as reasons to flip variants. The active-line glow lands in B's drawer. The "Gemini calls PawConscious through A2A v0.3" framing lands in B's header.

Next step: implement Variant B as the new `services/mesh_api/static/shopper-demo.html` + a new server route `POST /demo/shopper/llm` (ADC-auth Vertex AI Gemini with `verify_claim` registered as a tool). Localhost iterate before push.
