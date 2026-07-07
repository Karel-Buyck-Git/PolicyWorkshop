# Company Integration Essential — Web PubSub

## Tier rationale

**Essential** — Baseline hygiene for Web PubSub: the non-negotiable controls every deployment should enforce from day one. This tier delivers RBAC and managed-identity controls eliminating shared credentials. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Web PubSub Service should enable diagnostic logs | ee8a7be2-e9b5-47b9-9d37-d9b141ea78a4 |  | Audit enabling of diagnostic logs. This enables you to recreate activity trails to use for investigation purposes; when a security incident occurs or when your network is compromised | AuditIfNotExists, Disabled | AuditIfNotExists | AuditIfNotExists | AuditIfNotExists | Web PubSub | Integration | 1.0.0 | BuiltIn | Essential | No | No |
| 2 | Azure Web PubSub Service should have local authentication methods disabled | b66ab71c-582d-4330-adfd-ac162e78691e |  | Disabling local authentication methods improves security by ensuring that Azure Web PubSub Service exclusively require Azure Active Directory identities for authentication. | Audit, Deny, Disabled | Audit | Audit | Deny | Web PubSub | Integration | 1.0.0 | BuiltIn | Essential | No | No |
| 3 | Configure Azure Web PubSub Service to disable local authentication | 17f9d984-90c8-43dd-b7a6-76cb694815c1 |  | Disable local authentication methods so that your Azure Web PubSub Service exclusively requires Azure Active Directory identities for authentication. | Modify, Disabled | Modify | Modify | Modify | Web PubSub | Integration | 1.0.0 | BuiltIn | Essential | No | Yes |
