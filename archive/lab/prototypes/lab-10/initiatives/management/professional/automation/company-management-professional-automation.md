# Company Management Professional — Automation

## Tier rationale

**Professional** — Active security posture for Automation: controls that produce signals an operations team must act on. This tier delivers network hardening (public access disabled, VNet integration, firewall rules). Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Automation accounts should disable public network access | 955a914f-bf86-4f0e-acd5-e0766b0efcb6 |  | Disabling public network access improves security by ensuring that the resource isn't exposed on the public internet. You can limit exposure of your Automation account resources by creating private endpoints instead. Learn more at: https://docs.microsoft.com/azure/automation/how-to/private-link-security. | Audit, Deny, Disabled | Audit | Audit | Deny | Automation | Management | 1.0.0 | BuiltIn | Professional | No | No |
| 2 | Configure Azure Automation accounts to disable public network access | 23b36a7c-9d26-4288-a8fd-c1d2fa284d8c |  | Disable public network access for Azure Automation account so that it isn't accessible over the public internet. This configuration helps protect them against data leakage risks. You can limit exposure of the your Automation account resources by creating private endpoints instead. Learn more at: https://aka.ms/privateendpoints. | Modify, Disabled | Modify | Modify | Modify | Automation | Management | 1.0.0 | BuiltIn | Professional | No | Yes |
