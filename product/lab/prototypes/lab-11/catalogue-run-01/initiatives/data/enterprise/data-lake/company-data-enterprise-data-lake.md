# Company Data Enterprise — Data Lake

## Tier rationale

**Enterprise** — Zero-trust and regulatory alignment for Data Lake: controls that require infrastructure investment or map directly to compliance frameworks. This tier delivers diagnostic settings streaming to Log Analytics / Event Hub / Sentinel. Together these policies protect against lateral movement, sovereign-data exfiltration, and audit gaps in regulated workloads. Maps to NIS2 Articles 21–23, ISO 27001 A.13.1.3 (network segregation) and A.18 (compliance), NIST SP 800-207 (Zero Trust).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Resource logs in Azure Data Lake Store should be enabled | 057ef27e-665e-4328-8ea3-04b3122bd9fb |  | Audit enabling of resource logs. This enables you to recreate activity trails to use for investigation purposes; when a security incident occurs or when your network is compromised | AuditIfNotExists, Disabled | AuditIfNotExists | AuditIfNotExists | AuditIfNotExists | Data Lake | Data | 5.0.0 | BuiltIn | Enterprise | No | No |
| 2 | Resource logs in Data Lake Analytics should be enabled | c95c74d9-38fe-4f0d-af86-0c7d626a315c |  | Audit enabling of resource logs. This enables you to recreate activity trails to use for investigation purposes; when a security incident occurs or when your network is compromised | AuditIfNotExists, Disabled | AuditIfNotExists | AuditIfNotExists | AuditIfNotExists | Data Lake | Data | 5.0.0 | BuiltIn | Enterprise | No | No |
