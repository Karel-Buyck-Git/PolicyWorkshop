# Company Compute Essential — Batch

## Tier rationale

**Essential** — Baseline hygiene for Batch: the non-negotiable controls every deployment should enforce from day one. This tier delivers RBAC and managed-identity controls eliminating shared credentials, TLS / HTTPS enforcement preventing in-transit interception, and encryption-at-rest with service-managed keys. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Batch pools should have disk encryption enabled | 1760f9d4-7206-436e-a28f-d9f3a5c8a227 |  | Enabling Azure Batch disk encryption ensures that data is always encrypted at rest on your Azure Batch compute node. Learn more about disk encryption in Batch at https://docs.microsoft.com/azure/batch/disk-encryption. | Audit, Disabled, Deny | Audit | Audit | Deny | Batch | Compute | 1.0.0 | BuiltIn | Essential | No | No |
| 2 | Batch accounts should have local authentication methods disabled | 6f68b69f-05fe-49cd-b361-777ee9ca7e35 |  | Disabling local authentication methods improves security by ensuring that Batch accounts require Azure Active Directory identities exclusively for authentication. Learn more at: https://aka.ms/batch/auth. | Audit, Deny, Disabled | Audit | Audit | Deny | Batch | Compute | 1.0.0 | BuiltIn | Essential | No | No |
| 3 | Configure Batch accounts to disable local authentication | 4dbc2f5c-51cf-4e38-9179-c7028eed2274 |  | Disable location authentication methods so that your Batch accounts require Azure Active Directory identities exclusively for authentication. Learn more at: https://aka.ms/batch/auth. | Modify, Disabled | Modify | Modify | Modify | Batch | Compute | 1.0.0 | BuiltIn | Essential | No | Yes |
