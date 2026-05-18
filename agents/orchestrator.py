"""Orchestrator (ParallelAgent fan-out + SequentialAgent merge per PLAN.md §2).

End-to-end mesh pipeline:
1. claim-extractor pulls all claims from a product URL
2. For each claim: ParallelAgent fan-out across (evidence-grader, vet-panel, compliance)
3. auditor reviews the merged evidence per claim
4. Returns full EndorsementClaimBundle (PCEC v0.1 shape)

For Phase 3 we use asyncio.gather as the parallel primitive (deterministic, works
without Agent Engine deployment). ADK ParallelAgent + SequentialAgent wrappers are
declared for the public API surface in services/mesh_api/ (Phase 4).

Per codex G9 #6: retry/timeout via shared.llm_retry; deterministic sampling
(temperature 0) already enforced in each agent module.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents.auditor import audit_bundle
from agents.claim_extractor import extract_claims
from agents.compliance import map_claim as compliance_map
from agents.evidence_grader import grade_claim
from agents.vet_panel import score_claim as vet_score
from shared.pcec_schema import (  # noqa: E402
    AuditVerdict, Claim, ComplianceMapping, EndorsementClaimBundle,
    EvidenceBundle, VetRubricScore,
)


async def process_claim(claim: Claim) -> tuple[EvidenceBundle, VetRubricScore, ComplianceMapping, AuditVerdict]:
    """ParallelAgent equivalent: fan out evidence-grade + vet-score + compliance-map for one claim,
    then run auditor on the evidence bundle."""
    # Parallel fan-out
    evidence, vet, comp = await asyncio.gather(
        grade_claim(claim),
        vet_score(claim),
        compliance_map(claim),
    )
    # Auditor runs after evidence is available
    audit = await audit_bundle(evidence)
    return evidence, vet, comp, audit


async def run_mesh(product_url: str, max_claims: int | None = None) -> EndorsementClaimBundle:
    """Run the full mesh pipeline against a product URL.

    Returns the assembled EndorsementClaimBundle ready for signing.
    """
    print(f"[orchestrator] Step 1: claim extraction from {product_url}")
    claims = await extract_claims(product_url)
    if max_claims is not None:
        claims = claims[:max_claims]
    print(f"[orchestrator] Extracted {len(claims)} claims")

    print(f"[orchestrator] Step 2: parallel fan-out across {len(claims)} claims...")
    results = await asyncio.gather(*[process_claim(c) for c in claims])

    print("[orchestrator] Step 3: assemble bundle")
    bundle = EndorsementClaimBundle(
        sku=product_url,  # v0.1 uses URL as SKU until we extract GTIN/ASIN
        product_url=product_url,
        claims=claims,
        evidence=[r[0] for r in results],
        vet_scores=[r[1] for r in results],
        compliance=[r[2] for r in results],
        audit=[r[3] for r in results],
    )
    return bundle


def summarize(bundle: EndorsementClaimBundle) -> str:
    """Plain-text summary for stdout / Mesh Console UI."""
    lines = [f"\n=== PawConscious Mesh — Bundle for {bundle.sku} ===\n"]
    lines.append(f"Issued at: {bundle.issued_at.isoformat()}Z")
    lines.append(f"Issuer: {bundle.issuer}")
    lines.append(f"Total claims: {len(bundle.claims)}")

    pass_count = sum(1 for a in bundle.audit if a.verdict == "PASS")
    fail_count = sum(1 for a in bundle.audit if a.verdict == "FAIL")
    cond_count = sum(1 for a in bundle.audit if a.verdict == "CONDITIONAL")
    violation_count = sum(1 for c in bundle.compliance if c.violation_flag)
    escalate_count = sum(1 for v in bundle.vet_scores if v.escalate_to_human_vet)

    lines.append(f"\nAudit verdicts: {pass_count} PASS / {cond_count} CONDITIONAL / {fail_count} FAIL")
    lines.append(f"Compliance flags: {violation_count} violations")
    lines.append(f"Vet escalations: {escalate_count} claims need human vet review")

    lines.append("\n--- Per-claim detail ---")
    for i, (c, ev, vet, comp, aud) in enumerate(
        zip(bundle.claims, bundle.evidence, bundle.vet_scores, bundle.compliance, bundle.audit), 1
    ):
        lines.append(f"\n{i}. [{c.kind.value}] {c.text!r}")
        lines.append(f"   Evidence: {len(ev.papers)} papers (real PMIDs)")
        lines.append(f"   Vet: {vet.score}/5{' ESCALATE' if vet.escalate_to_human_vet else ''}")
        lines.append(f"   Compliance: FTC {comp.ftc_section or '-'} {'⚠ VIOLATION' if comp.violation_flag else ''}")
        lines.append(f"   Audit: {aud.verdict}{f' ({len(aud.findings)} findings)' if aud.findings else ''}")

    return "\n".join(lines)


async def main() -> None:
    """Phase 3 verification: full mesh against real Native Pet PDP, top 5 claims for speed."""
    url = "https://www.nativepet.com/products/hip-joint"
    bundle = await run_mesh(url, max_claims=5)
    print(summarize(bundle))


if __name__ == "__main__":
    asyncio.run(main())
