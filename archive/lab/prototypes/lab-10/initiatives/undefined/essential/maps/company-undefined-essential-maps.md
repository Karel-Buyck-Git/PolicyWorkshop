# Company undefined Essential — Maps

## Tier rationale

**Essential** — Baseline hygiene for Maps: the non-negotiable controls every deployment should enforce from day one. This tier protects against credential theft, unencrypted data exposure, and accidental data loss for Maps workloads. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Maps account should not process data globally. | c707daa0-b93b-454d-9e1e-8ac59866316c |  | This policy restricts the data processing locations you can add to your Azure Maps accounts. Use to enforce your geo-compliance requirements. | Audit, Deny, Disabled | Deny | Audit | Deny | Maps | undefined | 1.0.0 | BuiltIn | Essential | No | No |
