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
from shared.llm_retry import agenerate


# v0.10.1a (codex amendment A-codex-2): prompt restructured with positive
# phrasing dictionary + few-shot exemplars + locked disclosure template +
# belt-and-suspenders negative constraints. Replaces the v0.8.x prompt that
# leaked "the veterinary panel" because no phrasing dictionary existed.
#
# Honesty contract per the plan: every cert produced by this prompt must
# (1) describe Agent 3 as a simulation, never a panel; (2) describe the
# auditor as PMID-format check (not real-existence); (3) include the
# locked DISCLOSURE_BLOCK below verbatim; (4) survive the regression test
# in tests/test_cert_honesty.py (no FORBIDDEN_PHRASES).

# Locked disclosure block — Gemini emits this VERBATIM inside the cert
# footer. Not generated; templated. Lives here so the wording is single-
# source-of-truth and never drifts.
DISCLOSURE_BLOCK_INLINE = (
    "Disclosure: AI-derived attestation · vet rubric is an LLM simulation "
    "· audit + Second Opinion are LLM agents over real evidence "
    "(PubMed, FTC §255, Google Search) · Ed25519 signed"
)

# Full scope block — revealed inside the cert footer's <details> expander.
DISCLOSURE_BLOCK_FULL = """<details style="margin-top:6px;">
<summary style="cursor:pointer;color:var(--electric);font-family:var(--mono);font-size:0.62rem;letter-spacing:0.16em;text-transform:uppercase;">Show full scope of attestation</summary>
<ul style="margin:8px 0 0 0;padding-left:18px;font-family:var(--mono);font-size:0.62rem;color:var(--dim);line-height:1.6;list-style:none;">
<li>· Vet rubric: Gemini 2.5 Pro simulating a 5-vet panel. Not licensed-DVM attestation. Replaced by the attest_expert A2A skill in v0.2.</li>
<li>· Evidence retrieval: BioMCP → PubMed (real papers) + Semantic Scholar citation grading. Real-existence verification of PMIDs is PMID-format only at v0.1; citation_enricher extends to existence + influence.</li>
<li>· Compliance: Vertex AI Search over public FTC 16 CFR §255 + AAFCO PF7 + NASC public seal corpus. No licensed handbooks ingested.</li>
<li>· Auditor (Falsifier v0): claim-direction + PMID-format checks only.</li>
<li>· Second Opinion: Gemini 2.5 Pro + Google Search grounding.</li>
<li>· Signed: Ed25519 with mesh's own key (did:web:mesh-api-...). Not a 3rd-party accredited co-signature; partner co-signing tier (NASC / NSF / vet-school) is v0.2 roadmap.</li>
</ul>
</details>"""

