# Azure Load Testing Policies

## Tier rationale

**Essential** — No essential-tier policies are defined for Azure Load Testing in the current built-in policy set.

**Professional** — No professional-tier policies are defined for Azure Load Testing in the current built-in policy set.

**Enterprise** — Zero-trust and regulatory alignment for Azure Load Testing: controls that require infrastructure investment or map directly to compliance frameworks. This tier delivers private endpoints and private link removing the public attack surface and customer-managed keys (CMK / BYOK) for cryptographic sovereignty. Together these policies protect against lateral movement, sovereign-data exfiltration, and audit gaps in regulated workloads. Maps to NIS2 Articles 21–23, ISO 27001 A.13.1.3 (network segregation) and A.18 (compliance), NIST SP 800-207 (Zero Trust).

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure load testing resource should use customer-managed keys to encrypt data at rest | 65c4f833-1f2e-426c-8780-f6d7593bed7a |  | Use customer-managed keys(CMK) to manage the encryption at rest for your Azure Load Testing resource. By default the encryptio is done using Service managed keys, customer-managed keys enable the data to be encrypted with an Azure Key Vault key created and owned by you. You have full control and responsibility for the key lifecycle, including rotation and management. Learn more at https://docs.microsoft.com/azure/load-testing/how-to-configure-customer-managed-keys?tabs=portal. | Audit, Deny, Disabled | Audit | Audit | Deny | Azure Load Testing | DevOps | 1.0.0 | BuiltIn | Enterprise | No | No |
| 2 | Load tests using Azure Load Testing should be run only against private endpoints from within a virtual network. | d855fd7a-9be5-4d84-8b75-28d41aadc158 | Preview | Azure Load Testing engine instances should use virtual network injection for the following purposes: 1. Isolate Azure Load Testing engines to a virtual network. 2. Enable Azure Load Testing engines to interact with systems in either on premises data centers or Azure service in other virtual networks. 3. Empower customers to control inbound and outbound network communications for Azure Load Testing engines. | Audit, Deny, Disabled | Audit | Audit | Deny | Azure Load Testing | DevOps | 1.0.0-preview | BuiltIn | Enterprise | No | No |
