# Health Data Services workspace Policies

## Tier rationale

**Essential** — No essential-tier policies are defined for Health Data Services workspace in the current built-in policy set.

**Professional** — Active security posture for Health Data Services workspace: controls that produce signals an operations team must act on. This tier delivers network hardening (public access disabled, VNet integration, firewall rules). Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

**Enterprise** — No enterprise-tier policies are defined for Health Data Services workspace in the current built-in policy set.

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Health Data Services workspace should use private link | 64528841-2f92-43f6-a137-d52e5c3dbeac |  | Health Data Services workspace should have at least one approved private endpoint connection. Clients in a virtual network can securely access resources that have private endpoint connections through private links. For more information, visit: https://aka.ms/healthcareapisprivatelink. | No | No | Audit, Disabled | Audit | Audit | Audit | Health Data Services workspace | Data | 1.0.0 | BuiltIn | Professional |
