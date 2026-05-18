# PawConscious Mesh — A2A Agent Card

**Path:** `/.well-known/agent-card.json`
**Protocol:** A2A v0.3 (Linux Foundation, April 2026 GA)
**Status:** Draft (hackathon-deliverable, single mesh card)

## Why this exists (honest)

A2A v0.3 lets any A2A-compatible LLM agent discover and call our trust mesh. **The mesh is A2A v0.3 compatible. We have no current third-party integrations** — no Rufus, no Perplexity Shopping, no ChatGPT commerce, no Gemini Shopping. The protocol is open; consumers have not yet integrated.

For the hackathon demo, we ship a small **ShopperAgent** (source in our public repo) that exercises the card end-to-end. The demo proves the protocol works, not that the consumer ecosystem is using it yet.

The forward vision is the Stripe/Twilio asymmetry — brands pay for cert issuance, agent consumers call `verify_claim` for free. But that's roadmap, not v0.1 reality. Today, the A2A endpoint is rate-limited and gated by a demo API key for safety; public open access ships post-hackathon once abuse controls are validated.

## Agent card schema

```json
{
  "name": "PawConscious Mesh",
  "description": "A2A trust mesh for expert-claim commerce. Verify endorsement claims on commerce SKUs against signed PCEC bundles.",
  "url": "https://mesh-api-40952019806.us-central1.run.app/a2a/v1",
  "version": "0.1.0",
  "provider": {
    "organization": "PawConscious",
    "url": "https://pawconscious.com"
  },
  "documentationUrl": "https://github.com/odominguez7/PawConscious-Mesh-GFS",
  "capabilities": {
    "streaming": true,
    "pushNotifications": false,
    "stateTransitionHistory": false
  },
  "authentication": {
    "schemes": ["api-key"],
    "note": "Hackathon period: demo API key required (request via repo issue). Public open access post-hackathon once abuse controls are validated."
  },
  "defaultInputModes": ["text"],
  "defaultOutputModes": ["text", "application/ld+json"],
  "skills": [
    {
      "id": "verify_claim",
      "name": "Verify endorsement claim",
      "description": "Given a SKU (GTIN/ASIN/Shopify product handle) and a claim text, return a trust score 0-1 plus the underlying PCEC bundle URN. Trust score is derived from: peer-reviewed evidence presence, vet-panel rubric, FTC §255 compliance mapping, and adversarial audit verdict.",
      "tags": ["trust", "endorsement", "substantiation", "commerce", "PCEC"],
      "examples": [
        "Verify the claim 'supports joint mobility' for SKU urn:gtin:00850001234567",
        "Is 'vet-formulated' substantiated on this Honest Paws Calming Bites product?"
      ],
      "inputModes": ["text"],
      "outputModes": ["text", "application/ld+json"]
    },
    {
      "id": "fetch_substantiation_bundle",
      "name": "Fetch substantiation bundle",
      "description": "Given a PCEC claim URN, return the full EvidenceBundle + ExpertAttestation + AuditVerdict JSON-LD. Use this when the caller needs to inspect the underlying evidence (not just the trust score) — for example, a regulator inspector or a competitive-intelligence agent.",
      "tags": ["PCEC", "evidence", "audit"],
      "examples": [
        "Fetch the substantiation for claim urn:pcec:claim:01HZ123XYZ"
      ],
      "inputModes": ["text"],
      "outputModes": ["application/ld+json"]
    },
    {
      "id": "attest_expert",
      "name": "Attest expert credential",
      "description": "Given an expert DID (vet, dermatologist, athlete, physician), return verified credential metadata: license type, jurisdiction, current status, and the set of claims the expert has signed in the last 12 months. Use this to validate whether an expert endorsement on a PDP is real and current.",
      "tags": ["DID", "credential", "expert"],
      "examples": [
        "Attest expert did:web:bostonvet.example:experts:dr-smith"
      ],
      "inputModes": ["text"],
      "outputModes": ["application/ld+json"]
    }
  ]
}
```

## How agents call us (hackathon)

Any A2A v0.3-compatible agent can:
1. Discover via `GET https://mesh-api-40952019806.us-central1.run.app/.well-known/agent-card.json`
2. Request a demo API key via GitHub issue on the repo
3. Invoke `POST https://mesh-api-40952019806.us-central1.run.app/a2a/v1/tasks/send` with a `verify_claim` task and the demo key in the auth header
4. Stream responses via SSE per A2A v0.3

The hackathon ships with one verified consumer: our own `ShopperAgent` Cloud Run service (source in the public repo). Judges can verify the external call is real by reading the ShopperAgent source + watching the live demo moment.

## Why this is the rubric-maxxing single feature

The GFS hackathon explicitly mandates **A2A protocol** and **Gemini Enterprise integration**. A2A v0.3 agent cards are the canonical Gemini Enterprise integration path (per Google's [Startup Technical Guide: AI Agents](https://google.github.io/adk-docs/) §An overview of Google Cloud's agent ecosystem).

Most hackathon entries will use A2A internally — peer agents talking to each other inside one team's stack. PawConscious Mesh additionally exposes A2A externally — any A2A-compatible agent can call our mesh (with a demo key during the hackathon period). The demo proves the protocol works end-to-end with a real external consumer (our ShopperAgent). That's "real agentic infrastructure with a working external client," not "real agentic infrastructure used by Perplexity" — we don't claim what we haven't built.

## Status

To be implemented in Phase 2 (D3-D5). See PLAN.md.
