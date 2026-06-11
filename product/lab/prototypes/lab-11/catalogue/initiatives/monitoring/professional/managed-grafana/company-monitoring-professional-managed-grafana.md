# Company Monitoring Professional — Managed Grafana

## Tier rationale

**Professional** — Active security posture for Managed Grafana: controls that produce signals an operations team must act on. This tier delivers network hardening (public access disabled, VNet integration, firewall rules). Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Managed Grafana workspaces should disable public network access | e8775d5a-73b7-4977-a39b-833ef0114628 |  | Disabling public network access improves security by ensuring that your Azure Managed Grafana workspace isn't exposed on the public internet. Creating private endpoints can limit exposure of your workspaces. | Audit, Deny, Disabled | Audit | Audit | Deny | Managed Grafana | Monitoring | 1.0.0 | BuiltIn | Professional | No | No |
| 2 | Configure Azure Managed Grafana workspaces to disable public network access | 67529aa1-5285-4b1c-8e6f-5ccd861ac98e |  | Disable public network access for your Azure Managed Grafana workspace so that it's not accessible over the public internet. This can reduce data leakage risks. | Modify, Disabled | Modify | Modify | Modify | Managed Grafana | Monitoring | 1.0.0 | BuiltIn | Professional | No | Yes |
