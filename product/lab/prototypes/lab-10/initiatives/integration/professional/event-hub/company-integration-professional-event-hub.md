# Company Integration Professional — Event Hub

## Tier rationale

**Professional** — Active security posture for Event Hubs: controls that produce signals an operations team must act on. This tier delivers network hardening (public access disabled, VNet integration, firewall rules). Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Configure Event Hub namespaces with private endpoints | 91678b7c-d721-4fc5-b179-3cdf74e96b1c |  | Private endpoints connect your virtual network to Azure services without a public IP address at the source or destination. By mapping private endpoints to Event Hub namespaces, you can reduce data leakage risks. Learn more at: https://docs.microsoft.com/azure/event-hubs/private-link-service. | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | Event Hub | Integration | 1.0.0 | BuiltIn | Professional | Yes | Yes |
| 2 | Event Hub Namespaces should disable public network access | 0602787f-9896-402a-a6e1-39ee63ee435e |  | Azure Event Hub should have public network access disabled. Disabling public network access improves security by ensuring that the resource isn't exposed on the public internet. You can limit exposure of your resources by creating private endpoints instead. Learn more at: https://docs.microsoft.com/azure/event-hubs/private-link-service | Audit, Deny, Disabled | Audit | Audit | Deny | Event Hub | Integration | 1.0.0 | BuiltIn | Professional | No | No |
