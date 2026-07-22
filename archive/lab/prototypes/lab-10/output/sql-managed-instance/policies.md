# SQL Managed Instance Policies

## Tier rationale

**Essential** — Baseline hygiene for SQL Managed Instance: the non-negotiable controls every deployment should enforce from day one. This tier delivers TLS / HTTPS enforcement preventing in-transit interception and encryption-at-rest with service-managed keys. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

**Professional** — No professional-tier policies are defined for SQL Managed Instance in the current built-in policy set.

**Enterprise** — Zero-trust and regulatory alignment for SQL Managed Instance: controls that require infrastructure investment or map directly to compliance frameworks. This tier delivers customer-managed keys (CMK / BYOK) for cryptographic sovereignty. Together these policies protect against lateral movement, sovereign-data exfiltration, and audit gaps in regulated workloads. Maps to NIS2 Articles 21–23, ISO 27001 A.13.1.3 (network segregation) and A.18 (compliance), NIST SP 800-207 (Zero Trust).

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | TLS protocol 1.2 must be used for Arc SQL managed instances. | bb3c7464-033e-41ee-81dc-480fde675b20 |  | As a part of network settings, Microsoft recommends allowing only TLS 1.2 for TLS protocols in SQL Servers. Learn more on network settings for SQL Server at https://aka.ms/TlsSettingsSQLServer. | Audit, Disabled | Audit | Audit | Audit | SQL Managed Instance | Data | 1.0.0 | BuiltIn | Essential | No | No |
| 2 | Transparent Data Encryption must be enabled for Arc SQL managed instances. | 6599ab01-29bc-4852-a6f5-de9e2151714a |  | Enable transparent data encryption (TDE) at-rest on an Azure Arc-enabled SQL Managed Instance. Learn more at https://aka.ms/EnableTDEArcSQLMI. | Audit, Disabled | Audit | Audit | Audit | SQL Managed Instance | Data | 1.0.0 | BuiltIn | Essential | No | No |
| 3 | Customer managed key encryption must be used as part of CMK Encryption for Arc SQL managed instances. | 413923f0-ff16-41ae-8583-90c5c5d9fa8f |  | As a part of CMK encryption, Customer managed key encryption must be used. Learn more at https://aka.ms/EnableTDEArcSQLMI. | Audit, Disabled | Audit | Audit | Audit | SQL Managed Instance | Data | 1.0.0 | BuiltIn | Enterprise | No | No |
