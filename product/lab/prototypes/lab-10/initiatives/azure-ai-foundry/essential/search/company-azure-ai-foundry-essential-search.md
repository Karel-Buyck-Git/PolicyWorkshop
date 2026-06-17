# Company Azure AI Foundry Essential — Search

## Tier rationale

**Essential** — Baseline hygiene for Search: the non-negotiable controls every deployment should enforce from day one. This tier delivers RBAC and managed-identity controls eliminating shared credentials and TLS / HTTPS enforcement preventing in-transit interception. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure AI Search services should have local authentication methods disabled | 6300012e-e9a4-4649-b41f-a85f5c43be91 |  | Disabling local authentication methods improves security by ensuring that Azure AI Search services exclusively require Azure Active Directory identities for authentication. Learn more at: https://aka.ms/azure-cognitive-search/rbac. Note that while the disable local authentication parameter is still in preview, the deny effect for this policy may result in limited Azure AI Search portal functionality since some features of the Portal use the GA API which does not support the parameter. | Audit, Deny, Disabled | Audit | Audit | Deny | Search | Azure AI Foundry | 1.0.1 | BuiltIn | Essential | No | No |
| 2 | Configure Azure AI Search services to disable local authentication | 4eb216f2-9dba-4979-86e6-5d7e63ce3b75 |  | Disable local authentication methods so that your Azure AI Search services exclusively require Azure Active Directory identities for authentication. Learn more at: https://aka.ms/azure-cognitive-search/rbac. | Modify, Disabled | Modify | Modify | Modify | Search | Azure AI Foundry | 2.0.0 | BuiltIn | Essential | No | Yes |
