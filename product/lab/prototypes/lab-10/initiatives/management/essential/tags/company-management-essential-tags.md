# Company Management Essential — Tags

## Tier rationale

**Essential** — Baseline hygiene for Tags: the non-negotiable controls every deployment should enforce from day one. This tier delivers tagging, SKU, and naming controls for cost and ownership accountability. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Require a tag and its value on resource groups | 8ce3da23-7156-49e4-b145-24f95f9dcb46 |  | Enforces a required tag and its value on resource groups. | Deny | Deny | Deny | Deny | Tags | Management | 1.0.0 | BuiltIn | Essential | Yes | No |
| 2 | Require a tag and its value on resources | 1e30110a-5ceb-460c-a204-c1c3969c6d62 |  | Enforces a required tag and its value. Does not apply to resource groups. | Deny | Deny | Deny | Deny | Tags | Management | 1.0.1 | BuiltIn | Essential | Yes | No |
| 3 | Require a tag on resource groups | 96670d01-0a4d-4649-9c89-2d3abc0a5025 |  | Enforces existence of a tag on resource groups. | Deny | Deny | Deny | Deny | Tags | Management | 1.0.0 | BuiltIn | Essential | Yes | No |
| 4 | Require a tag on resources | 871b6d14-10aa-478d-b590-94f262ecfa99 |  | Enforces existence of a tag. Does not apply to resource groups. | Deny | Deny | Deny | Deny | Tags | Management | 1.0.1 | BuiltIn | Essential | Yes | No |
