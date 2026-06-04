"""Citation Enricher.

Enriches `Evidence` with real `citation_count` and `influential_citation_count`
from AI2's Semantic Scholar Graph API — the public surface of the Asta product
that the architecture doc names "AI2 Asta MCP".

Terminology note: there is no published "Asta MCP" server today; the citation
grading is a one-shot HTTP enrichment, not a tool-using LLM loop, so MCP is the
wrong protocol for this layer. We keep the interface narrow (one async
function, takes Evidence list, returns Evidence list) so an MCP wrapper is a
drop-in later if AI2 ships one.

Endpoint: POST https://api.semanticscholar.org/graph/v1/paper/batch
  ?fields=citationCount,influentialCitationCount
  body: {"ids": ["PMID:32316397", ...]}
Up to 500 IDs per call. Response array aligned by request order; `null` for
unknown PMIDs.

Failure mode: any non-2xx, timeout, or network error leaves the input
Evidence list untouched (citation_count stays at its prior value, usually 0).
We never crash the verification pipeline on a citation lookup miss.

API key: optional. SEMANTIC_SCHOLAR_API_KEY env var unlocks higher rate
limits; without it we use the public anonymous tier (1 req/sec across the
shared pool, frequent 429s on single-paper endpoints — batch is safer).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared.pcec_schema import Evidence  # noqa: E402

S2_BATCH_URL = "https://api.semanticscholar.org/graph/v1/paper/batch"
S2_FIELDS = "citationCount,influentialCitationCount"
S2_MAX_BATCH = 500
S2_TIMEOUT_S = 10.0


async def enrich_with_citations(
    papers: list[Evidence],
    *,
    debug: bool = False,
) -> list[Evidence]:
    """Return a new list of Evidence with citation counts populated.

    Drops nothing. On error, returns the input list unchanged (counts at 0).
    """
    if not papers:
        return papers

    # Dedupe PMIDs while preserving first-seen order — multiple Evidence may
    # share a PMID across claims; one S2 lookup suffices.
    seen: dict[str, None] = {}
    for p in papers:
        if p.pmid and p.pmid not in seen:
            seen[p.pmid] = None
    pmids = list(seen.keys())
    if not pmids:
        return papers

    headers = {"Content-Type": "application/json"}
    api_key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY")
    if api_key:
        headers["x-api-key"] = api_key

    counts: dict[str, tuple[int, int]] = {}
    try:
        async with httpx.AsyncClient(timeout=S2_TIMEOUT_S) as client:
            for offset in range(0, len(pmids), S2_MAX_BATCH):
                chunk = pmids[offset : offset + S2_MAX_BATCH]
                resp = await client.post(
                    S2_BATCH_URL,
                    params={"fields": S2_FIELDS},
                    json={"ids": [f"PMID:{pmid}" for pmid in chunk]},
                    headers=headers,
                )
                if resp.status_code != 200:
                    if debug:
                        print(
                            f"[s2] batch {offset}: HTTP {resp.status_code} "
                            f"— leaving counts at 0"
                        )
                    return papers
                rows = resp.json()
                for pmid, row in zip(chunk, rows):
                    if not row:
                        continue
                    cc = int(row.get("citationCount") or 0)
                    ic = int(row.get("influentialCitationCount") or 0)
                    counts[pmid] = (cc, ic)
    except (httpx.HTTPError, ValueError) as exc:
        if debug:
            print(f"[s2] enrichment failed: {exc!r} — leaving counts at 0")
        return papers

    enriched: list[Evidence] = []
    for p in papers:
        hit = counts.get(p.pmid)
        if hit is None:
            enriched.append(p)
            continue
        cc, ic = hit
        enriched.append(p.model_copy(update={
            "citation_count": cc,
            "influential_citation_count": ic,
        }))
    if debug:
        hits = sum(1 for p in enriched if p.citation_count > 0)
        print(f"[s2] enriched {hits}/{len(enriched)} papers with real citation counts")
    return enriched
