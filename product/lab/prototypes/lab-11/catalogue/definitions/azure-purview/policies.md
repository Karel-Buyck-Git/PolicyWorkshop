# Azure Purview Policies

## Tier rationale

**Essential** — No essential-tier policies are defined for Microsoft Purview in the current built-in policy set.

**Professional** — No professional-tier policies are defined for Microsoft Purview in the current built-in policy set.

**Enterprise** — Zero-trust and regulatory alignment for Microsoft Purview: controls that require infrastructure investment or map directly to compliance frameworks. This tier delivers private endpoints and private link removing the public attack surface. Together these policies protect against lateral movement, sovereign-data exfiltration, and audit gaps in regulated workloads. Maps to NIS2 Articles 21–23, ISO 27001 A.13.1.3 (network segregation) and A.18 (compliance), NIST SP 800-207 (Zero Trust).

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Purview accounts should use private link | 9259053b-ddb8-40ab-842a-0aef19d0ade4 |  | Azure Private Link lets you connect your virtual network to Azure services without a public IP address at the source or destination. The private link platform handles the connectivity between the consumer and services over the Azure backbone network. By mapping private endpoints to your Azure Purview accounts instead of the entire service, you'll also be protected against data leakage risks. Learn more at: https://aka.ms/purview-private-link. | Audit, Disabled | Audit | Audit | Audit | Azure Purview | Data | 1.0.0 | BuiltIn | Enterprise | No | No |
