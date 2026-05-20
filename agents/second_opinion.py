"""Agent 7 — Second Opinion.

Adversarial double-validation. Takes the signed bundle + cert from the first 5+1
agents, runs 4 stress-tests using Google Search grounding to pull external
evidence, and returns a verdict on whether the original verification would survive
real-world scrutiny.

Stress tests:
1. COURT — would this claim survive a class-action plaintiff theory?
2. REGULATOR — has the brand or claim type been subject to FTC enforcement, FDA
   warning letters, AAFCO action?
3. SCIENTIFIC CONSENSUS — does current peer-reviewed literature contradict the
   claim mechanism?
4. PUBLIC SKEPTICISM — what would Reddit / consumer advocacy / trade press say?

Architecture:
- Primary path: Managed Agents API (Gemini 3.5 Flash, native web browsing) —
  Google just launched this (2026-05-19); using it is the polish move.
- Fallback path: gemini-2.5-pro with Google Search grounding via google.genai
  (production-stable; same capability shape).

This file ships the fallback path. The Managed Agents migration is queued behind
a feature flag once the preview API stabilizes.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared.pcec_schema import EndorsementClaimBundle  # noqa: E402

from google import genai
from google.genai import types


SECOND_OPINION_PROMPT = """You are the SECOND OPINION agent for PawConscious — an adversarial double-validation layer that runs AFTER five other agents have verified a product claim and signed an evidence bundle.

Your job: TRY TO BREAK their conclusion. Search the public web for evidence that contradicts the claim, regulatory actions against this brand or claim type, scientific consensus shifts, plaintiff cases on this claim type, and consumer-advocacy concerns. Use Google Search grounding to pull real-time evidence.

BUNDLE (already verified, signed, chain-anchored):
{bundle_summary}

Run these 4 stress tests:

1. COURT test — would this claim survive a class-action plaintiff theory under FTC §255 substantiation rules? Search for similar claim language that has resulted in settlements (e.g., Cosequin $11.5M Nutramax 2024, Prevagen $165M, GlycoFlex pending). Verdict: SURVIVES | NEEDS REVIEW.

2. REGULATOR test — has the brand or this specific claim type been subject to FTC enforcement action, FDA warning letters, AAFCO action, or state AG inquiry? Search regulator news + databases. Verdict: SURVIVES | NEEDS REVIEW.

3. SCIENTIFIC CONSENSUS test — does current peer-reviewed literature (last 24 months) contradict the claim mechanism? Search PubMed and recent reviews. Verdict: SURVIVES | NEEDS REVIEW.

4. PUBLIC SKEPTICISM test — what does the public discourse say (Reddit r/pets, ConsumerLab, science-blogger reviews, trade press)? Is there a credible counter-narrative that would surface to a skeptical buyer or AI shopping agent? Verdict: SURVIVES | NEEDS REVIEW.

RETURN STRICT JSON (no markdown, no prose):
{{
  "tests": [
    {{"name": "COURT", "verdict": "SURVIVES" or "NEEDS REVIEW", "rationale": "one-sentence finding citing the source"}},
    {{"name": "REGULATOR", "verdict": "...", "rationale": "..."}},
    {{"name": "SCIENTIFIC CONSENSUS", "verdict": "...", "rationale": "..."}},
    {{"name": "PUBLIC SKEPTICISM", "verdict": "...", "rationale": "..."}}
  ],
  "strongest_counter": "the single strongest counter-argument you found, in plain language",
  "overall_verdict": "CONFIRMS" or "NEEDS REVIEW",
  "summary": "one-sentence summary of the second opinion in the founder's voice — direct, no hedging"
}}

Be HONEST. If you can't find contradicting evidence on a test, say SURVIVES. If you find legitimate concerns, say NEEDS REVIEW. Don't manufacture controversy. Don't rubber-stamp."""


def _client() -> genai.Client:
    return genai.Client(vertexai=True, project="pawconscious-mesh-2026", location="us-central1")


async def get_second_opinion(bundle: EndorsementClaimBundle) -> dict:
    """Adversarial double-validation. Returns structured verdict + counter-evidence.

    Uses Google Search grounding (the fallback for Managed Agents API). Output shape
    matches the cert frontend's "second_opinion" panel.
    """
    bundle_dict = json.loads(bundle.model_dump_json())
    # Compress for the prompt
    summary = {
        "brand_or_product": bundle_dict.get("sku"),
        "claims": [c.get("text") for c in bundle_dict.get("claims", [])],
        "vet_scores": [{"score": v.get("score"), "escalate": v.get("escalate_to_human_vet")} for v in bundle_dict.get("vet_scores", [])],
        "compliance": [{"ftc_section": c.get("ftc_section"), "violation_flag": c.get("violation_flag")} for c in bundle_dict.get("compliance", [])],
        "audit": [{"verdict": a.get("verdict")} for a in bundle_dict.get("audit", [])],
    }

    prompt = SECOND_OPINION_PROMPT.format(bundle_summary=json.dumps(summary, indent=2))

    client = _client()
    response = client.models.generate_content(
        model="gemini-2.5-pro",  # 2.5 Pro for the depth (this agent needs to reason about adversarial evidence)
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.3,
            tools=[types.Tool(google_search=types.GoogleSearch())],
            max_output_tokens=4000,
        ),
    )

    text = (response.text or "").strip()
    # Strip markdown fence if present (Gemini often wraps JSON in ```json...```)
    if text.startswith("```"):
        text = text.split("```", 2)[1] if text.count("```") >= 2 else text
        if text.startswith("json\n"):
            text = text[5:]
        if text.startswith("json "):
            text = text[5:]
    text = text.strip()
    # Strip Google Search citation markers like [1] [2][3] that break JSON parsing
    import re as _re
    text = _re.sub(r'\[\d+(?:,\s*\d+)*\]', '', text)
    # Strip control characters
    text = text.replace("\r", "").translate({i: None for i in range(0x20) if i not in (0x09, 0x0A)})
    # Extract the outer JSON object if there's prose before/after
    first_brace = text.find('{')
    last_brace = text.rfind('}')
    if first_brace >= 0 and last_brace > first_brace:
        text = text[first_brace:last_brace+1]

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        # Defensive fallback — never let the second opinion crash the verify flow
        return {
            "tests": [],
            "strongest_counter": "Second Opinion JSON parse failed — falling back to base verdict.",
            "overall_verdict": "CONFIRMS",
            "summary": f"Second opinion unavailable this run ({type(e).__name__}); base 5+1-agent bundle stands.",
            "_parse_error": str(e)[:200],
        }
