# PCEC v0.1 — Provenance for Commerce Endorsement Claims

**Status:** Draft v0.1 · **Date:** 2026-05-18 · **License:** CC-BY-4.0 · **Maintainer:** PawConscious

## Why this exists

Every expert claim made on a commerce surface — "vet-formulated," "clinically proven," "dermatologist-tested," "athlete-endorsed," "physician-developed" — currently has no machine-verifiable provenance. The badge is a `<span>` with a checkmark. The audit trail is a folder in someone's Dropbox. When the FTC inquiry arrives, or the class action drops, the brand cannot produce a signed evidence chain in under a week.

C2PA solved this for images. PCEC solves it for endorsement claims.

## Design principles

1. **The badge is the doorbell. The signed manifest is the house.** Consumer-visible elements are minimal — a 24×24 SVG. Everything else is machine-readable JSON-LD travelling with the SKU.
2. **Signatures, not assertions.** Every claim is signed by the issuing expert's DID. Every assertion ("4/5 vet panel score") is signed by the rubric runner's DID. Every audit verdict is signed by the auditor's DID.
3. **Anchored to a transparency log.** All issuances are append-only to a public log. Brands cannot silently revoke past claims. Experts cannot silently un-attest.
4. **Travels with the SKU, not the storefront.** Claims must be readable by any PDP, PIM, ad-tech, retailer feed, AI shopping agent, or regulator inspector — without proprietary clients.
5. **Open spec, neutral governance.** Spec lives on GitHub under CC-BY-4.0. Reference implementation under MIT. Founding members signed within 60 days of v0.1; donation to Linux Foundation within 12 months.

## Core types (v0.1)

### `EndorsementClaim`
```json
{
  "@context": "https://pcec.dev/v0/context.jsonld",
  "type": "EndorsementClaim",
  "id": "urn:pcec:claim:01HZ123XYZ...",
  "sku": "urn:gtin:00850001234567",
  "claim_text": "Supports joint mobility in senior dogs",
  "claim_kind": "efficacy",
  "issued_at": "2026-05-18T15:00:00Z",
  "expires_at": "2027-05-18T15:00:00Z",
  "issuer": "did:web:pawconscious.com",
  "evidence": [{ "type": "EvidenceBundle", "id": "urn:pcec:evidence:..." }],
  "attestations": [{ "type": "ExpertAttestation", "id": "urn:pcec:att:..." }],
  "audit": { "type": "AuditVerdict", "id": "urn:pcec:audit:..." },
  "signature": { "type": "Ed25519Signature2020", "...": "..." }
}
```

### `EvidenceBundle`
```json
{
  "@context": "https://pcec.dev/v0/context.jsonld",
  "type": "EvidenceBundle",
  "id": "urn:pcec:evidence:...",
  "claim": "urn:pcec:claim:...",
  "papers": [
    {
      "pmid": "31234567",
      "doi": "10.1234/example",
      "relevance_score": 0.87,
      "citation_count": 247,
      "influential_citation_count": 18,
      "agent_signature": "..."
    }
  ],
  "agent_runs": [
    { "agent_did": "did:web:pawconscious.com:agents:evidence-grader", "run_id": "...", "signature": "..." }
  ]
}
```

### `ExpertAttestation`
```json
{
  "@context": "https://pcec.dev/v0/context.jsonld",
  "type": "ExpertAttestation",
  "id": "urn:pcec:att:...",
  "claim": "urn:pcec:claim:...",
  "expert": "did:web:bostonvet.example:experts:dr-smith",
  "credential": {
    "type": "VeterinaryLicense",
    "jurisdiction": "MA",
    "license_number": "VET-12345",
    "verified_at": "2026-05-18T15:00:00Z"
  },
  "rubric_score": { "scale": "1-5", "value": 4 },
  "rationale": "Three RCTs support the joint-mobility claim in dogs >7yr",
  "signature": "..."
}
```

### `AuditVerdict`
```json
{
  "@context": "https://pcec.dev/v0/context.jsonld",
  "type": "AuditVerdict",
  "id": "urn:pcec:audit:...",
  "claim": "urn:pcec:claim:...",
  "auditor": "did:web:pawconscious.com:agents:auditor",
  "verdict": "PASS",
  "challenges_run": [
    "citation_existence",
    "claim_direction_match",
    "cherry_pick_check",
    "sample_size_adequacy"
  ],
  "findings": [],
  "signature": "..."
}
```

## Embedding in the wild

### HTML PDP
```html
<meta name="pcec-claim" content="urn:pcec:claim:01HZ123XYZ..."/>
<script src="https://pawconscious.com/embed/PAW-2026-NATIVE.js" async></script>
```

### Image-bound (via C2PA assertion)
PCEC defines a C2PA assertion `pcec.endorsement-claim` containing the claim URN. C2PA-aware tools (Adobe Express, Microsoft Office, browsers) display the claim provenance inline with the image.

### Product feed (Shopify, Akeneo, Salsify, Meta Catalog, TikTok Shop)
Add `pcec_claim_id` as a custom metafield. Downstream feeds (Klaviyo, Recharge, ad-tech) read the metafield and resolve the bundle via the resolver API.

### Resolver API
`GET https://resolve.pcec.dev/v0/claim/{urn}` → returns full claim + evidence + attestations + audit JSON-LD.

### A2A agent skill
Any LLM agent can call `verify_claim(sku, claim_text)` on a PCEC-supporting mesh to get a real-time trust score before answering a user.

## Trust model

Trust roots are operated by neutral parties. v0.1 ships with one trust root (`did:web:pcec.dev`) maintained by PawConscious. v1.0 (post-Linux Foundation donation) ships with N trust roots maintained by founding members.

Browser / agent / regulator trust stores ship the public keys of trust roots. Compromised roots are revocable via the transparency log + emergency rotation.

## Conformance levels

- **PCEC-Conformant Issuer:** can sign valid claims, evidence, attestations, audits
- **PCEC-Conformant Resolver:** can dereference any claim URN to its bundle
- **PCEC-Conformant Embedder:** correctly embeds + renders claim metadata
- **PCEC-Conformant Validator:** can verify all signatures, check transparency log inclusion, and produce a verdict

## v0.1 → v1.0 path

| v0.1 (hackathon) | v1.0 (post-LinuxFoundation) |
|---|---|
| 1 trust root | N trust roots |
| Software Ed25519 signing | HSM signing required |
| Transparency log on Firestore | Sigstore-compatible Rekor instance |
| 1 founding member (PawConscious) | 6-8 founding members |
| 1 vertical (pet) | N verticals |
| MIT reference impl | + ISO submission |

## Not in v0.1
- ZK-proofs for evidence privacy (post-v2)
- Cross-jurisdiction expert credential federation (post-v2)
- Revocation networks (deferred)
- Stake-based slashing for misbehaving signers (post-v2)

## How to contribute
File issues at `github.com/odominguez7/PawConscious-Mesh-GFS/issues`. Implementers welcome; founding-member program opens 2026-06-15 (post-hackathon).
