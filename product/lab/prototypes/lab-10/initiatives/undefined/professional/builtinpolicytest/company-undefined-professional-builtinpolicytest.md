# Company undefined Professional — BuiltInPolicyTest

## Tier rationale

**Professional** — Active security posture for BuiltInPolicyTest: controls that produce signals an operations team must act on. This tier delivers auto-remediation deployments. Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Append a tag and its value to resources - This built-in is created for versioning test. | 125b7269-7ec9-47bf-8beb-8865b61c2c95 | Preview | Appends the specified tag and value when any resource which is missing this tag is created or updated. Does not modify the tags of resources created before this policy was applied until those resources are changed. Does not apply to resource groups. New 'modify' effect policies are available that support remediation of tags on existing resources (see https://aka.ms/modifydoc). | Append, Disabled | Append | Append | Append | BuiltInPolicyTest | undefined | 1.0.0-preview | BuiltIn | Professional | Yes | No |
