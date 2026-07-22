# DevOpsInfrastructure Policies

## Tier rationale

**Essential** — No essential-tier policies are defined for DevOpsInfrastructure in the current built-in policy set.

**Professional** — Active security posture for DevOpsInfrastructure: controls that produce signals an operations team must act on. This tier delivers network hardening (public access disabled, VNet integration, firewall rules). Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

**Enterprise** — No enterprise-tier policies are defined for DevOpsInfrastructure in the current built-in policy set.

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Microsoft Managed DevOps Pools should be provided with valid subnet resource in order to configure with own virtual network. | 0d6d79a8-8406-4e87-814d-2dcd83b2c355 | Preview | Disallows creating Pool resources if a valid subnet resource is not provided. | Audit, Deny, Disabled | Audit | Deny | DevOpsInfrastructure | DevOps | 1.0.0-preview | BuiltIn | Professional |
