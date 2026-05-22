# Brief: `/demo/shopper` redesign

**Status:** v0 draft for founder edit. Not committed. No code yet. **Author:** Claude. **Date:** 2026-05-21.

**Source decision:** "Default text, plus a Watch in voice mode button that plays a pre-recorded 30s clip" (Omar, 2026-05-21).

**Audience:** Track 3 hackathon judge clicking the Devpost link with 3 minutes of attention. Secondary: B2B buyer (General Counsel, Compliance, AI-shopping platform team) sent the link by a salesperson.

---

## What this surface is for

`/demo/shopper` is the **proof that PawConscious works agent-to-agent**. A judge should land on the page and within 90 seconds understand:

1. An external AI agent (Gemini, in this demo) is talking to PawConscious through the public A2A protocol.
2. Gemini decided to call PawConscious autonomously because it needed to verify product claims before recommending.
3. PawConscious returned a signed evidence bundle Gemini can synthesize against.
4. The whole exchange is verifiable: anchor hash, signature, did:web identity.

The current page does point 1 partially (the mesh call is real) but the "Gemini" voice is a hardcoded JS shell. We are fixing that.

## Two modes on the same page

### Mode A: text (default, what judges land on)

A two-pane layout, same as today:

- **Left pane: chat.** User types a question. Gemini answers using the PawConscious tool. Real Gemini API call. Real tool-use turn that calls our A2A endpoint. Real bundle synthesis.
- **Right pane: behind-the-monitor.** Live A2A traffic log. The exact JSON tool-call Gemini emits, the exact JSON our mesh returns, the chain anchor, the bundle hash, the signature.

User can either type their own question or click one of three pre-baked example chips:

- *"Should I buy this for my senior dog with hip pain?"*
- *"Are the joint mobility claims actually backed by evidence?"*
- *"Any FTC §255 issues with this product?"*

The canonical product is Native Pet hip-joint (the one we have a committed sample bundle for at `demo/captures/live-mesh-call-2026-05-18-native-pet.json`).

### Mode B: "Watch in voice mode" button

A single button labeled **"Watch this in voice mode (30s)"** sits next to the chat input. Click it: a modal opens, the pre-recorded video plays. 30 seconds. Founder + canonical SKU, voice-in voice-out via Gemini Live, same A2A traffic visible on screen.

Modal closes, user back to text mode. No mic permission ever requested.

## The three required moments (visible in both modes)

These are the beats every judge has to leave with seared in:

| # | Moment | Visible where |
|---|---|---|
| 1 | **Gemini decides to call PawConscious.** The tool-call JSON appears in the right pane. Words like `tool: "verify_claim"` and `product_url: "..."` are scannable. | Right pane (text mode) + screen overlay (voice video) |
| 2 | **PawConscious mesh runs.** The orchestrator topology streams in the right pane: claim_extractor → ParallelAgent[evidence, vet, compliance] → auditor → sign → second_opinion. Real time. | Right pane both modes |
| 3 | **Signed bundle returns, Gemini synthesizes the recommendation citing the bundle.** Left pane gets the verdict with the chain anchor short-hash inline + "verify offline" link to `/.well-known/did.json`. | Left pane both modes |

## Taste rule check (preflight before any code)

Cross-reference every constraint against `docs/TASTE.md`:

- **#1 No silent failures.** If Gemini rate-limits or mesh times out, the right pane says exactly that. Left pane refuses to recommend. No fake-success.
- **#2 Internal honesty.** The right pane shows real JSON, not stylized stub. The left pane never claims more than the bundle supports.
- **#3 One primary CTA.** The Ask button is primary. "Watch voice" is secondary (smaller, lower contrast). Example chips are tertiary.
- **#4 Every claim points at evidence.** The verdict includes the chain anchor short-hash + `/.well-known/did.json` link. Judge can verify offline.
- **#5 Codex handshake.** Will run after implementation, before push.
- **#6 Dogfood.** Founder runs the canonical question end-to-end before push.
- **#7 Behind-the-monitor pane always visible.** Right pane never collapses or hides on this surface.
- **#8 Quality in details.** Empty state ("ask anything about this product…"), loading state (the streaming JSON tool-call), error state (Gemini fails, mesh fails, both fail).
- **#9 Same vocabulary.** "A2A v0.3", "4-of-7 on ADK", "chain anchor", "did:web" all match README + `/architecture` + Devpost.
- **#10 No em dashes, no "thrilled".**
- **#11 Respect judge intelligence.** 90-second comprehension target.
- **#12 Subtraction.** No competing CTAs. No third pane. No tabs. No tour overlay.

