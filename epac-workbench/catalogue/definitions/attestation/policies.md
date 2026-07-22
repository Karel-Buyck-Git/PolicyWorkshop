# Attestation Policies

## Tier rationale

**Essential** — No essential-tier policies are defined for Attestation in the current built-in policy set.

**Professional** — Active security posture for Attestation: controls that produce signals an operations team must act on. This tier delivers network hardening (public access disabled, VNet integration, firewall rules). Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

**Enterprise** — No enterprise-tier policies are defined for Attestation in the current built-in policy set.

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Attestation providers should disable public network access | 5e7e928c-8693-4a23-9bf3-1c77b9a8fe97 |  | To improve the security of Azure Attestation Service, ensure that it isn't exposed to the public internet and can only be accessed from a private endpoint. Disable the public network access property as described in aka.ms/azureattestation. This option disables access from any public address space outside the Azure IP range, and denies all logins that match IP or virtual network-based firewall rules. This reduces data leakage risks. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Attestation | Security | 1.0.0 | BuiltIn | Professional |
| 2 | Azure Attestation providers should use private endpoints | 7b256a2d-058b-41f8-bed9-3f870541c40a |  | Private endpoints provide a way to connect Azure Attestation providers to your Azure resources without sending traffic over the public internet. By preventing public access, private endpoints help protect against undesired anonymous access. | No | No | AuditIfNotExists, Disabled | AuditIfNotExists | AuditIfNotExists | AuditIfNotExists | Attestation | Security | 1.0.0 | BuiltIn | Professional |
