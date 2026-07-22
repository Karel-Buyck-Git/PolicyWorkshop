# Company Container Services Professional — Container Apps

## Tier rationale

**Professional** — Active security posture for Container Apps: controls that produce signals an operations team must act on. This tier delivers network hardening (public access disabled, VNet integration, firewall rules). Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Container App environments should use network injection | 8b346db6-85af-419b-8557-92cee2c0f9bb |  | Container Apps environments should use virtual network injection to: 1.Isolate Container Apps from the public internet 2.Enable network integration with resources on-premises or in other Azure virtual networks 3.Achieve more granular control over network traffic flowing to and from the environment. | Audit, Disabled, Deny | Audit | Audit | Deny | Container Apps | Container Services | 1.0.2 | BuiltIn | Professional | No | No |
| 2 | Container Apps environment should disable public network access | d074ddf8-01a5-4b5e-a2b8-964aed452c0a |  | Disable public network access to improve security by exposing the Container Apps environment through an internal load balancer. This removes the need for a public IP address and prevents internet access to all Container Apps within the environment. | Audit, Deny, Disabled | Audit | Audit | Deny | Container Apps | Container Services | 1.1.0 | BuiltIn | Professional | No | No |
