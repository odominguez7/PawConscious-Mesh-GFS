"""Claim Extractor Agent (PRODUCTION-quality per declared depth in PLAN.md §2).

Takes a product detail page URL, fetches the page, and extracts every health/efficacy
claim using Gemini reasoning. Returns a structured list of Claim objects per PCEC v0.1.

Per codex G8 Phase 2 blocking risk: PDP fetch may be blocked by anti-bot. Simple
httpx + BeautifulSoup primary path; fall back documented in docs/agents/claim-extractor.md.

Model: gemini-2.5-pro (GA). Upgrade path to gemini-3-pro on Vertex AI GA.
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

import httpx
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared.pcec_schema import Claim, ClaimKind  # noqa: E402

# ADK + Vertex imports
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool


PDP_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


async def fetch_pdp_html(url: str) -> str:
    """Fetch a product detail page and return cleaned text content.

    Strips scripts/styles, keeps headings + body text. If the fetch fails (403, 429,
    timeout), raises an exception the agent can report back honestly.
    """
    headers = {
        "User-Agent": PDP_USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        html = response.text

    soup = BeautifulSoup(html, "lxml")
    # Strip script / style / nav / footer noise
    for tag in soup(["script", "style", "noscript", "nav", "footer", "header"]):
        tag.decompose()

    # Keep only main content; many PDPs have <main> or product detail divs
    main = soup.find("main") or soup.find(attrs={"role": "main"}) or soup.body
    if main is None:
        return soup.get_text(separator="\n", strip=True)[:20000]

    text = main.get_text(separator="\n", strip=True)
    # Truncate to avoid blowing context window
    return text[:20000]


CLAIM_EXTRACTION_PROMPT = """You are the claim-extractor agent in the PawConscious Mesh / ACP system.

Your job: read a pet supplement product detail page (PDP) and extract every health or efficacy claim made about the product.

A "claim" is any statement that implies the product produces a specific health, behavioral, or physiological effect on the pet. Examples:
- "Supports joint mobility in senior dogs"  → efficacy
- "Promotes a calm demeanor"                 → efficacy
- "Veterinarian formulated"                  → expert
- "Made in USA from organic ingredients"     → provenance + ingredient
- "10x absorption vs other brands"           → performance
- "Safe for puppies"                         → safety

For each claim found:
1. Quote the exact text from the page
2. Classify the kind: efficacy / safety / ingredient / expert / provenance / performance
3. Note where on the page it appeared (hero / bullets / description / fine print)
4. Include 1-2 sentences of surrounding context

Return a JSON list of claims. If no claims found, return an empty list and explain why.

Be EXHAUSTIVE — capture every claim, including subtle implied ones (e.g. "your dog's secret to a happy gut" implies digestive efficacy).
Be HONEST — do not invent claims that aren't on the page.

PDP CONTENT:
---
{pdp_text}
---

Return ONLY valid JSON in this shape (no markdown, no commentary):
{{
  "claims": [
    {{
      "text": "...",
      "kind": "efficacy",
      "position_on_page": "hero / bullets / description / fine_print / other",
      "raw_context": "..."
    }}
  ]
}}
"""


def build_claim_extractor_agent() -> LlmAgent:
    """Build the claim-extractor ADK LlmAgent."""

    fetch_tool = FunctionTool(fetch_pdp_html)

    agent = LlmAgent(
        name="claim_extractor",
        model="gemini-2.5-pro",
        description=(
            "Extracts every health/efficacy claim from a pet supplement product detail page. "
            "Production-quality agent per PLAN.md §2. Returns structured PCEC Claim objects."
        ),
        instruction=(
            "When called with a product URL, use the fetch_pdp_html tool to retrieve the page text. "
            "Then carefully extract every claim per the schema. Return ONLY valid JSON, no markdown."
        ),
        tools=[fetch_tool],
    )
    return agent


async def extract_claims(url: str) -> list[Claim]:
    """High-level wrapper: URL in, list[Claim] out.

    Standalone helper for testing without the full ADK runtime — used by Phase 2 verification.
    """
    pdp_text = await fetch_pdp_html(url)

    # Direct Gemini call for standalone testing
    from google import genai
    from google.genai import types

    client = genai.Client(vertexai=True, project="pawconscious-mesh-2026", location="us-central1")

    prompt = CLAIM_EXTRACTION_PROMPT.format(pdp_text=pdp_text)

    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.0,
        ),
    )

    payload = json.loads(response.text)
    # Gemini sometimes returns a top-level list vs {"claims": [...]}
    if isinstance(payload, list):
        raw_claims = payload
    elif isinstance(payload, dict):
        raw_claims = payload.get("claims", [])
    else:
        raw_claims = []

    claims: list[Claim] = []
    for raw in raw_claims:
        kind_str = raw.get("kind", "efficacy").lower()
        try:
            kind = ClaimKind(kind_str)
        except ValueError:
            kind = ClaimKind.EFFICACY  # fallback
        claims.append(Claim(
            text=raw.get("text", ""),
            kind=kind,
            position_on_page=raw.get("position_on_page"),
            raw_context=raw.get("raw_context"),
        ))

    return claims


async def main() -> None:
    """Phase 2 verification: extract claims from a real Honest Paws PDP."""
    # Native Pet Hip & Joint — verified live PDP
    test_url = "https://www.nativepet.com/products/hip-joint"

    print(f"Fetching: {test_url}")
    try:
        claims = await extract_claims(test_url)
    except httpx.HTTPStatusError as e:
        print(f"HTTP error fetching PDP: {e}")
        # Fallback to a different real DTC pet brand
        alt_url = "https://www.honestpaws.com/products/calm-soft-chews-for-dogs"
        print(f"Falling back: {alt_url}")
        claims = await extract_claims(alt_url)

    print(f"\nExtracted {len(claims)} claims:")
    for i, c in enumerate(claims, 1):
        print(f"\n{i}. [{c.kind.value}] {c.text}")
        if c.position_on_page:
            print(f"   position: {c.position_on_page}")
        if c.raw_context:
            print(f"   context: {c.raw_context[:120]}...")


if __name__ == "__main__":
    asyncio.run(main())
