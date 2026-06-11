# Company Web Professional — App Configuration

## Tier rationale

**Professional** — Active security posture for App Configuration: controls that produce signals an operations team must act on. This tier delivers network hardening (public access disabled, VNet integration, firewall rules). Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | App Configuration should disable public network access | 3d9f5e4c-9947-4579-9539-2a7695fbc187 |  | Disabling public network access improves security by ensuring that the resource isn't exposed on the public internet. You can limit exposure of your resources by creating private endpoints instead. Learn more at: https://aka.ms/appconfig/private-endpoint. | Audit, Deny, Disabled | Audit | Audit | Deny | App Configuration | Web | 1.0.0 | BuiltIn | Professional | No | No |
| 2 | Configure App Configuration to disable public network access | 73290fa2-dfa7-4bbb-945d-a5e23b75df2c |  | Disable public network access for App Configuration so that it isn't accessible over the public internet. This configuration helps protect them against data leakage risks. You can limit exposure of the your resources by creating private endpoints instead. Learn more at: https://aka.ms/appconfig/private-endpoint. | Modify, Disabled | Modify | Modify | Modify | App Configuration | Web | 1.0.0 | BuiltIn | Professional | No | Yes |
