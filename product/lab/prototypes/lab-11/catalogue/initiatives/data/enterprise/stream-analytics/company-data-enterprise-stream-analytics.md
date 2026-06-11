# Company Data Enterprise — Stream Analytics

## Tier rationale

**Enterprise** — Zero-trust and regulatory alignment for Stream Analytics: controls that require infrastructure investment or map directly to compliance frameworks. This tier delivers diagnostic settings streaming to Log Analytics / Event Hub / Sentinel and customer-managed keys (CMK / BYOK) for cryptographic sovereignty. Together these policies protect against lateral movement, sovereign-data exfiltration, and audit gaps in regulated workloads. Maps to NIS2 Articles 21–23, ISO 27001 A.13.1.3 (network segregation) and A.18 (compliance), NIST SP 800-207 (Zero Trust).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Stream Analytics jobs should use customer-managed keys to encrypt data | 87ba29ef-1ab3-4d82-b763-87fcd4f531f7 |  | Use customer-managed keys when you want to securely store any metadata and private data assets of your Stream Analytics jobs in your storage account. This gives you total control over how your Stream Analytics data is encrypted. | Audit, Audit, Deny, Deny, Disabled, Disabled | Audit | Audit | Deny | Stream Analytics | Data | 1.1.0 | BuiltIn | Enterprise | No | No |
| 2 | Resource logs in Azure Stream Analytics should be enabled | f9be5368-9bf5-4b84-9e0a-7850da98bb46 |  | Audit enabling of resource logs. This enables you to recreate activity trails to use for investigation purposes; when a security incident occurs or when your network is compromised | AuditIfNotExists, Disabled | AuditIfNotExists | AuditIfNotExists | AuditIfNotExists | Stream Analytics | Data | 5.0.0 | BuiltIn | Enterprise | No | No |
