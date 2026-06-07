# Company Compute Enterprise — Desktop Virtualization

## Tier rationale

**Enterprise** — Zero-trust and regulatory alignment for Azure Virtual Desktop: controls that require infrastructure investment or map directly to compliance frameworks. This tier delivers private endpoints and private link removing the public attack surface. Together these policies protect against lateral movement, sovereign-data exfiltration, and audit gaps in regulated workloads. Maps to NIS2 Articles 21–23, ISO 27001 A.13.1.3 (network segregation) and A.18 (compliance), NIST SP 800-207 (Zero Trust).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Virtual Desktop service should use private link | ca950cd7-02f7-422e-8c23-91ff40f169c1 |  | Using Azure Private Link with your Azure Virtual Desktop resources can improve security and keep your data safe. Learn more about private links at: https://aka.ms/avdprivatelink. | Audit, Disabled | Audit | Audit | Audit | Desktop Virtualization | Compute | 1.0.0 | BuiltIn | Enterprise | No | No |
| 2 | Configure Azure Virtual Desktop hostpool resources to use private DNS zones | 9427df23-0f42-4e1e-bf99-a6133d841c4a |  | Use private DNS zones to override the DNS resolution for a private endpoint. A private DNS zone links to your virtual network to resolve to Azure Virtual Desktop resources. Learn more at: https://aka.ms/privatednszone. | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | Desktop Virtualization | Compute | 1.0.0 | BuiltIn | Enterprise | Yes | Yes |
| 3 | Configure Azure Virtual Desktop workspace resources to use private DNS zones | 34804460-d88b-4922-a7ca-537165e060ed |  | Use private DNS zones to override the DNS resolution for a private endpoint. A private DNS zone links to your virtual network to resolve to Azure Virtual Desktop resources. Learn more at: https://aka.ms/privatednszone. | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | Desktop Virtualization | Compute | 1.0.0 | BuiltIn | Enterprise | Yes | Yes |
