# Company Management Essential — Managed Application

## Tier rationale

**Essential** — Baseline hygiene for Managed Application: the non-negotiable controls every deployment should enforce from day one. This tier protects against credential theft, unencrypted data exposure, and accidental data loss for Managed Application workloads. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Deploy associations for a managed application | 17763ad9-70c0-4794-9397-53d765932634 |  | Deploys an association resource that associates selected resource types to the specified managed application.  This policy deployment does not support nested resource types. | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | Managed Application | Management | 1.0.0 | BuiltIn | Essential | Yes | Yes |
