# Azure Purview Policies

| # | Policy | Tag | Description | Allowed Values | Default Value | MVP Value | Category | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Purview accounts should use private link |  | Azure Private Link lets you connect your virtual network to Azure services without a public IP address at the source or destination. The private link platform handles the connectivity between the consumer and services over the Azure backbone network. By mapping private endpoints to your Azure Purview accounts instead of the entire service, you'll also be protected against data leakage risks. Learn more at: https://aka.ms/purview-private-link. | Audit, Disabled | Audit | Audit | Azure Purview | 1.0.0 | BuiltIn | Enterprise |
