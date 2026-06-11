# Company Compute Professional — Compute

## Tier rationale

**Professional** — Active security posture for Compute: controls that produce signals an operations team must act on. This tier delivers network hardening (public access disabled, VNet integration, firewall rules). Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Configure managed disks to disable public network access | 8426280e-b5be-43d9-979e-653d12a08638 |  | Disable public network access for your managed disk resource so that it's not accessible over the public internet. This can reduce data leakage risks. Learn more at: https://aka.ms/disksprivatelinksdoc. | Modify, Disabled | Modify | Modify | Modify | Compute | Compute | 2.0.0 | BuiltIn | Professional | Yes | Yes |
| 2 | Managed disks should disable public network access | 8405fdab-1faf-48aa-b702-999c9c172094 |  | Disabling public network access improves security by ensuring that a managed disk isn't exposed on the public internet. Creating private endpoints can limit exposure of managed disks. Learn more at: https://aka.ms/disksprivatelinksdoc. | Audit, Deny, Disabled | Audit | Audit | Deny | Compute | Compute | 2.1.0 | BuiltIn | Professional | No | No |
