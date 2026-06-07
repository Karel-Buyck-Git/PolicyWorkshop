# Company Azure AI Foundry Professional — Cognitive Services

## Tier rationale

**Professional** — Active security posture for Cognitive Services: controls that produce signals an operations team must act on. This tier delivers network hardening (public access disabled, VNet integration, firewall rules). Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Configure Cognitive Services accounts to disable public network access | 47ba1dd7-28d9-4b07-a8d5-9813bed64e0c |  | Disable public network access for your Cognitive Services resource so that it's not accessible over the public internet. This can reduce data leakage risks. Learn more at: https://go.microsoft.com/fwlink/?linkid=2129800. | Disabled, Modify | Modify | Modify | Modify | Cognitive Services | Azure AI Foundry | 3.0.0 | BuiltIn | Professional | No | Yes |
| 2 | Configure Cognitive Services accounts with private endpoints | db630ad5-52e9-4f4d-9c44-53912fe40053 |  | Private endpoints connect your virtual networks to Azure services without a public IP address at the source or destination. By mapping private endpoints to Cognitive Services, you'll reduce the potential for data leakage. Learn more about private links at: https://go.microsoft.com/fwlink/?linkid=2129800. | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | Cognitive Services | Azure AI Foundry | 3.0.0 | BuiltIn | Professional | Yes | Yes |
