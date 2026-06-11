# Company Azure AI Foundry Enterprise — Azure Ai Services

## Tier rationale

**Enterprise** — Zero-trust and regulatory alignment for Azure AI Services: controls that require infrastructure investment or map directly to compliance frameworks. This tier delivers private endpoints and private link removing the public attack surface. Together these policies protect against lateral movement, sovereign-data exfiltration, and audit gaps in regulated workloads. Maps to NIS2 Articles 21–23, ISO 27001 A.13.1.3 (network segregation) and A.18 (compliance), NIST SP 800-207 (Zero Trust).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure AI Services resources should use Azure Private Link | d6759c02-b87f-42b7-892e-71b3f471d782 |  | Azure Private Link lets you connect your virtual network to Azure services without a public IP address at the source or destination. The Private Link platform reduces data leakage risks by handling the connectivity between the consumer and services over the Azure backbone network. Learn more about private links at: https://aka.ms/AzurePrivateLink/Overview | Audit, Disabled | Audit | Audit | Audit | Azure Ai Services | Azure AI Foundry | 1.0.0 | BuiltIn | Enterprise | No | No |
