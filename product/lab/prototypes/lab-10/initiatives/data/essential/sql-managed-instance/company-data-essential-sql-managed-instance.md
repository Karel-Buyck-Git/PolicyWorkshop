# Company Data Essential — SQL Managed Instance

## Tier rationale

**Essential** — Baseline hygiene for SQL Managed Instance: the non-negotiable controls every deployment should enforce from day one. This tier delivers TLS / HTTPS enforcement preventing in-transit interception and encryption-at-rest with service-managed keys. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | TLS protocol 1.2 must be used for Arc SQL managed instances. | bb3c7464-033e-41ee-81dc-480fde675b20 |  | As a part of network settings, Microsoft recommends allowing only TLS 1.2 for TLS protocols in SQL Servers. Learn more on network settings for SQL Server at https://aka.ms/TlsSettingsSQLServer. | Audit, Disabled | Audit | Audit | Audit | SQL Managed Instance | Data | 1.0.0 | BuiltIn | Essential | No | No |
| 2 | Transparent Data Encryption must be enabled for Arc SQL managed instances. | 6599ab01-29bc-4852-a6f5-de9e2151714a |  | Enable transparent data encryption (TDE) at-rest on an Azure Arc-enabled SQL Managed Instance. Learn more at https://aka.ms/EnableTDEArcSQLMI. | Audit, Disabled | Audit | Audit | Audit | SQL Managed Instance | Data | 1.0.0 | BuiltIn | Essential | No | No |
