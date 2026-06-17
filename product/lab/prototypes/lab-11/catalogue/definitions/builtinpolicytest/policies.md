# BuiltInPolicyTest Policies

## Tier rationale

**Essential** — Baseline hygiene for BuiltInPolicyTest: the non-negotiable controls every deployment should enforce from day one. This tier delivers tagging, SKU, and naming controls for cost and ownership accountability. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

**Professional** — Active security posture for BuiltInPolicyTest: controls that produce signals an operations team must act on. This tier delivers auto-remediation deployments. Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

**Enterprise** — No enterprise-tier policies are defined for BuiltInPolicyTest in the current built-in policy set.

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Requires resources to not have a specific tag. This is a versioning test built-in. | 36fd7371-8eb7-4321-9c30-a7100022d048 |  | Denies the creation of a resource that contains the given tag. Does not apply to resource groups. | Yes | No | Audit, Deny, Disabled | Audit | Audit | Deny | BuiltInPolicyTest | Undefined | 2.0.1 | BuiltIn | Essential |
| 2 | Append a tag and its value to resources - This built-in is created for versioning test. | 125b7269-7ec9-47bf-8beb-8865b61c2c95 | Preview | Appends the specified tag and value when any resource which is missing this tag is created or updated. Does not modify the tags of resources created before this policy was applied until those resources are changed. Does not apply to resource groups. New 'modify' effect policies are available that support remediation of tags on existing resources (see https://aka.ms/modifydoc). | Yes | No | Append, Disabled | Append | Append | Append | BuiltInPolicyTest | Undefined | 1.0.0-preview | BuiltIn | Professional |
