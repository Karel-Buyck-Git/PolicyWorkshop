# Attestation Policies

## Tier rationale

**Essential** — No essential-tier policies are defined for Attestation in the current built-in policy set.

**Professional** — No professional-tier policies are defined for Attestation in the current built-in policy set.

**Enterprise** — Zero-trust and regulatory alignment for Attestation: controls that require infrastructure investment or map directly to compliance frameworks. This tier delivers private endpoints and private link removing the public attack surface. Together these policies protect against lateral movement, sovereign-data exfiltration, and audit gaps in regulated workloads. Maps to NIS2 Articles 21–23, ISO 27001 A.13.1.3 (network segregation) and A.18 (compliance), NIST SP 800-207 (Zero Trust).

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Attestation providers should disable public network access | 5e7e928c-8693-4a23-9bf3-1c77b9a8fe97 |  | To improve the security of Azure Attestation Service, ensure that it isn't exposed to the public internet and can only be accessed from a private endpoint. Disable the public network access property as described in aka.ms/azureattestation. This option disables access from any public address space outside the Azure IP range, and denies all logins that match IP or virtual network-based firewall rules. This reduces data leakage risks. | Audit, Deny, Disabled | Audit | Audit | Deny | Attestation | Security | 1.0.0 | BuiltIn | Enterprise | No | No |
| 2 | Azure Attestation providers should use private endpoints | 7b256a2d-058b-41f8-bed9-3f870541c40a |  | Private endpoints provide a way to connect Azure Attestation providers to your Azure resources without sending traffic over the public internet. By preventing public access, private endpoints help protect against undesired anonymous access. | AuditIfNotExists, Disabled | AuditIfNotExists | AuditIfNotExists | AuditIfNotExists | Attestation | Security | 1.0.0 | BuiltIn | Enterprise | No | No |
