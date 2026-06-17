# Company DevOps Essential — Custom Provider

## Tier rationale

**Essential** — Baseline hygiene for Custom Provider: the non-negotiable controls every deployment should enforce from day one. This tier protects against credential theft, unencrypted data exposure, and accidental data loss for Custom Provider workloads. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Deploy associations for a custom provider | c15c281f-ea5c-44cd-90b8-fc3c14d13f0c |  | Deploys an association resource that associates selected resource types to the specified custom provider. This policy deployment does not support nested resource types. | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | Custom Provider | DevOps | 1.0.0 | BuiltIn | Essential | Yes | Yes |
