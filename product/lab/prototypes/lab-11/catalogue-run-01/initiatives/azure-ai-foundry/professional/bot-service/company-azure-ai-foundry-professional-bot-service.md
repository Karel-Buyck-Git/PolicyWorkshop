# Company Azure AI Foundry Professional — Bot Service

## Tier rationale

**Professional** — Active security posture for Bot Service: controls that produce signals an operations team must act on. This tier delivers network hardening (public access disabled, VNet integration, firewall rules). Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Bot Service should have public network access disabled | 5e8168db-69e3-4beb-9822-57cb59202a9d |  | Bots should be set to 'isolated only' mode. This setting configures Bot Service channels that require traffic over the public internet to be disabled. | Audit, Deny, Disabled | Audit | Audit | Deny | Bot Service | Azure AI Foundry | 1.0.0 | BuiltIn | Professional | No | No |
