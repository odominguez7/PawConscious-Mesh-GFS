"""Single source of truth for the PawConscious bundle verdict.

The verdict is THE product. A green badge must mean "health claims are
substantiated", not merely "no violation found". Before 2026-05-28 the verdict
was derived from audit + FTC flags only, which gave a clean PASS to products
whose only claims are marketing puffery (vet rubric 1/5) and ignored the
adversarial Second Opinion entirely. A dog treat whose claims were "100% Happy
Guarantee" and "delicious treats" earned the same green PASS as a PubMed-backed
joint supplement, while the Second Opinion said NEEDS REVIEW. That is a trust
product lying.

This module folds in the vet rubric and the Second Opinion, and adds a neutral
"no verifiable health claims" state for puffery-only products.

IMPORTANT: the JS mirror `pcVerdict()` in services/mesh_api/static/console-v2.html
MUST stay in sync with this. Both implement the same precedence.
"""
from __future__ import annotations

from typing import Any


# Precedence (highest first):
#   FAIL  >  NEEDS REVIEW(SO)  >  no testable claims (puffery)  >  CONDITIONAL
#         >  FTC flag  >  weak evidence  >  VERIFIED
# A vet rubric score of 1/5 marks a claim as non-testable (puffery / subjective /
# marketing), per the rubric's own definition.
def compute_verdict(output: dict | None, second_opinion: dict | None = None) -> dict[str, Any]:
    """Return {key, label, color, explain} for a signed bundle's `output`.

    key   : VERIFIED | CONDITIONAL | NO_CLAIMS | FAIL | ISSUED
    color : pass (green) | cond (amber) | none (gray) | fail (red)
    """
    out = output or {}
    audit_verdicts = [a.get("verdict") for a in out.get("audit", []) if isinstance(a, dict)]
    ftc_flags = [c for c in out.get("compliance", []) if isinstance(c, dict) and c.get("violation_flag")]
    vet = [v.get("score") for v in out.get("vet_scores", [])
           if isinstance(v, dict) and isinstance(v.get("score"), (int, float))]
    testable = [s for s in vet if s > 1]
    so = (str((second_opinion or {}).get("overall_verdict") or "")).strip().upper()

    def V(key, label, color, explain):
        return {"key": key, "label": label, "color": color, "explain": explain}

    # 1. Hard failures.
    if "FAIL" in audit_verdicts:
        return V("FAIL", "FAIL", "fail",
                 "The audit failed on at least one claim: the evidence does not support it.")
    if so == "FAIL":
        return V("FAIL", "FAIL", "fail",
                 "The adversarial Second Opinion found evidence that contradicts the claims.")

    # 2. Nothing substantiated: every claim scored 1/5, whether because it is
    #    marketing puffery (no testable claim, e.g. "delicious treats") or a real
    #    health claim with no supporting evidence (e.g. weak calming claims). Either
    #    way nothing was substantiated, so this is neutral gray, never a green pass.
    #    (Precise puffery-vs-unsupported split needs a "puffery" claim kind in the
    #    extractor + a seed re-capture; tracked as follow-up.)
    if vet and not testable:
        return V("NO_CLAIMS", "Unverified", "none",
                 "No health claim on this product could be substantiated. Its claims are "
                 "either marketing language or lack supporting evidence.")

    # 3. The Second Opinion is a flag the badge must honor.
    if so in ("NEEDS REVIEW", "NEEDS_REVIEW"):
        return V("CONDITIONAL", "Conditional", "cond",
                 "The adversarial Second Opinion advises review before relying on these claims.")

    # 4. Auditor caveats and compliance flags.
    if "CONDITIONAL" in audit_verdicts:
        return V("CONDITIONAL", "Conditional", "cond",
                 "The audit cleared the claims with caveats.")
    if ftc_flags:
        return V("CONDITIONAL", "Conditional", "cond",
                 "An FTC §255 substantiation flag should be addressed before launch.")

    # 5. Weak-but-not-failed evidence.
    if testable and (sum(testable) / len(testable)) < 2.5:
        return V("CONDITIONAL", "Conditional", "cond",
                 "The claims are testable but the supporting evidence is weak.")

    # 6. Earned pass: a substantiated, testable health claim with no blocking flags.
    if testable:
        return V("VERIFIED", "Verified", "pass",
                 "Health claims are substantiated by graded PubMed evidence.")

    # 7. No vet scores at all (cannot assess substance) -> conservative.
    if audit_verdicts:
        return V("CONDITIONAL", "Conditional", "cond",
                 "Issued; claim substance could not be fully assessed.")
    return V("ISSUED", "Issued", "cond", "Bundle issued.")
