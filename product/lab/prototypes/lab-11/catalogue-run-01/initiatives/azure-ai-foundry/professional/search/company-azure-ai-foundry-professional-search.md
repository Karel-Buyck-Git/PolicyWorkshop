# Company Azure AI Foundry Professional — Search

## Tier rationale

**Professional** — Active security posture for Search: controls that produce signals an operations team must act on. This tier delivers network hardening (public access disabled, VNet integration, firewall rules). Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure AI Search services should disable public network access | ee980b6d-0eca-4501-8d54-f6290fd512c3 |  | Disabling public network access improves security by ensuring that your Azure AI Search service is not exposed on the public internet. Creating private endpoints can limit exposure of your Search service. Learn more at: https://aka.ms/azure-cognitive-search/inbound-private-endpoints. | Audit, Deny, Disabled | Audit | Audit | Deny | Search | Azure AI Foundry | 1.0.1 | BuiltIn | Professional | No | No |
| 2 | Configure Azure AI Search services to disable public network access | 9cee519f-d9c1-4fd9-9f79-24ec3449ed30 |  | Disable public network access for your Azure AI Search service so that it is not accessible over the public internet. This can reduce data leakage risks. Learn more at: https://aka.ms/azure-cognitive-search/inbound-private-endpoints. | Modify, Disabled | Modify | Modify | Modify | Search | Azure AI Foundry | 1.0.1 | BuiltIn | Professional | No | Yes |
