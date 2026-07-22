# Azure Purview Policies

## Tier rationale

**Essential** — No essential-tier policies are defined for Microsoft Purview in the current built-in policy set.

**Professional** — Active security posture for Microsoft Purview: controls that produce signals an operations team must act on. This tier delivers network hardening (public access disabled, VNet integration, firewall rules). Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

**Enterprise** — No enterprise-tier policies are defined for Microsoft Purview in the current built-in policy set.

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Purview accounts should use private link | 9259053b-ddb8-40ab-842a-0aef19d0ade4 |  | Azure Private Link lets you connect your virtual network to Azure services without a public IP address at the source or destination. The private link platform handles the connectivity between the consumer and services over the Azure backbone network. By mapping private endpoints to your Azure Purview accounts instead of the entire service, you'll also be protected against data leakage risks. Learn more at: https://aka.ms/purview-private-link. | No | No | Audit, Disabled | Audit | Audit | Audit | Azure Purview | Data | 1.0.0 | BuiltIn | Professional |
