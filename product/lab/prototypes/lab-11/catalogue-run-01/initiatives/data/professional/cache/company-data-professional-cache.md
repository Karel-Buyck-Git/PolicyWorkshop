# Company Data Professional — Cache

## Tier rationale

**Professional** — Active security posture for Cache: controls that produce signals an operations team must act on. This tier delivers network hardening (public access disabled, VNet integration, firewall rules). Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Cache for Redis should disable public network access | 470baccb-7e51-4549-8b1a-3e5be069f663 |  | Disabling public network access improves security by ensuring that the Azure Cache for Redis isn't exposed on the public internet. You can limit exposure of your Azure Cache for Redis by creating private endpoints instead. Learn more at: https://docs.microsoft.com/azure/azure-cache-for-redis/cache-private-link. | Audit, Deny, Disabled | Audit | Audit | Deny | Cache | Data | 1.0.0 | BuiltIn | Professional | No | No |
| 2 | Configure Azure Cache for Redis to disable public network access | 30b3dfa5-a70d-4c8e-bed6-0083858f663d |  | Disable public network access for your Azure Cache for Redis resource so that it's not accessible over the public internet. This helps protect the cache against data leakage risks. | Modify, Disabled | Modify | Modify | Modify | Cache | Data | 1.0.0 | BuiltIn | Professional | No | Yes |
