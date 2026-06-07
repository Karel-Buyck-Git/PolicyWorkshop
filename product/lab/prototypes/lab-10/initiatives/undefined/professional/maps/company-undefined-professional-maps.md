# Company undefined Professional — Maps

## Tier rationale

**Professional** — Active security posture for Maps: controls that produce signals an operations team must act on. This tier delivers network hardening (public access disabled, VNet integration, firewall rules). Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Configure Azure Maps Accounts to disable public network access | bf9b1f7c-41ee-4de9-8eab-e3eb43aeea40 |  | Disable public network access for your Maps Account so that it's not accessible over the public internet. This can reduce data leakage risks. Learn more at: https://aka.ms/azmprivatelink | Modify, Disabled | Modify | Modify | Modify | Maps | undefined | 1.0.0 | BuiltIn | Professional | No | Yes |
| 2 | CORS should not allow every resource to access your map account. | 50553764-7777-43cf-bf12-8647e0b9ba01 |  | Cross-Origin Resource Sharing (CORS) should not allow all domains to access your map account. Allow only required domains to interact with your map account. | Disabled, Audit, Deny | Audit | Audit | Deny | Maps | undefined | 1.0.0 | BuiltIn | Professional | No | No |
