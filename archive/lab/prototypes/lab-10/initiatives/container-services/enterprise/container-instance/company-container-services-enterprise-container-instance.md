# Company Container Services Enterprise — Container Instance

## Tier rationale

**Enterprise** — Zero-trust and regulatory alignment for Container Instance: controls that require infrastructure investment or map directly to compliance frameworks. This tier delivers diagnostic settings streaming to Log Analytics / Event Hub / Sentinel and customer-managed keys (CMK / BYOK) for cryptographic sovereignty. Together these policies protect against lateral movement, sovereign-data exfiltration, and audit gaps in regulated workloads. Maps to NIS2 Articles 21–23, ISO 27001 A.13.1.3 (network segregation) and A.18 (compliance), NIST SP 800-207 (Zero Trust).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Container Instance container group should use customer-managed key for encryption | 0aa61e00-0a01-4a3c-9945-e93cffedf0e6 |  | Secure your containers with greater flexibility using customer-managed keys. When you specify a customer-managed key, that key is used to protect and control access to the key that encrypts your data. Using customer-managed keys provides additional capabilities to control rotation of the key encryption key or cryptographically erase data. | Audit, Disabled, Deny | Audit | Audit | Deny | Container Instance | Container Services | 1.0.0 | BuiltIn | Enterprise | No | No |
| 2 | Configure diagnostic settings for container groups to Log Analytics workspace | 41ebf9df-66cb-48e9-a8d0-98afb4e150ce |  | Deploys the diagnostic settings for Container Instance to stream resource logs to a Log Analytics workspace when any container instance which is missing this diagnostic settings is created or updated. | DeployIfNotExists, AuditIfNotExists, Disabled | DeployIfNotExists | AuditIfNotExists | DeployIfNotExists | Container Instance | Container Services | 1.0.0 | BuiltIn | Enterprise | Yes | Yes |
