"""One-shot cacher: runs the Document AI ingester on the two committed
Green Gruff COAs and writes JSON results to corpus/coa/cached/. The demo
cinematic loads these JSON files (or embeds them as JS constants) so the
"lab certificate" bento card in scene-2 / scene-2b renders consistently
without a live API call on every page load.

Re-run this script if the source COA PDFs change, or if we add new ones.

Usage:
  PYTHONPATH=. .venv/bin/python tools/cache_coa_extractions.py
"""

from __future__ import annotations

import json
from pathlib import Path

from agents.coa_ingester import ingest_coa


COAS_TO_CACHE = [
    {
        "pdf": "corpus/coa/green-gruff-ease-joint-hip.pdf",
        "label": "Green Gruff EASE · Joint & Hip · public COA",
        "out": "corpus/coa/cached/green-gruff-ease.json",
    },
    {
        "pdf": "corpus/coa/green-gruff-relax-calming.pdf",
        "label": "Green Gruff RELAX · Calming · public COA",
        "out": "corpus/coa/cached/green-gruff-relax.json",
    },
]


def main() -> None:
    out_dir = Path("corpus/coa/cached")
    out_dir.mkdir(parents=True, exist_ok=True)

    for entry in COAS_TO_CACHE:
        pdf_path = Path(entry["pdf"])
        out_path = Path(entry["out"])
        print(f"\n=== {entry['label']} ===")
        if not pdf_path.exists():
            print(f"  SKIP, missing: {pdf_path}")
            continue
        result = ingest_coa(pdf_path.read_bytes(), label=entry["label"])
        payload = result.to_bundle_dict()
        # Truncate raw_text to keep the cache slim; full text re-runnable.
        payload["raw_text_preview"] = (
            (result.raw_text[:1200] + "…") if result.raw_text else ""
        )
        out_path.write_text(json.dumps(payload, indent=2, default=str))
        print(f"  Pages: {result.page_count}")
        print(f"  Findings: {len(result.findings)}")
        print(f"  Wrote: {out_path}")


if __name__ == "__main__":
    main()
