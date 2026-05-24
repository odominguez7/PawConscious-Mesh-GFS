# Runbook · Agent Engine routing + Cloud Run warm-up

**Owner:** Omar
**When to run:** 2026-06-04 evening (before judges land at 2026-06-05 noon PT)
**Reversible:** Yes — every step has a single-command rollback

## What this does

- Flips `ACP_USE_AGENT_ENGINE=true` on the live `mesh-api` Cloud Run
  service. Traffic now routes through the deployed Vertex AI Reasoning
  Engine first, with auto-fallback to inline asyncio if the engine p95
  exceeds 2x inline or three consecutive engine calls fail.
- Sets Cloud Run `--min-instances=1` so the first judge click does not
  pay a cold-start latency penalty (~20-40 seconds at base SKU).
- Cost during the ~24 hour judging window: ~$1-2 actual spend.

## Prerequisites

Active gcloud config must be `pawconscious-mesh`:

```bash
gcloud config configurations activate pawconscious-mesh
gcloud config get project
# expect: pawconscious-mesh-2026
```

## Step 1 — Flip the Agent Engine feature flag + pin min-instances

```bash
gcloud run services update mesh-api \
  --region=us-central1 \
  --update-env-vars=ACP_USE_AGENT_ENGINE=true \
  --min-instances=1 \
  --quiet
```

Cloud Run rolls a new revision with the env var + min-instances change.
~30 seconds. Traffic auto-switches to the new revision.

## Step 2 — Verify the flip landed

```bash
curl -s https://mesh-api-40952019806.us-central1.run.app/health/agent-engine | jq
```

Expected output:

```json
{
  "status": "ok",
  "agent_engine_resource": "projects/40952019806/locations/us-central1/reasoningEngines/1255381144908595200",
  "feature_flag_use_agent_engine": true,
  "traffic_gate_open": true,
  "traffic_gate_reason": "initial: feature flag ON",
  ...
}
```

If `feature_flag_use_agent_engine` is still `false`, the env var didn't
land. Re-run Step 1 with `--update-env-vars` or use the GCP console.

## Step 3 — Smoke-test the live mesh via Agent Engine

```bash
TASK=$(curl -s -X POST \
  https://mesh-api-40952019806.us-central1.run.app/a2a/v1/tasks/send \
  -H "X-API-Key: demo-key-2026-06" \
  -H "Content-Type: application/json" \
  -d '{"message":{"role":"user","parts":[{"type":"text","text":"https://www.nativepet.com/products/hip-joint"}]},"skill":"verify_claim"}' \
  | jq -r .task_id)
echo "task: $TASK"
```

Then poll:

```bash
curl -s "https://mesh-api-40952019806.us-central1.run.app/a2a/v1/tasks/get/$TASK" \
  -H "X-API-Key: demo-key-2026-06" | jq '.status, .bundle_hash'
```

Expected: status transitions `submitted` → `working` → `completed` in
~2-4 minutes with a real `bundle_hash`. Cloud Logging will show the
`span_name=route_decision path=agent_engine` entry plus per-agent spans
for each step (claim-extractor, evidence-grader, vet-rubric, compliance,
auditor).

## Step 4 — Observe in Cloud Logging

Open Log Explorer with this query:

```
resource.type="cloud_run_revision"
resource.labels.service_name="mesh-api"
jsonPayload.span_name=("agent_call" OR "route_decision")
```

You should see one `route_decision` line per task plus one `agent_call`
line per agent invocation with `agent`, `duration_ms`, and `outcome`
fields. That's the Section 6 observability story for the rubric.

## Rollback — if Agent Engine misbehaves

Single command flips the flag back to inline (no min-instances change):

```bash
gcloud run services update mesh-api \
  --region=us-central1 \
  --update-env-vars=ACP_USE_AGENT_ENGINE=false \
  --quiet
```

The auto-fallback gate also rolls itself closed after three consecutive
Agent Engine failures OR if Agent Engine p95 exceeds 2x inline p95 over
a 20-call rolling window. The env var override is the manual kill.

## After judging — return min-instances to 0 (cost control)

After the submission window closes (2026-06-05 evening), drop the
always-on instance back to scale-to-zero:

```bash
gcloud run services update mesh-api \
  --region=us-central1 \
  --min-instances=0 \
  --quiet
```

## Why we do not flip the flag earlier

Flipping the flag earlier than judging-eve burns Reasoning Engine call
credit on dev traffic + makes any infra issue land on the live demo
URL before we have eyes on it. The inline asyncio path is the proven
default. Agent Engine is the documented Track 3 bonus signal; we flip
it on right before judges land so the observability spans + the
`/health/agent-engine` badge both reflect a live route during scoring.
