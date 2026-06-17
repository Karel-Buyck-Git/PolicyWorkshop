# Company Container Services Professional — Container Instance

## Tier rationale

**Professional** — Active security posture for Container Instance: controls that produce signals an operations team must act on. This tier delivers network hardening (public access disabled, VNet integration, firewall rules). Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Container Instance container group should deploy into a virtual network | 8af8f826-edcb-4178-b35f-851ea6fea615 |  | Secure communication between your containers with Azure Virtual Networks. When you specify a virtual network, resources within the virtual network can securely and privately communicate with each other. | Audit, Disabled, Deny | Audit | Audit | Deny | Container Instance | Container Services | 2.0.0 | BuiltIn | Professional | No | No |
