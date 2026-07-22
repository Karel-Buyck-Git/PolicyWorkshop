# Company undefined Professional — Mission

## Tier rationale

**Professional** — Active security posture for Mission: controls that produce signals an operations team must act on. This tier delivers network hardening (public access disabled, VNet integration, firewall rules). Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure SQL Database should restrict or disable Public network access | 5cc7aeef-357e-433d-9627-05354b40f8e2 |  | This policy applies exclusively to Mission Platform products and services; usage outside of these scopes is not supported. It enforces private-endpoint-only access for Azure SQL databases to remove public ingress paths and reduce exposure risks (see https://learn.microsoft.com/azure/azure-sql/database/connectivity-architecture). | Audit, Deny, Disabled | Audit | Audit | Deny | Mission | undefined | 1.0.0 | BuiltIn | Professional | No | No |
| 2 | CosmosDB should restrict public access but allow access from certain IP addresses | 65e3adf0-0793-4cd2-af1f-134216ad5ce1 |  | This policy applies exclusively to Mission Platform products and services; usage outside of these scopes is not supported. This policy restricts Cosmos DB public network access while permitting connectivity from designated IP address ranges required for essential platform operations. | Audit, Deny, Disabled | Audit | Audit | Deny | Mission | undefined | 1.0.0 | BuiltIn | Professional | No | No |
