# Company Data Professional — Data Factory

## Tier rationale

**Professional** — Active security posture for Data Factory: controls that produce signals an operations team must act on. This tier delivers network hardening (public access disabled, VNet integration, firewall rules). Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Configure Data Factories to disable public network access | 08b1442b-7789-4130-8506-4f99a97226a7 |  | Disable public network access for your Data Factory so that it is not accessible over the public internet. This can reduce data leakage risks. Learn more at: https://docs.microsoft.com/azure/data-factory/data-factory-private-link. | Modify, Disabled | Modify | Modify | Modify | Data Factory | Data | 1.0.0 | BuiltIn | Professional | No | Yes |
| 2 | Configure private endpoints for Data factories | 496ca26b-f669-4322-a1ad-06b7b5e41882 |  | Private endpoints connect your virtual network to Azure services without a public IP address at the source or destination.  By mapping private endpoints to your Azure Data Factory, you can reduce data leakage risks.  Learn more at: https://docs.microsoft.com/azure/data-factory/data-factory-private-link. | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | Data Factory | Data | 1.1.0 | BuiltIn | Professional | Yes | Yes |
| 3 | SQL Server Integration Services integration runtimes on Azure Data Factory should be joined to a virtual network | 0088bc63-6dee-4a9c-9d29-91cfdc848952 |  | Azure Virtual Network deployment provides enhanced security and isolation for your SQL Server Integration Services integration runtimes on Azure Data Factory, as well as subnets, access control policies, and other features to further restrict access. | Audit, Deny, Disabled | Audit | Audit | Deny | Data Factory | Data | 2.3.0 | BuiltIn | Professional | No | No |
