# Company Integration Professional — Web PubSub

## Tier rationale

**Professional** — Active security posture for Web PubSub: controls that produce signals an operations team must act on. This tier delivers network hardening (public access disabled, VNet integration, firewall rules). Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Web PubSub Service should disable public network access | bf45113f-264e-4a87-88f9-29ac8a0aca6a |  | Disabling public network access improves security by ensuring that Azure Web PubSub service isn't exposed on the public internet. Creating private endpoints can limit exposure of Azure Web PubSub service. Learn more at: https://aka.ms/awps/networkacls. | Audit, Deny, Disabled | Audit | Audit | Deny | Web PubSub | Integration | 1.0.0 | BuiltIn | Professional | No | No |
| 2 | Configure Azure Web PubSub Service to disable public network access | 5b1213e4-06e4-4ccc-81de-4201f2f7131a |  | Disable public network access for your Azure Web PubSub resource so that it's not accessible over the public internet. This can reduce data leakage risks. Learn more at: https://aka.ms/awps/networkacls. | Modify, Disabled | Modify | Modify | Modify | Web PubSub | Integration | 1.0.0 | BuiltIn | Professional | No | Yes |
