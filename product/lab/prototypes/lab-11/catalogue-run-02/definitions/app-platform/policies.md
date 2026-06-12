# App Platform Policies

## Tier rationale

**Essential** — No essential-tier policies are defined for App Platform in the current built-in policy set.

**Professional** — Active security posture for App Platform: controls that produce signals an operations team must act on. This tier delivers network hardening (public access disabled, VNet integration, firewall rules) and audit-log and monitoring controls that produce signals for ops teams. Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

**Enterprise** — No enterprise-tier policies are defined for App Platform in the current built-in policy set.

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Audit Azure Spring Cloud instances where distributed tracing is not enabled | 0f2d8593-4667-4932-acca-6a9f187af109 | Preview | Distributed tracing tools in Azure Spring Cloud allow debugging and monitoring the complex interconnections between microservices in an application. Distributed tracing tools should be enabled and in a healthy state. | Audit, Disabled | Audit | Audit | Audit | App Platform | Web | 1.0.0-preview | BuiltIn | Professional | No | No |
| 2 | Azure Spring Cloud should use network injection | af35e2a4-ef96-44e7-a9ae-853dd97032c4 |  | Azure Spring Cloud instances should use virtual network injection for the following purposes: 1. Isolate Azure Spring Cloud from Internet. 2. Enable Azure Spring Cloud to interact with systems in either on premises data centers or Azure service in other virtual networks. 3. Empower customers to control inbound and outbound network communications for Azure Spring Cloud. | Audit, Disabled, Deny | Audit | Audit | Deny | App Platform | Web | 1.2.0 | BuiltIn | Professional | No | No |