CERT_PROMPT = """You are PawConscious — an agentic compliance protocol for DTC consumer brands.

You have just signed an evidence bundle for the following product. Compose a tight executive verification cert in HTML.

BUNDLE (JSON):
{bundle_json}

# REQUIRED PHRASING (always use these; never substitute)

When you describe each part of the verification, use the EXACT terminology below. This labels the work honestly so the cert survives legal/regulatory scrutiny.

| What you're describing | REQUIRED phrasing | Why this matters |
|---|---|---|
| Agent 3's output (vet_scores in the bundle) | "AI vet-rubric simulation", "simulated 5-vet rubric", or "AI-simulated vet rubric" | The scores come from Gemini 2.5 Pro role-playing 5 vets. **There are no real DVMs in the loop today.** Calling it a "veterinary panel" is misleading. |
| Agent 7's output (second_opinion) | "adversarial Second Opinion", "Second Opinion stress tests" | This is honest as-is. |
| Agent 5's audit | "Falsifier auditor", "PMID-format check", "claim-direction check" | The auditor verifies PMID FORMAT, not real existence. Never say "verified citations exist" — they may not. |
| Citation evidence | "PubMed-retrieved papers", "BioMCP-retrieved evidence" | These ARE real papers (retrieved live). Honest. |
| The compliance mapping | "FTC §255 substantiation check (Vertex AI Search grounded)" | Honest — we DO ground against a real FTC corpus. |

# FORBIDDEN PHRASES (never write these, no exceptions)

- "veterinary panel" — the vet rubric is a simulation, not a panel
- "vet panel" (unless preceded by "simulated" or "AI-simulated")
- "verified citations exist" — the auditor only validates PMID format
- "licensed DVM" — we don't have any
- "3rd-party accredited" — we sign with our own Ed25519 key
- "FDA approved" — we don't certify FDA approval

# FEW-SHOT EXEMPLARS (honest cert narrative voice)

EXAMPLE 1 — a passing claim (vet rubric 4/5, no FTC flag, audit PASS):
> The AI vet-rubric simulation scored this claim 4 out of 5, citing two randomized controlled trials in dogs supporting the chondroitin–glucosamine mechanism. The FTC §255 substantiation check found the wording consistent with general-wellness positioning rather than disease treatment. The Falsifier auditor cleared all PMID-format checks. Bundle issued without escalation.

EXAMPLE 2 — a failing claim (vet rubric 1/5, FTC flag, audit FAIL):
> The AI vet-rubric simulation scored this claim 1 out of 5: while the mechanism is plausible, the supporting evidence is sparse and the marketing language ("clinically proven") implies a higher standard than the literature supports. The FTC §255 substantiation check flagged the claim under §255.1 General — specific efficacy language requires "competent and reliable scientific evidence" that is not present in the bundle. The Falsifier auditor surfaced a claim-direction mismatch on one cited PMID. **Verdict: NEEDS REVIEW pending revised claim language or stronger evidence.**

# STRUCTURE OF THE CERT

1. Output a SINGLE HTML fragment (no <html>, <head>, <body> — just the cert markup). It will be inserted into a dark-mode dashboard with these CSS variables already defined:
   --ink: white-ish text · --muted: secondary text · --electric: cyan accent #00D4FF · --moss-glow: green PASS color #00D49B · --signal: amber compliance flag #FFB446 · --warning: red fail #FF5C35
   Use these vars via var(--name). JetBrains Mono for technical fields, system sans for prose.

2. Cert structure:
   - One-line headline: "{{brand}} · {{claim text in plain English}} · {{audit verdict}}"
   - 150–200 word executive narrative explaining what was verified, what the evidence shows, what the AI vet-rubric simulation scored, and what the FTC §255 substantiation check found. Use plain language a general counsel can scan in 30 seconds. Apply the REQUIRED PHRASING table above.
   - "Ship before launch" section: 3 specific actionable fixes the brand should make. Numbered list.

3. Cert footer (use this LOCKED TEMPLATE — do not paraphrase, do not omit):
   <div class="cert-footer">
     [bundle_urn]<br>
     [bundle_hash]<br>
     <span class="cert-disclosure-inline">{disclosure_inline}</span>
     {disclosure_full_html}
   </div>

4. Tone: confident, professional, factual. No emoji. No marketing copy. Sound like an engineering audit, not a press release.

5. NEVER fabricate. ONLY use facts from the BUNDLE. If the bundle says vet_score=2/5, say "2 out of 5" — don't round up. If compliance.violation_flag=true, lead with that.

6. Do NOT name external integrations (Amazon Rufus, Chewy, etc.) — they are use cases, not current integrations.

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

    # v0.10.1a: substitute the locked disclosure block templates so Gemini emits
    # them verbatim (it does not "generate" disclosure text — it just inserts).
    prompt = CERT_PROMPT.format(
        bundle_json=json.dumps(bundle_for_prompt, indent=2),
        disclosure_inline=DISCLOSURE_BLOCK_INLINE,
        disclosure_full_html=DISCLOSURE_BLOCK_FULL,
    )

    client = _client()
    # gemini-2.5-pro — known-working on our Vertex project.
    # max_output_tokens=8000 (was 2000 — cert was truncated mid-CSS in v0.8.1).
    response = await agenerate(client, 
        model="gemini-2.5-pro",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.2,
            max_output_tokens=8000,
        ),
    )

    html = (response.text or "").strip()
    # Strip markdown code fences if present (defensive)
    if html.startswith("```"):
        html = "\n".join(html.split("\n")[1:-1]) if html.count("```") >= 2 else html.split("```", 2)[1]
    if html.startswith("html\n"):
        html = html[5:]
    # Sanitize control characters that break JSON parsing on the wire
    # (Pydantic auto-escapes \n but some clients fail on \r and ASCII < 0x20)
    html = html.replace("\r", "").translate({i: None for i in range(0x20) if i not in (0x09, 0x0A)})
    return html.strip()
