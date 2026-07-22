# Company Integration Professional — Service Bus

## Tier rationale

**Professional** — Active security posture for Service Bus: controls that produce signals an operations team must act on. This tier delivers network hardening (public access disabled, VNet integration, firewall rules). Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Configure Service Bus namespaces with private endpoints | 7d890f7f-100c-473d-baa1-2777e2266535 |  | Private endpoints connect your virtual network to Azure services without a public IP address at the source or destination. By mapping private endpoints to Service Bus namespaces, you can reduce data leakage risks. Learn more at: https://docs.microsoft.com/azure/service-bus-messaging/private-link-service. | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | Service Bus | Integration | 1.0.0 | BuiltIn | Professional | Yes | Yes |
| 2 | Service Bus Namespaces should disable public network access | cbd11fd3-3002-4907-b6c8-579f0e700e13 |  | Azure Service Bus should have public network access disabled. Disabling public network access improves security by ensuring that the resource isn't exposed on the public internet. You can limit exposure of your resources by creating private endpoints instead. Learn more at: https://docs.microsoft.com/azure/service-bus-messaging/private-link-service | Audit, Deny, Disabled | Audit | Audit | Deny | Service Bus | Integration | 1.1.0 | BuiltIn | Professional | No | No |
