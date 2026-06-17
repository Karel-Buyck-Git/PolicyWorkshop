# Company Data Enterprise — SQL Managed Instance

## Tier rationale

**Enterprise** — Zero-trust and regulatory alignment for SQL Managed Instance: controls that require infrastructure investment or map directly to compliance frameworks. This tier delivers customer-managed keys (CMK / BYOK) for cryptographic sovereignty. Together these policies protect against lateral movement, sovereign-data exfiltration, and audit gaps in regulated workloads. Maps to NIS2 Articles 21–23, ISO 27001 A.13.1.3 (network segregation) and A.18 (compliance), NIST SP 800-207 (Zero Trust).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Customer managed key encryption must be used as part of CMK Encryption for Arc SQL managed instances. | 413923f0-ff16-41ae-8583-90c5c5d9fa8f |  | As a part of CMK encryption, Customer managed key encryption must be used. Learn more at https://aka.ms/EnableTDEArcSQLMI. | Audit, Disabled | Audit | Audit | Audit | SQL Managed Instance | Data | 1.0.0 | BuiltIn | Enterprise | No | No |
