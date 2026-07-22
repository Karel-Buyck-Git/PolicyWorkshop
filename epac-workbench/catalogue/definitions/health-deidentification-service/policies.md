# Health Deidentification Service Policies

## Tier rationale

**Essential** — No essential-tier policies are defined for Health Deidentification Service in the current built-in policy set.

**Professional** — Active security posture for Health Deidentification Service: controls that produce signals an operations team must act on. This tier delivers network hardening (public access disabled, VNet integration, firewall rules). Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

**Enterprise** — No enterprise-tier policies are defined for Health Deidentification Service in the current built-in policy set.

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Health Data Services de-identification service should disable public network access | c5f34731-7ab9-42ff-922d-ef4920068b74 |  | Disabling public network access improves security by ensuring that the resource isn't exposed on the public internet. You can limit exposure of your resources by creating private endpoints instead. | No | No | Audit, Disabled | Audit | Audit | Audit | Health Deidentification Service | Data | 1.0.0 | BuiltIn | Professional |
| 2 | Azure Health Data Services de-identification service should use private link | d9b2d63d-a233-4123-847a-7f7e5f5d7e7a |  | Azure Health Data Services de-identification service should have at least one approved private endpoint connection. Clients in a virtual network can securely access resources that have private endpoint connections through private links. | No | No | Audit, Disabled | Audit | Audit | Audit | Health Deidentification Service | Data | 1.0.0 | BuiltIn | Professional |
