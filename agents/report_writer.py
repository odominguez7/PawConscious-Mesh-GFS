"""Agent 6 — Cert Composer / Report Writer.

Post-merge agent that takes the signed EndorsementClaimBundle and writes a
brand-themed executive verification cert in HTML.

Model: gemini-2.5-flash-002 (fast, cheap, good at HTML gen). Bumps to
gemini-3.5-flash after A/B eval passes (per WIN_PLAN Day 4).

Runs AFTER the bundle is signed but BEFORE the response returns. Output
attaches to task_store as `cert_html`. Frontend renders it in the cert pane
instead of the static template.

Determinism: temperature=0.2 (slight variation OK for narrative; cert content
is deterministic given the same bundle).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared.pcec_schema import EndorsementClaimBundle  # noqa: E402

from google import genai
from google.genai import types


CERT_PROMPT = """You are PawConscious — an agentic compliance protocol for DTC consumer brands.

You have just signed an evidence bundle for the following product. Compose a tight executive verification cert in HTML.

BUNDLE (JSON):
{bundle_json}

INSTRUCTIONS:
1. Output a SINGLE HTML fragment (no <html>, <head>, <body> — just the cert markup). It will be inserted into a dark-mode dashboard with these CSS variables already defined:
   --ink: white-ish text · --muted: secondary text · --electric: cyan accent #00D4FF · --moss-glow: green PASS color #00D49B · --signal: amber compliance flag #FFB446 · --warning: red fail #FF5C35
   Use these vars via var(--name). Use the JetBrains Mono font for technical fields, system sans for prose.
2. Structure:
   - One-line headline: "{{brand}} · {{claim text in plain English}} · {{audit verdict}}"
   - 150-200 word executive narrative explaining what was verified, what the evidence shows, what the vet rubric scored, and what the FTC compliance check found. Use plain language a general counsel can scan in 30 seconds.
   - "Ship before launch" section: 3 specific, actionable fixes the brand should make. Numbered list.
3. Tone: confident, professional, factual. No emoji. No marketing copy. Sound like an engineering audit, not a press release.
4. NEVER fabricate. ONLY use facts from the BUNDLE. If the bundle says vet_score=2/5, say "2 out of 5" — don't round up. If compliance.violation_flag=true, lead with that.
5. Do NOT name external integrations (Amazon Rufus, Chewy, etc.) — they are use cases, not current integrations.
6. End with the signed bundle URN + chain anchor as a small monospace block.

Return ONLY the HTML. No prose preamble, no explanation. Start with <div class="cert-composed"> and end with </div>."""


def _client() -> genai.Client:
    return genai.Client(vertexai=True, project="pawconscious-mesh-2026", location="us-central1")


async def compose_cert(bundle: EndorsementClaimBundle, bundle_hash: str | None, chain_anchor: str | None) -> str:
    """Generate a branded HTML cert from the signed bundle.

    Returns a self-contained HTML fragment ready to inject into the demo-cert pane.
    """
    bundle_dict = json.loads(bundle.model_dump_json())
    # Trim to only the fields the LLM needs (avoid wasting context on raw evidence dumps)
    bundle_for_prompt = {
        "product_url": bundle_dict.get("product_url"),
        "sku": bundle_dict.get("sku"),
        "bundle_urn": bundle_dict.get("bundle_urn"),
        "issued_at": bundle_dict.get("issued_at"),
        "claims": [
            {"text": c["text"], "kind": c.get("kind")} for c in bundle_dict.get("claims", [])
        ],
        "vet_scores": [
            {"score": v["score"], "rationale": v.get("rationale", "")[:200], "escalate": v.get("escalate_to_human_vet")}
            for v in bundle_dict.get("vet_scores", [])
        ],
        "compliance": [
            {
                "ftc_section": c.get("ftc_section"),
                "violation_flag": c.get("violation_flag"),
                "rationale": (c.get("rationale") or "")[:240],
            }
            for c in bundle_dict.get("compliance", [])
        ],
        "audit": [
            {"verdict": a.get("verdict"), "findings_count": len(a.get("findings", []))}
            for a in bundle_dict.get("audit", [])
        ],
        "evidence_summary": [
            {"papers_count": len(e.get("papers", []))} for e in bundle_dict.get("evidence", [])
        ],
        "bundle_hash": bundle_hash,
        "chain_anchor": chain_anchor,
    }

    prompt = CERT_PROMPT.format(bundle_json=json.dumps(bundle_for_prompt, indent=2))

    client = _client()
    # gemini-2.5-flash for speed (cert composition is HTML, doesn't need 2.5 Pro depth).
    # Upgrade to gemini-3.5-flash queued per WIN_PLAN Day 4 A/B eval.
    response = client.models.generate_content(
        model="gemini-2.5-flash-002",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.2,
            max_output_tokens=2000,
        ),
    )

    html = (response.text or "").strip()
    # Strip markdown code fences if present (defensive)
    if html.startswith("```"):
        html = "\n".join(html.split("\n")[1:-1]) if html.count("```") >= 2 else html.split("```", 2)[1]
    if html.startswith("html\n"):
        html = html[5:]
    return html.strip()
