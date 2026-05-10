# App Platform Policies

| # | Policy | Tag | Description | Allowed Values | Default Value | MVP Value | Category | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Audit Azure Spring Cloud instances where distributed tracing is not enabled | Preview | Distributed tracing tools in Azure Spring Cloud allow debugging and monitoring the complex interconnections between microservices in an application. Distributed tracing tools should be enabled and in a healthy state. | Audit, Disabled | Audit | Audit | App Platform | 1.0.0-preview | BuiltIn | Enterprise |
| 2 | Azure Spring Cloud should use network injection |  | Azure Spring Cloud instances should use virtual network injection for the following purposes: 1. Isolate Azure Spring Cloud from Internet. 2. Enable Azure Spring Cloud to interact with systems in either on premises data centers or Azure service in other virtual networks. 3. Empower customers to control inbound and outbound network communications for Azure Spring Cloud. | Audit, Disabled, Deny | Audit | Deny | App Platform | 1.2.0 | BuiltIn | Professional |
