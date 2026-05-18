# Independence Principle

**Status:** Architectural commitment v1 · 2026-05-18

> Trust infrastructure must be structurally independent of the parties being verified. ACP is third-party. Brands pay us per claim. Retailers pay us platform fees. Neither side can alter the rubric. The audit trail is public.

This is how SOC2, PCI-DSS, and C2PA work. It is why Trustpilot has a credibility problem (pay-for-reviews). It is why we avoid that pattern from day one.

## The 6 architectural commitments

### 1. ACP is third-party. Retailers can be customers, never operators.

Chewy, Petco, Amazon Pet may pay ACP for catalog-wide verification. They cannot run ACP internally. The mesh is operated by PawConscious (now), donated to Linux Foundation (Y2+).

**Anti-pattern we reject:** "Chewy Verified" as a Chewy-owned trust mark. That collapses Chewy's commercial interest into Chewy's trust verification. Same problem as Amazon Choice — opaque, biased, unaccountable.

**Our pattern:** ACP Verified appears on Chewy PDPs because the brand paid ACP independently. Chewy's only role is making the badge visible on their UI.

### 2. Same rate card for everyone.

Chewy private-label brands (`Frisco`, `American Journey`, `Tylee's`) pay the same per-claim fee as Native Pet, Honest Paws, or any independent. No discount, no priority routing, no algorithm favor.

**Anti-pattern we reject:** retailer private label gets free or favored verification.

### 3. Public audit trail.

Every cert is Ed25519-signed and anchored to a transparency log. Every grounding source (PubMed PMID, FTC §255 snippet) is hashed (sha256). Anyone can verify a cert's evidence chain and a brand can't silently re-issue.

**Implementation:** `/pcec/v0/claim/{urn}` resolver returns the full bundle. Transparency log = public-read Firestore (Phase 11 wiring). Bundle hash + signature already shipped (Phase 4-5).

### 4. Vet panel is academic, not retailer-affiliated.

Vet attestations come from academic clinical-nutrition programs (Tufts Cummings, Cornell CVM, UPenn PennVet, UC Davis VMTH) — regulator-credible, financial-conflict-free.

**Anti-pattern we reject:** Chewy's in-house veterinary advisor signing attestations on Chewy private-label products. That's the structural conflict we exist to prevent.

### 5. PCEC spec donated to Linux Foundation (Y2+).

Standards body governance prevents any single company — including us — from manipulating scoring rules. Same model as C2PA (Adobe couldn't unilaterally rewrite watermark verification rules) and OpenID Connect.

**Implication:** brands and retailers cannot lobby ACP to change rubrics. They lobby Linux Foundation, which requires broad consensus.

### 6. Retailer contracts cap operational influence.

Chewy may pay $1M/yr for catalog verification API. They cannot purchase rubric changes, scoring preferences, or sealed-envelope deals. Same as SOC2 — AWS pays Deloitte for the audit, but AWS cannot tell Deloitte what to score.

**Contractual:** all retailer/insurer enterprise contracts include a clause: "ACP scoring methodology is determined by [Linux Foundation governance / PawConscious independent vet board, pre-LF donation]. Customer cannot direct scoring outcomes for individual products or brands."

## How this answers Series A red flags

When an a16z infra investor asks "what stops you from being captured by the largest retailer customer?" the answer is:

> "Three structural firewalls. (1) Rate card is public and uniform — Chewy private label pays exactly what an indie brand pays per claim. (2) Audit trail is public — anyone can verify any cert's evidence chain. (3) Scoring methodology is governed by an independent vet advisory board today, Linux Foundation tomorrow. None of these can be changed by a paying customer, even our largest. It's the same model that made SOC2 trustworthy: the auditor (us) cannot be directed by the audited party (the retailer)."

## How this answers regulator concerns

When the FTC or NY AG asks "why should we treat ACP Verified as evidence?" the answer is:

> "Our verification methodology is public (PCEC v0.1 spec, MIT-licensed code, open audit trail). Every cert is cryptographically signed, every evidence source is hashed, every vet attestation is signed by a DID anchored to an academic credential. The methodology cannot be silently modified by any party including the brand being verified. The structural pattern matches accredited certification (ISO 17065), which courts already accept as substantiation."

## How this differentiates from Trustpilot

Trustpilot accepts paid placements; brands can boost favorable reviews; pay-for-removal is alleged. Their consumer-facing trust mark has eroded specifically because the commercial model is captured by the verified parties.

ACP cannot accept paid score changes because:
- The score is computed by deterministic agent pipeline + public corpus
- The bundle is cryptographically signed against an immutable methodology hash
- Removing a violation requires the brand to actually fix the underlying claim, not pay us off
- Anyone can re-run the pipeline against the same URL and get the same result (deterministic temperature=0 Gemini calls + open corpus)

## Why this matters for Track 3 rubric

The hackathon rules say B2B. Enterprise B2B trust infrastructure that captures buyers is a known failure mode (Trustpilot, Yelp). Demonstrating structural independence pre-empts the "how do you avoid capture" red flag and turns it into a moat narrative.

## Public commitment

This doc is public, MIT-licensed in the repo. By committing it pre-revenue, we make capture harder — any future deviation would be a documented betrayal of the v1 principle, visible in git history.

## Related docs

- `BUSINESS_PLAN.md` — full thesis + Y1-Y5 arc
- `docs/PCEC-v0.md` — spec draft
- `docs/A2A-AGENT-CARD.md` — public protocol surface
- `START_HERE.md` — one-doc consolidated view
