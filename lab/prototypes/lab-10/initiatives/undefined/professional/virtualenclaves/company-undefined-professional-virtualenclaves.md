# Company undefined Professional — VirtualEnclaves

## Tier rationale

**Professional** — Active security posture for VirtualEnclaves: controls that produce signals an operations team must act on. This tier delivers network hardening (public access disabled, VNet integration, firewall rules). Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Network interfaces should be connected to an approved subnet of the approved virtual network | f3a7bbfd-a810-47a6-b5ba-8e17d8cffb96 |  | This policy blocks network interfaces from connecting to a virtual network or subnet that is not approved. https://aka.ms/VirtualEnclaves | Audit, Deny, Disabled | Deny | Audit | Deny | VirtualEnclaves | undefined | 1.0.0 | BuiltIn | Professional | Yes | No |
