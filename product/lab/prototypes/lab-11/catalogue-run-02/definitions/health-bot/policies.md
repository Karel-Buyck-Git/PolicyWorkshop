# Health Bot Policies

## Tier rationale

**Essential** — No essential-tier policies are defined for Health Bot in the current built-in policy set.

**Professional** — No professional-tier policies are defined for Health Bot in the current built-in policy set.

**Enterprise** — Zero-trust and regulatory alignment for Health Bot: controls that require infrastructure investment or map directly to compliance frameworks. This tier delivers customer-managed keys (CMK / BYOK) for cryptographic sovereignty and direct mapping to regulatory framework controls. Together these policies protect against lateral movement, sovereign-data exfiltration, and audit gaps in regulated workloads. Maps to NIS2 Articles 21–23, ISO 27001 A.13.1.3 (network segregation) and A.18 (compliance), NIST SP 800-207 (Zero Trust).

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Health Bots should use Azure RBAC as their access control method | 96561daf-13ae-4008-9300-638df7e6a11a |  | Have a more precise and robust control over access control for your healthcare agents, by setting Azure RBAC as your access control method. Roles are assigned through the Access Control blade in your resource page, groups can be leveraged to share permissions, and custom roles can be authored to cater for specific use cases. Learn more at https://docs.microsoft.com/azure/health-bot/cmk | Audit, Disabled | Audit | Audit | Audit | Health Bot | Azure AI Foundry | 1.0.0 | BuiltIn | Enterprise | No | No |
| 2 | Azure Health Bots should use customer-managed keys to encrypt data at rest | 4d080fa5-a6d2-4f98-ba9c-f482d0d335c0 |  | Use customer-managed keys (CMK) to manage the encryption at rest of the data of your healthbots. By default, the data is encrypted at rest with service-managed keys, but CMK are commonly required to meet regulatory compliance standards. CMK enable the data to be encrypted with an Azure Key Vault key created and owned by you. You have full control and responsibility for the key lifecycle, including rotation and management. Learn more at https://docs.microsoft.com/azure/health-bot/cmk | Audit, Disabled | Audit | Audit | Audit | Health Bot | Azure AI Foundry | 1.0.0 | BuiltIn | Enterprise | No | No |
