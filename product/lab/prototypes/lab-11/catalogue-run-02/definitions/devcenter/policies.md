# DevCenter Policies

## Tier rationale

**Essential** — Baseline hygiene for DevCenter: the non-negotiable controls every deployment should enforce from day one. This tier protects against credential theft, unencrypted data exposure, and accidental data loss for DevCenter workloads. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

**Professional** — No professional-tier policies are defined for DevCenter in the current built-in policy set.

**Enterprise** — No enterprise-tier policies are defined for DevCenter in the current built-in policy set.

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Microsoft Dev Box Pools should not use Microsoft Hosted Networks. | ece3c79b-2caf-470d-a5f5-66470c4fc649 | Preview | Disallows the use of Microsoft Hosted Networks when creating Pool resources. | Audit, Deny, Disabled | Audit | Audit | Deny | DevCenter | DevOps | 1.0.0-preview | BuiltIn | Essential | No | No |
