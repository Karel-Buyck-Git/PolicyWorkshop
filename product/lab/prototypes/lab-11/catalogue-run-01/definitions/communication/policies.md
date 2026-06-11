# Communication Policies

## Tier rationale

**Essential** — Baseline hygiene for Communication: the non-negotiable controls every deployment should enforce from day one. This tier delivers RBAC and managed-identity controls eliminating shared credentials. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

**Professional** — No professional-tier policies are defined for Communication in the current built-in policy set.

**Enterprise** — No enterprise-tier policies are defined for Communication in the current built-in policy set.

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Communication service resource should use a managed identity | bcff6755-335b-484d-b435-d1161db39cdc |  | Assigning a managed identity to your Communication service resource helps ensure secure authentication. This identity is used by this Communication service resource to communicate with other Azure services, like Azure Storage, in a secure way without you having to manage any credentials. | Audit, Deny, Disabled | Audit | Audit | Deny | Communication | Integration | 1.0.0 | BuiltIn | Essential | No | No |
| 2 | Communication service resource should use allow listed data location | 93c45b74-42a1-4967-b25d-82c4dc630921 |  | Create a Communication service resource only from an allow listed data location. This data location determines where the data of the communication service resource will be stored at rest, ensuring your preferred allow listed data locations as this cannot be changed after resource creation. | Audit, Deny, Disabled | Audit | Audit | Deny | Communication | Integration | 1.0.0 | BuiltIn | Essential | Yes | No |
| 3 | Communication services resource should have local authentication methods disabled | fc264132-db9c-4302-bb7d-3994c36461fe |  | Disabling local authentication methods improves security by ensuring that Communication services resource exclusively require Microsoft Entra ID identities for authentication. | Audit, Deny, Disabled | Audit | Audit | Deny | Communication | Integration | 1.0.0 | BuiltIn | Essential | No | No |
| 4 | Communication services should have local authentication disabled | 145408bc-d134-468a-ae3b-1eaf3b9e5ac7 |  | This policy ensures that local authentication methods are disabled for Communication services, requiring Microsoft Entra ID identities for authentication. Enforcing this policy helps improve security by preventing the use of less secure local authentication. | Modify, Disabled | Modify | Modify | Modify | Communication | Integration | 1.1.0 | BuiltIn | Essential | No | Yes |
