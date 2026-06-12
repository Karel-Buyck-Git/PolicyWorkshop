# Custom Provider Policies

## Tier rationale

**Essential** — Baseline hygiene for Custom Provider: the non-negotiable controls every deployment should enforce from day one. This tier protects against credential theft, unencrypted data exposure, and accidental data loss for Custom Provider workloads. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

**Professional** — No professional-tier policies are defined for Custom Provider in the current built-in policy set.

**Enterprise** — No enterprise-tier policies are defined for Custom Provider in the current built-in policy set.

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Deploy associations for a custom provider | c15c281f-ea5c-44cd-90b8-fc3c14d13f0c |  | Deploys an association resource that associates selected resource types to the specified custom provider. This policy deployment does not support nested resource types. | Yes | Yes | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | Custom Provider | DevOps | 1.0.0 | BuiltIn | Essential |
