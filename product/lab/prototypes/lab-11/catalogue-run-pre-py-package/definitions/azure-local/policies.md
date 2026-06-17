# Azure Local Policies

## Tier rationale

**Essential** — Baseline hygiene for Azure Local: the non-negotiable controls every deployment should enforce from day one. This tier protects against credential theft, unencrypted data exposure, and accidental data loss for Azure Local workloads. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

**Professional** — No professional-tier policies are defined for Azure Local in the current built-in policy set.

**Enterprise** — No enterprise-tier policies are defined for Azure Local in the current built-in policy set.

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Restrict resource types to Azure services supported in Azure Local disconnected operations | dabf7c7f-5354-42de-a92a-8367f538dd71 | Preview | Restrict the use of Azure services to those supported in Azure Local disconnected operations. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Azure Local | Compute | 1.0.0-preview | BuiltIn | Essential |
