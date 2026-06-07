# Company Integration Professional — SignalR

## Tier rationale

**Professional** — Active security posture for SignalR: controls that produce signals an operations team must act on. This tier delivers network hardening (public access disabled, VNet integration, firewall rules). Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Configure private endpoints to Azure SignalR Service | ef45854f-b33f-49a3-8041-9057e915d88f |  | Private endpoints connect your virtual network to Azure services without a public IP address at the source or destination. By mapping private endpoints to Azure SignalR Service resources, you can reduce data leakage risks. Learn more at https://aka.ms/asrs/privatelink. | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | SignalR | Integration | 1.0.0 | BuiltIn | Professional | Yes | Yes |
