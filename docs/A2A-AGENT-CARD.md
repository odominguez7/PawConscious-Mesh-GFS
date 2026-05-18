# PawConscious Mesh — Public A2A Agent Card

**Path:** `/.well-known/agent-card.json`
**Protocol:** A2A v0.3 (Linux Foundation, April 2026 GA)
**Status:** Draft (hackathon-deliverable)

## Why this exists

A2A v0.3 lets any LLM agent (Rufus, Perplexity Shopping, ChatGPT commerce, Gemini Shopping, custom enterprise agents) discover and call our trust mesh **without an account, an API key dance, or a SaaS subscription**. The brand pays us for issuing claims. The agent ecosystem calls us for free to verify them.

This asymmetry is the Stripe/Twilio playbook. Merchants pay; end-user-side calls are free.

## Agent card schema

```json
{
  "name": "PawConscious Mesh",
  "description": "A2A trust mesh for expert-claim commerce. Verify endorsement claims on commerce SKUs against signed PCEC bundles.",
  "url": "https://mesh.pawconscious.com/a2a/v1",
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
    "schemes": ["none"]
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

## How agents call us

Any A2A-compliant agent can:
1. Discover via `GET https://mesh.pawconscious.com/.well-known/agent-card.json`
2. Invoke `POST https://mesh.pawconscious.com/a2a/v1/tasks/send` with a `verify_claim` task
3. Stream responses via SSE per A2A v0.3

No API key. No registration. Free at the call-site (rate-limited per IP at high traffic to prevent abuse).

## Why this is the rubric-maxxing single feature

The GFS hackathon explicitly mandates **A2A protocol** and **Gemini Enterprise integration**. Public A2A agent cards are the canonical Gemini Enterprise integration path (per Google's [Startup Technical Guide: AI Agents](https://google.github.io/adk-docs/) §An overview of Google Cloud's agent ecosystem).

Most hackathon entries will use A2A internally — peer agents talking to each other inside one team's stack. PawConscious Mesh additionally exposes A2A externally — any third-party agent in the world can call our mesh. That is the strongest possible signal of "this is real agentic infrastructure, not a demo."

## Status

To be implemented in Phase 2 (D3-D5). See PLAN.md.
