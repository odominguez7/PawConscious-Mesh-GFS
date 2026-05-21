#!/usr/bin/env python3
"""ADK eval baseline runner — exercises the verify_claim multi-agent flow.

Reads tests/adk_eval/cases.json, hits the live mesh-api, scores each case
on 4 structural assertions:
  - returned a task_id
  - completed within timeout
  - bundle_signature present and not 'unsigned…'
  - output.audit has >= min_audits entries

Outputs JSONL + a PASS/FAIL summary. Designed to be re-runnable as a
GitHub Actions step to keep a published baseline score on the README.

Usage:
  python tests/adk_eval/run.py                       # smoke (first 3 cases)
  python tests/adk_eval/run.py --full                # all 20 cases (slow, ~60-90 min — single Cloud Run instance)
  python tests/adk_eval/run.py --case EC-001         # single case

Env:
  MESH_URL (default: https://mesh-api-40952019806.us-central1.run.app)
  MESH_API_KEY (default: demo-key-2026-06)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

try:
    import httpx
except ImportError:
    print("pip install httpx", file=sys.stderr)
    sys.exit(1)

MESH_URL = os.environ.get("MESH_URL", "https://mesh-api-40952019806.us-central1.run.app").rstrip("/")
MESH_API_KEY = os.environ.get("MESH_API_KEY", "demo-key-2026-06")
CASES_FILE = Path(__file__).parent / "cases.json"
RESULTS_DIR = Path(__file__).parent / "results"


def run_case(client: httpx.Client, case: dict[str, Any], timeout_s: int = 900) -> dict[str, Any]:
    case_id = case["id"]
    url = case["url"]
    t0 = time.monotonic()
    result: dict[str, Any] = {
        "case_id": case_id,
        "url": url,
        "assertions": {},
        "pass": False,
        "skipped": False,
        "error": None,
        "elapsed_s": 0.0,
    }
    # Pre-flight: HEAD probe the source URL. DTC pet brands churn catalog pages
    # weekly; a true 4xx/5xx here is a stale-fixture problem.
    #
    # Codex Day-21 amend pass: anti-bot status codes (403/406/429) and 5xx
    # indicate the page EXISTS but the server is blocking naive HEAD probes.
    # The mesh's Firecrawl fallback path is built exactly for these — so do
    # NOT skip them. Skip only on hard dead-URL signals (404, 410, network
    # errors, redirect loops).
    ANTI_BOT_CODES = {401, 403, 405, 406, 429, 500, 502, 503, 504}
    HARD_DEAD_CODES = {404, 410}
    try:
        head = client.head(url, follow_redirects=True, timeout=15.0, headers={"User-Agent": "Mozilla/5.0 (pcec-eval)"})
        code = head.status_code
        if code == 200 or code in ANTI_BOT_CODES:
            pass  # eligible — let the mesh's Firecrawl fallback do the work
        elif code in HARD_DEAD_CODES:
            result["skipped"] = True
            result["error"] = f"url_dead: HEAD returned {code}"
            result["elapsed_s"] = round(time.monotonic() - t0, 1)
            return result
        else:
            # Unknown response — be conservative; treat as eligible and let
            # the mesh report the real failure mode through its task_store.
            result["preflight_warning"] = f"HEAD returned unexpected {code} — proceeding"
    except Exception as e:
        result["skipped"] = True
        result["error"] = f"url_dead: HEAD raised {type(e).__name__}"
        result["elapsed_s"] = round(time.monotonic() - t0, 1)
        return result
    try:
        submit = client.post(
            f"{MESH_URL}/a2a/v1/tasks/send",
            json={"skill": "verify_claim", "input": {"product_url": url, "max_claims": 1}},
            headers={"X-API-Key": MESH_API_KEY, "Content-Type": "application/json"},
            timeout=60.0,
        )
        submit.raise_for_status()
        task = submit.json()
        task_id = task.get("task_id")
        result["assertions"]["task_id_returned"] = bool(task_id)
        if not task_id:
            result["error"] = "no task_id"
            return result

        # poll — mesh runs single-instance, so the GET endpoint can be blocked
        # behind in-flight worker calls for tens of seconds. Use a generous per-GET
        # read timeout AND retry on ReadTimeout (don't fail the case just because
        # one poll request stalled). overall `timeout_s` deadline is the real bound.
        deadline = time.monotonic() + timeout_s
        last_status = "submitted"
        data: dict[str, Any] = {}
        while time.monotonic() < deadline:
            time.sleep(5.0)
            try:
                get = client.get(f"{MESH_URL}/a2a/v1/tasks/get/{task_id}", timeout=300.0)
                get.raise_for_status()
                data = get.json()
                last_status = data.get("status", "")
                if last_status in ("completed", "failed"):
                    break
            except httpx.ReadTimeout:
                # GET was blocked behind the worker; keep polling until deadline.
                continue
            except httpx.HTTPStatusError as e:
                # Transient 5xx — retry. 4xx is real and should fail the case.
                if e.response.status_code >= 500:
                    continue
                raise

        result["assertions"]["completed_within_timeout"] = last_status == "completed"
        if last_status != "completed":
            result["error"] = f"final status {last_status}"
            return result

        signature = data.get("bundle_signature") or ""
        signed = bool(signature) and not signature.startswith("unsigned")
        result["assertions"]["signature_present"] = signed

        audits = (data.get("output") or {}).get("audit", [])
        result["assertions"]["min_audits_met"] = len(audits) >= case.get("min_audits", 1)

        result["pass"] = all(result["assertions"].values())
        result["audit_count"] = len(audits)
        result["bundle_hash"] = data.get("bundle_hash")
        result["chain_anchor"] = data.get("chain_anchor")
    except Exception as e:
        result["error"] = f"{type(e).__name__}: {e}"
    finally:
        result["elapsed_s"] = round(time.monotonic() - t0, 1)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--full", action="store_true", help="run all cases (slow)")
    parser.add_argument("--case", help="run single case by id")
    parser.add_argument("--no-network", action="store_true", help="dry-run without hitting mesh")
    args = parser.parse_args()

    spec = json.loads(CASES_FILE.read_text())
    cases = spec["cases"]
    if args.case:
        cases = [c for c in cases if c["id"] == args.case]
    elif not args.full:
        cases = cases[:3]

    if args.no_network:
        print(f"DRY RUN — would run {len(cases)} cases against {MESH_URL}", file=sys.stderr)
        return 0

    RESULTS_DIR.mkdir(exist_ok=True)
    ts = time.strftime("%Y%m%dT%H%M%S")
    out_path = RESULTS_DIR / f"eval-{ts}.jsonl"
    summary_path = RESULTS_DIR / "latest.json"

    print(f"eval baseline · mesh={MESH_URL} · {len(cases)} cases", file=sys.stderr)
    results = []
    with httpx.Client() as client, out_path.open("w") as f:
        for i, case in enumerate(cases, 1):
            print(f"[{i}/{len(cases)}] {case['id']} {case['url'][:60]}…", file=sys.stderr)
            r = run_case(client, case)
            if r.get("skipped"):
                tag = "SKIP"
            elif r["pass"]:
                tag = "PASS"
            else:
                tag = "FAIL"
            print(f"  {tag} {r['elapsed_s']}s {r.get('error','')}", file=sys.stderr)
            results.append(r)
            f.write(json.dumps(r) + "\n")

    skipped = sum(1 for r in results if r.get("skipped"))
    passed = sum(1 for r in results if r["pass"])
    total = len(results)
    eligible = total - skipped
    summary = {
        "mesh_url": MESH_URL,
        "timestamp": ts,
        "total": total,
        "skipped_url_dead": skipped,
        "eligible": eligible,
        "passed": passed,
        "score": f"{passed}/{eligible}",
        "pct": round(passed / eligible * 100, 1) if eligible else 0.0,
        "out_file": str(out_path.name),
        "note": "Skipped cases had upstream PDP URLs that returned non-200 at eval time (DTC catalogs churn). Pass rate excludes skipped cases from the denominator.",
    }
    summary_path.write_text(json.dumps(summary, indent=2))
    print(f"\n→ {passed}/{eligible} passed ({summary['pct']}%) · {skipped} skipped (url_dead) · {total} total — written to {out_path}", file=sys.stderr)
    return 0 if eligible > 0 and passed == eligible else 1


if __name__ == "__main__":
    sys.exit(main())
