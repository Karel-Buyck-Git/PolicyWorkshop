# VM Image Builder Policies

## Tier rationale

**Essential** — No essential-tier policies are defined for VM Image Builder in the current built-in policy set.

**Professional** — Active security posture for VM Image Builder: controls that produce signals an operations team must act on. This tier delivers network hardening (public access disabled, VNet integration, firewall rules). Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

**Enterprise** — No enterprise-tier policies are defined for VM Image Builder in the current built-in policy set.

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | VM Image Builder templates should use private link | 2154edb9-244f-4741-9970-660785bccdaa |  | Azure Private Link lets you connect your virtual network to Azure services without a public IP address at the source or destination. The Private Link platform handles the connectivity between the consumer and services over the Azure backbone network. By mapping private endpoints to your VM Image Builder building resources, data leakage risks are reduced. Learn more about private links at: https://docs.microsoft.com/azure/virtual-machines/linux/image-builder-networking#deploy-using-an-existing-vnet. | No | No | Audit, Disabled, Deny | Audit | Audit | Deny | VM Image Builder | Compute | 1.1.0 | BuiltIn | Professional |
