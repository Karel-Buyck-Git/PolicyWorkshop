# Company Integration Essential — SignalR

## Tier rationale

**Essential** — Baseline hygiene for SignalR: the non-negotiable controls every deployment should enforce from day one. This tier delivers RBAC and managed-identity controls eliminating shared credentials. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure SignalR Service should enable diagnostic logs | d9f1f9a9-8795-49f9-9e7b-e11db14caeb2 |  | Audit enabling of diagnostic logs. This enables you to recreate activity trails to use for investigation purposes; when a security incident occurs or when your network is compromised | AuditIfNotExists, Disabled | AuditIfNotExists | AuditIfNotExists | AuditIfNotExists | SignalR | Integration | 1.0.0 | BuiltIn | Essential | No | No |
| 2 | Azure SignalR Service should have local authentication methods disabled | f70eecba-335d-4bbc-81d5-5b17b03d498f |  | Disabling local authentication methods improves security by ensuring that Azure SignalR Service exclusively require Azure Active Directory identities for authentication. | Audit, Deny, Disabled | Audit | Audit | Deny | SignalR | Integration | 1.0.0 | BuiltIn | Essential | No | No |
| 3 | Configure Azure SignalR Service to disable local authentication | 702133e5-5ec5-4f90-9638-c78e22f13b39 |  | Disable local authentication methods so that your Azure SignalR Service exclusively requires Azure Active Directory identities for authentication. | Modify, Disabled | Modify | Modify | Modify | SignalR | Integration | 1.0.0 | BuiltIn | Essential | No | Yes |
