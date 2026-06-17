# ElasticSan Policies

## Tier rationale

**Essential** — No essential-tier policies are defined for ElasticSan in the current built-in policy set.

**Professional** — Active security posture for ElasticSan: controls that produce signals an operations team must act on. This tier delivers network hardening (public access disabled, VNet integration, firewall rules). Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

**Enterprise** — Zero-trust and regulatory alignment for ElasticSan: controls that require infrastructure investment or map directly to compliance frameworks. This tier delivers customer-managed keys (CMK / BYOK) for cryptographic sovereignty and direct mapping to regulatory framework controls. Together these policies protect against lateral movement, sovereign-data exfiltration, and audit gaps in regulated workloads. Maps to NIS2 Articles 21–23, ISO 27001 A.13.1.3 (network segregation) and A.18 (compliance), NIST SP 800-207 (Zero Trust).

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | ElasticSan should disable public network access | 6a92fe1f-0b86-44ae-843d-2db3d2b571ae |  | Disable public network access for your ElasticSan so that it's not accessible over the public internet. This can reduce data leakage risks. | Audit, Deny, Disabled | Audit | Audit | Deny | ElasticSan | Storage | 1.0.0 | BuiltIn | Professional | No | No |
| 2 | ElasticSan Volume Group should use private endpoints | 1abc5157-29f8-4dbd-b28e-ff99526cb8b7 |  | Private endpoints lets administrator connect virtual networks to Azure services without a public IP address at the source or destination. By mapping private endpoints to volume group, administrator can reduce data leakage risks | Audit, Disabled | Audit | Audit | Audit | ElasticSan | Storage | 1.0.0 | BuiltIn | Professional | No | No |
| 3 | ElasticSan Volume Group should use customer-managed keys to encrypt data at rest | 7698f4ed-80ce-4e13-b408-ee135fa400a5 |  | Use customer-managed keys to manage the encryption at rest of your VolumeGroup. By default, customer data is encrypted with platform-managed keys, but CMKs are commonly required to meet regulatory compliance standards. Customer-managed keys enable the data to be encrypted with an Azure Key Vault key created and owned by you, with full control and responsibility, including rotation and management. | Audit, Disabled | Audit | Audit | Audit | ElasticSan | Storage | 1.0.0 | BuiltIn | Enterprise | No | No |
