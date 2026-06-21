# Fluid Relay Policies

## Tier rationale

**Essential** — No essential-tier policies are defined for Fluid Relay in the current built-in policy set.

**Professional** — No professional-tier policies are defined for Fluid Relay in the current built-in policy set.

**Enterprise** — Zero-trust and regulatory alignment for Fluid Relay: controls that require infrastructure investment or map directly to compliance frameworks. This tier delivers customer-managed keys (CMK / BYOK) for cryptographic sovereignty and direct mapping to regulatory framework controls. Together these policies protect against lateral movement, sovereign-data exfiltration, and audit gaps in regulated workloads. Maps to NIS2 Articles 21–23, ISO 27001 A.13.1.3 (network segregation) and A.18 (compliance), NIST SP 800-207 (Zero Trust).

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Fluid Relay should use customer-managed keys to encrypt data at rest | 46388f67-373c-4018-98d3-2b83172dd13a |  | Use customer-managed keys to manage the encryption at rest of your Fluid Relay server. By default, customer data is encrypted with service-managed keys, but CMKs are commonly required to meet regulatory compliance standards. Customer-managed keys enable the data to be encrypted with an Azure Key Vault key created and owned by you, with full control and responsibility, including rotation and management. Learn more at https://docs.microsoft.com/azure/azure-fluid-relay/concepts/customer-managed-keys. | No | No | Audit, Disabled | Audit | Audit | Audit | Fluid Relay | Integration | 1.0.0 | BuiltIn | Enterprise |
