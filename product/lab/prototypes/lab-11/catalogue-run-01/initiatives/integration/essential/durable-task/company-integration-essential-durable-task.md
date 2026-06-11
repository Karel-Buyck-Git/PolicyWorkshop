# Company Integration Essential — Durable Task

## Tier rationale

**Essential** — Baseline hygiene for Durable Task: the non-negotiable controls every deployment should enforce from day one. This tier protects against credential theft, unencrypted data exposure, and accidental data loss for Durable Task workloads. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Durable Task schedulers should not allow open IP allowlists | d82527a7-91cd-409f-b96e-049600b16b9e |  | Deny Durable Task schedulers that include 0.0.0.0/0 in their IP allowlist to prevent exposure to the public internet. Remove the open entry so that only trusted networks can reach the scheduler. | Audit, Deny, Disabled | Audit | Audit | Deny | Durable Task | Integration | 1.0.0 | BuiltIn | Essential | No | No |
