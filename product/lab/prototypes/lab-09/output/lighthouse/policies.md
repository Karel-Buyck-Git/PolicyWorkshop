# Lighthouse Policies

## Tier rationale

**Essential** — Baseline hygiene for Lighthouse: the non-negotiable controls every deployment should enforce from day one. This tier protects against credential theft, unencrypted data exposure, and accidental data loss for Lighthouse workloads. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

**Professional** — No professional-tier policies are defined for Lighthouse in the current built-in policy set.

**Enterprise** — No enterprise-tier policies are defined for Lighthouse in the current built-in policy set.

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Allow managing tenant ids to onboard through Azure Lighthouse | 7a8a51a3-ad87-4def-96f3-65a1839242b6 |  | Restricting Azure Lighthouse delegations to specific managing tenants increases security by limiting those who can manage your Azure resources. | deny | deny | deny | Lighthouse | Management | 1.0.1 | BuiltIn | Essential |
| 2 | Audit delegation of scopes to a managing tenant | 76bed37b-484f-430f-a009-fd7592dff818 |  | Audit delegation of scopes to a managing tenant via Azure Lighthouse. | Audit, Disabled | Audit | Audit | Lighthouse | Management | 1.0.0 | BuiltIn | Essential |
