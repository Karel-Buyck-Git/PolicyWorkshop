# Stream Analytics Policies

## Tier rationale

**Essential** — Baseline hygiene for Stream Analytics: the non-negotiable controls every deployment should enforce from day one. This tier delivers RBAC and managed-identity controls eliminating shared credentials. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

**Professional** — No professional-tier policies are defined for Stream Analytics in the current built-in policy set.

**Enterprise** — Zero-trust and regulatory alignment for Stream Analytics: controls that require infrastructure investment or map directly to compliance frameworks. This tier delivers diagnostic settings streaming to Log Analytics / Event Hub / Sentinel and customer-managed keys (CMK / BYOK) for cryptographic sovereignty. Together these policies protect against lateral movement, sovereign-data exfiltration, and audit gaps in regulated workloads. Maps to NIS2 Articles 21–23, ISO 27001 A.13.1.3 (network segregation) and A.18 (compliance), NIST SP 800-207 (Zero Trust).

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Stream Analytics job should connect to trusted inputs and outputs | fe8684d6-3c5b-45c0-a08b-fa92653c2e1c |  | Ensure that Stream Analytics jobs do not have arbitrary Input or Output connections that are not defined in the allow-list. This checks that Stream Analytics jobs don't exfiltrate data by connecting to arbitrary sinks outside your organization. | Deny, Disabled, Audit | Audit | Audit | Deny | Stream Analytics | Data | 1.1.0 | BuiltIn | Essential | No | No |
| 2 | Stream Analytics job should use managed identity to authenticate endpoints | ea6c4923-510a-4346-be26-1894919a5b97 |  | Ensure that Stream Analytics jobs only connect to endpoints using managed identity authentication. | Deny, Disabled, Audit | Audit | Audit | Deny | Stream Analytics | Data | 1.0.0 | BuiltIn | Essential | No | No |
| 3 | Azure Stream Analytics jobs should use customer-managed keys to encrypt data | 87ba29ef-1ab3-4d82-b763-87fcd4f531f7 |  | Use customer-managed keys when you want to securely store any metadata and private data assets of your Stream Analytics jobs in your storage account. This gives you total control over how your Stream Analytics data is encrypted. | Audit, Audit, Deny, Deny, Disabled, Disabled | Audit | Audit | Deny | Stream Analytics | Data | 1.1.0 | BuiltIn | Enterprise | No | No |
| 4 | Resource logs in Azure Stream Analytics should be enabled | f9be5368-9bf5-4b84-9e0a-7850da98bb46 |  | Audit enabling of resource logs. This enables you to recreate activity trails to use for investigation purposes; when a security incident occurs or when your network is compromised | AuditIfNotExists, Disabled | AuditIfNotExists | AuditIfNotExists | AuditIfNotExists | Stream Analytics | Data | 5.0.0 | BuiltIn | Enterprise | No | No |
