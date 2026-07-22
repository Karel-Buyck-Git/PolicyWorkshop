# Company Management Essential — Automation

## Tier rationale

**Essential** — Baseline hygiene for Automation: the non-negotiable controls every deployment should enforce from day one. This tier delivers RBAC and managed-identity controls eliminating shared credentials and encryption-at-rest with service-managed keys. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Automation Account should have Managed Identity | dea83a72-443c-4292-83d5-54a2f98749c0 |  | Use Managed Identities as the recommended method for authenticating with Azure resources from the runbooks. Managed identity for authentication is more secure and eliminates the management overhead associated with using RunAs Account in your runbook code . | Audit, Disabled | Audit | Audit | Audit | Automation | Management | 1.0.0 | BuiltIn | Essential | No | No |
| 2 | Automation account variables should be encrypted | 3657f5a0-770e-44a3-b44e-9431ba1e9735 |  | It is important to enable encryption of Automation account variable assets when storing sensitive data | Audit, Deny, Disabled | Audit | Audit | Deny | Automation | Management | 1.1.0 | BuiltIn | Essential | No | No |
| 3 | Azure Automation account should have local authentication method disabled | 48c5f1cb-14ad-4797-8e3b-f78ab3f8d700 |  | Disabling local authentication methods improves security by ensuring that Azure Automation accounts exclusively require Azure Active Directory identities for authentication. | Audit, Deny, Disabled | Audit | Audit | Deny | Automation | Management | 1.0.0 | BuiltIn | Essential | No | No |
| 4 | Configure Azure Automation account to disable local authentication | 30d1d58e-8f96-47a5-8564-499a3f3cca81 |  | Disable local authentication methods so that your Azure Automation accounts exclusively require Azure Active Directory identities for authentication. | Modify, Disabled | Modify | Modify | Modify | Automation | Management | 1.0.0 | BuiltIn | Essential | No | Yes |
