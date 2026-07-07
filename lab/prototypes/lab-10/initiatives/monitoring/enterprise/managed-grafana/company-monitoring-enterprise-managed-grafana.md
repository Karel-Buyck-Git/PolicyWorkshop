# Company Monitoring Enterprise — Managed Grafana

## Tier rationale

**Enterprise** — Zero-trust and regulatory alignment for Managed Grafana: controls that require infrastructure investment or map directly to compliance frameworks. This tier delivers private endpoints and private link removing the public attack surface. Together these policies protect against lateral movement, sovereign-data exfiltration, and audit gaps in regulated workloads. Maps to NIS2 Articles 21–23, ISO 27001 A.13.1.3 (network segregation) and A.18 (compliance), NIST SP 800-207 (Zero Trust).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Managed Grafana workspaces should use private link | 3a97e513-f75e-4230-8137-1efad4eadbbc |  | Azure Private Link lets you connect your virtual networks to Azure services without a public IP address at the source or destination. The Private Link platform handles the connectivity between the consumer and services over the Azure backbone network. By mapping private endpoints to Managed Grafana, you can reduce data leakage risks. | Audit, Disabled | Audit | Audit | Audit | Managed Grafana | Monitoring | 1.0.1 | BuiltIn | Enterprise | No | No |
| 2 | Configure Azure Managed Grafana workspaces to use private DNS zones | 4c8537f8-cd1b-49ec-b704-18e82a42fd58 |  | Use private DNS zones to override the DNS resolution for a private endpoint. A private DNS zone links to your virtual network to resolve to Azure Managed Grafana workspaces. | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | Managed Grafana | Monitoring | 1.0.0 | BuiltIn | Enterprise | Yes | Yes |
