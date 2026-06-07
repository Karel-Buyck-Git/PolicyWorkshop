# Company undefined Essential — BuiltInPolicyTest

## Tier rationale

**Essential** — Baseline hygiene for BuiltInPolicyTest: the non-negotiable controls every deployment should enforce from day one. This tier delivers tagging, SKU, and naming controls for cost and ownership accountability. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Requires resources to not have a specific tag. This is a versioning test built-in. | 36fd7371-8eb7-4321-9c30-a7100022d048 |  | Denies the creation of a resource that contains the given tag. Does not apply to resource groups. | Audit, Deny, Disabled | Audit | Audit | Deny | BuiltInPolicyTest | undefined | 2.0.1 | BuiltIn | Essential | Yes | No |
