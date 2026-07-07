# Company Networking Enterprise — Network

## Tier rationale

**Enterprise** — Zero-trust and regulatory alignment for Network: controls that require infrastructure investment or map directly to compliance frameworks. This tier delivers diagnostic settings streaming to Log Analytics / Event Hub / Sentinel and zone-redundant deployments backing the 99.99% SLA. Together these policies protect against lateral movement, sovereign-data exfiltration, and audit gaps in regulated workloads. Maps to NIS2 Articles 21–23, ISO 27001 A.13.1.3 (network segregation) and A.18 (compliance), NIST SP 800-207 (Zero Trust).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Firewall should be deployed to span multiple Availability Zones | 3e1f521a-d037-4709-bdd6-1f532f271a75 |  | For increased availability we recommend deploying your Azure Firewall to span multiple Availability Zones. This ensures that your Azure Firewall will remain available in the event of a zone failure. | Audit, Deny, Disabled | Audit | Audit | Deny | Network | Networking | 1.0.0 | BuiltIn | Enterprise | No | No |
| 2 | Configure diagnostic settings for Azure Network Security Groups to Log Analytics workspace | 98a2e215-5382-489e-bd29-32e7190a39ba |  | Deploy diagnostic settings to Azure Network Security Groups to stream resource logs to a Log Analytics workspace. | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | Network | Networking | 1.0.0 | BuiltIn | Enterprise | Yes | Yes |
| 3 | Create central Log Analytics Workspace for VNet Flowlog Traffic Analytics in the specified Resource Group | 69f5d115-d282-4c1b-9c76-7f6640427d2e |  | Create a central Log Analytics Workspace in the assigned Scope and under Resource Group nwtarg-<subscriptionID> by default for VNet flowlogs. | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | Network | Networking | 1.0.0 | BuiltIn | Enterprise | No | Yes |
| 4 | Deploy VNet Flow Logs with Traffic Analytics for VNets with regional Storage and centralized Log Analytics | 6d7c9ba4-b4b9-4d38-9e86-f1bc6b322bde |  | Deploy VNet Flow Logs with Traffic Analytics for VNets with regional Storage and centralized Log Analytics. Before remediation ensure that the resourceGroupName Resource Group, Storage Account, Log Analytics Workspace, Network Watcher are all deployed already. | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | Network | Networking | 1.0.0 | BuiltIn | Enterprise | Yes | Yes |