## Input shape (what real Gemini receives)

```
System instruction: You are an AI shopping copilot helping a buyer evaluate
pet supplements. You have one tool available: verify_claim, which calls
PawConscious Mesh (a public A2A v0.3 agent at
https://mesh-api-40952019806.us-central1.run.app/a2a/v1/tasks/send)
to get an independent evidence audit on a product URL. Use the tool
before making any recommendation. Cite the bundle's chain anchor in
your final answer. If the bundle says NEEDS REVIEW or carries §255
violation flags, do not recommend without escalation.

Tool definition (Gemini function-calling shape):
{
  "name": "verify_claim",
  "description": "Get an independent evidence audit from PawConscious",
  "parameters": {
    "type": "object",
    "properties": {
      "product_url": {"type": "string"},
      "max_claims": {"type": "integer", "default": 3}
    }
  }
}

Initial context: The current product is Native Pet Hip+Joint Inflammatory
Care: https://www.nativepet.com/products/hip-joint
```

When the user asks anything, Gemini reads the system prompt, decides whether to call `verify_claim`, fires the tool call. Our server-side handler intercepts the tool call, fires the real A2A POST to mesh-api, polls for completion, returns the signed bundle JSON back to Gemini as the tool response. Gemini then synthesizes the recommendation.

## Stack choices (subject to founder edit)

- **Gemini API.** `gemini-2.5-pro` with function-calling. Streaming on for the synthesis (judge watches text fill in real-time).
- **Tool-call routing.** New FastAPI endpoint on the mesh service: `POST /demo/shopper/llm` that takes the user message, calls Gemini with the tool definition, intercepts tool calls, calls the public A2A endpoint, returns the streamed response. This keeps the demo callable from any browser without exposing the Gemini API key to the client.
- **Voice video.** Recorded once. Stored at `services/mesh_api/static/assets/voice-mode.mp4`. Plays inline in a modal. No external streaming dependency.

## Outputs of this brief

1. **Three UI mockup variants** of the new two-pane layout, 1280x800, generated via gpt-image-1. Founder picks one or kills all three and we rebrief.
2. **A 30-second voice video script + storyboard** for the recorded clip. Will be rendered via O22 pipeline (Gemini script → Veo for screen capture overlay → ElevenLabs founder VO → Lyria bed). One pack, founder picks the cut.
3. **The new `services/mesh_api/static/shopper-demo.html`** plus a new server route `POST /demo/shopper/llm`.

Each output gets a separate codex handshake.

## Acceptance criteria (judge dogfooding test)

A judge who lands on `/demo/shopper` cold should:

- ✅ Understand within 30 seconds what the page is doing.
- ✅ Click "Ask" on a pre-baked chip and see real A2A traffic stream in under 5 seconds.
- ✅ See a signed bundle + chain anchor land within 90 seconds.
- ✅ Be able to verify the bundle offline by clicking the did.json link.
- ✅ Click "Watch in voice mode" and see the 30-second clip without leaving the page.
- ✅ Leave the page able to describe what just happened to a colleague.

Each ✅ is a manual check before push.

## Open inputs (Omar to answer before I write code)

1. **Gemini API key.** Where does it live? Env var name on Cloud Run? Or do you set it in Secret Manager and I read it from there? I need it server-side, not client-side.
2. **gpt-image-1 access.** Do I run the mockup-generation API myself (give me a key + budget cap) or do you fire it from your local image-gen flow and paste back PNGs?
3. **O22 run authority.** When we get to the voice video, can I run `python validation/render_pack.py --brief <brief.yaml>` against your O22 GCP billing? It's ~$3.83 per pack. Or do you drive that step?
4. **Native Pet vs second SKU.** Sticking with `nativepet.com/products/hip-joint` as the canonical, or adding a second product the user can toggle to? Adds polish, doubles mesh-call cost on each visit.

Once those four are answered, I write the brief into a yaml O22 can ingest (for the voice video later) and the gpt-image-1 prompts (for the UI mockups now). Founder edit, then code.

---

## Acknowledgments

This brief was drafted against `docs/TASTE.md` v0. If a rule there changes, this brief recompiles against the new rule before any work continues.
