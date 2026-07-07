# Company Data Essential — Azure Data Explorer

## Tier rationale

**Essential** — Baseline hygiene for Azure Data Explorer: the non-negotiable controls every deployment should enforce from day one. This tier delivers encryption-at-rest with service-managed keys. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | All Database Admin on Azure Data Explorer should be disabled | 8945ba5e-918e-4a57-8117-fe615d12e3ba |  | Disable all database admin role to restrict granting highly privileged/administrative user role. | Audit, Deny, Disabled | Audit | Audit | Deny | Azure Data Explorer | Data | 1.0.0 | BuiltIn | Essential | No | No |
| 2 | Disk encryption should be enabled on Azure Data Explorer | f4b53539-8df9-40e4-86c6-6b607703bd4e |  | Enabling disk encryption helps protect and safeguard your data to meet your organizational security and compliance commitments. | Audit, Deny, Disabled | Audit | Audit | Deny | Azure Data Explorer | Data | 2.0.0 | BuiltIn | Essential | No | No |
| 3 | Double encryption should be enabled on Azure Data Explorer | ec068d99-e9c7-401f-8cef-5bdde4e6ccf1 |  | Enabling double encryption helps protect and safeguard your data to meet your organizational security and compliance commitments. When double encryption has been enabled, data in the storage account is encrypted twice, once at the service level and once at the infrastructure level, using two different encryption algorithms and two different keys. | Audit, Deny, Disabled | Audit | Audit | Deny | Azure Data Explorer | Data | 2.0.0 | BuiltIn | Essential | No | No |
