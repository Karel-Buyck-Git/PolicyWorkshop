# Site Recovery Policies

## Tier rationale

**Essential** — No essential-tier policies are defined for Site Recovery in the current built-in policy set.

**Professional** — Active security posture for Site Recovery: controls that produce signals an operations team must act on. This tier delivers network hardening (public access disabled, VNet integration, firewall rules). Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

**Enterprise** — No enterprise-tier policies are defined for Site Recovery in the current built-in policy set.

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Configure Azure Recovery Services vaults to use private DNS zones | 942bd215-1a66-44be-af65-6a1c0318dbe2 | Preview | Use private DNS zones to override the DNS resolution for a private endpoint. A private DNS zone links to your virtual network to resolve to Recovery Services Vaults. Learn more at: https://aka.ms/privatednszone. | Yes | Yes | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | Site Recovery | Storage | 1.0.0-preview | BuiltIn | Professional |
| 2 | Configure private endpoints on Azure Recovery Services vaults | e95a8a5c-0987-421f-84ab-df4d88ebf7d1 | Preview | Private endpoints connect your virtual network to Azure services without a public IP address at the source or destination. By mapping private endpoints to your site recovery resources of Recovery Services vaults, you can reduce data leakage risks. To use private links, managed service identity must be assigned to Recovery Services Vaults. Learn more about private links at: https://docs.microsoft.com/azure/site-recovery/azure-to-azure-how-to-enable-replication-private-endpoints. | Yes | Yes | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | Site Recovery | Storage | 1.0.0-preview | BuiltIn | Professional |
| 3 | Recovery Services vaults should use private link | 11e3da8c-1d68-4392-badd-0ff3c43ab5b0 | Preview | Azure Private Link lets you connect your virtual network to Azure services without a public IP address at the source or destination. The Private Link platform handles the connectivity between the consumer and services over the Azure backbone network. By mapping private endpoints to Azure Recovery Services vaults, data leakage risks are reduced. Learn more about private links for Azure Site Recovery at: https://aka.ms/HybridScenarios-PrivateLink and https://aka.ms/AzureToAzure-PrivateLink. | No | No | Audit, Disabled | Audit | Audit | Audit | Site Recovery | Storage | 1.0.0-preview | BuiltIn | Professional |
