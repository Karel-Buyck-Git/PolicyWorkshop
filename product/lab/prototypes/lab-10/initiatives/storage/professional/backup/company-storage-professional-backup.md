# Company Storage Professional — Backup

## Tier rationale

**Professional** — Active security posture for Backup: controls that produce signals an operations team must act on. This tier delivers network hardening (public access disabled, VNet integration, firewall rules). Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Recovery Services vaults should disable public network access | 9ebbbba3-4d65-4da9-bb67-b22cfaaff090 | Preview | Disabling public network access improves security by ensuring that recovery services vault is not exposed on the public internet. Creating private endpoints can limit exposure of recovery services vault. Learn more at: https://aka.ms/AB-PublicNetworkAccess-Deny. | Audit, Deny, Disabled | Audit | Audit | Deny | Backup | Storage | 1.0.0-preview | BuiltIn | Professional | No | No |
| 2 | Configure Azure Recovery Services vaults to disable public network access | 04726aae-4e8d-427c-af7d-ecf56d490022 | Preview | Disable public network access for your Recovery services vault so that it's not accessible over the public internet. This can reduce data leakage risks. Learn more at: https://aka.ms/AB-PublicNetworkAccess-Deny. | Modify, Disabled | Modify | Modify | Modify | Backup | Storage | 1.0.0-preview | BuiltIn | Professional | No | Yes |
