# Company DevOps Enterprise — Azure Load Testing

## Tier rationale

**Enterprise** — Zero-trust and regulatory alignment for Azure Load Testing: controls that require infrastructure investment or map directly to compliance frameworks. This tier delivers customer-managed keys (CMK / BYOK) for cryptographic sovereignty. Together these policies protect against lateral movement, sovereign-data exfiltration, and audit gaps in regulated workloads. Maps to NIS2 Articles 21–23, ISO 27001 A.13.1.3 (network segregation) and A.18 (compliance), NIST SP 800-207 (Zero Trust).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure load testing resource should use customer-managed keys to encrypt data at rest | 65c4f833-1f2e-426c-8780-f6d7593bed7a |  | Use customer-managed keys(CMK) to manage the encryption at rest for your Azure Load Testing resource. By default the encryptio is done using Service managed keys, customer-managed keys enable the data to be encrypted with an Azure Key Vault key created and owned by you. You have full control and responsibility for the key lifecycle, including rotation and management. Learn more at https://docs.microsoft.com/azure/load-testing/how-to-configure-customer-managed-keys?tabs=portal. | Audit, Deny, Disabled | Audit | Audit | Deny | Azure Load Testing | DevOps | 1.0.0 | BuiltIn | Enterprise | No | No |
