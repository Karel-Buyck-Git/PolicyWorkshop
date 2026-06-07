# Company DevOps Professional — Azure Load Testing

## Tier rationale

**Professional** — Active security posture for Azure Load Testing: controls that produce signals an operations team must act on. This tier delivers network hardening (public access disabled, VNet integration, firewall rules). Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Load tests using Azure Load Testing should be run only against private endpoints from within a virtual network. | d855fd7a-9be5-4d84-8b75-28d41aadc158 | Preview | Azure Load Testing engine instances should use virtual network injection for the following purposes: 1. Isolate Azure Load Testing engines to a virtual network. 2. Enable Azure Load Testing engines to interact with systems in either on premises data centers or Azure service in other virtual networks. 3. Empower customers to control inbound and outbound network communications for Azure Load Testing engines. | Audit, Deny, Disabled | Audit | Audit | Deny | Azure Load Testing | DevOps | 1.0.0-preview | BuiltIn | Professional | No | No |
