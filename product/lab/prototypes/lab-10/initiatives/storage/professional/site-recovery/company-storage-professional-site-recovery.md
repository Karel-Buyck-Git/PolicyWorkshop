# Company Storage Professional — Site Recovery

## Tier rationale

**Professional** — Active security posture for Site Recovery: controls that produce signals an operations team must act on. This tier delivers network hardening (public access disabled, VNet integration, firewall rules). Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Configure private endpoints on Azure Recovery Services vaults | e95a8a5c-0987-421f-84ab-df4d88ebf7d1 | Preview | Private endpoints connect your virtual network to Azure services without a public IP address at the source or destination. By mapping private endpoints to your site recovery resources of Recovery Services vaults, you can reduce data leakage risks. To use private links, managed service identity must be assigned to Recovery Services Vaults. Learn more about private links at: https://docs.microsoft.com/azure/site-recovery/azure-to-azure-how-to-enable-replication-private-endpoints. | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | Site Recovery | Storage | 1.0.0-preview | BuiltIn | Professional | Yes | Yes |
