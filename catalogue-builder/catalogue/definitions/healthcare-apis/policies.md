# Healthcare APIs Policies

## Tier rationale

**Essential** — No essential-tier policies are defined for Healthcare APIs in the current built-in policy set.

**Professional** — Active security posture for Healthcare APIs: controls that produce signals an operations team must act on. This tier protects against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse for Healthcare APIs workloads. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

**Enterprise** — Zero-trust and regulatory alignment for Healthcare APIs: controls that require infrastructure investment or map directly to compliance frameworks. This tier delivers customer-managed keys (CMK / BYOK) for cryptographic sovereignty and direct mapping to regulatory framework controls. Together these policies protect against lateral movement, sovereign-data exfiltration, and audit gaps in regulated workloads. Maps to NIS2 Articles 21–23, ISO 27001 A.13.1.3 (network segregation) and A.18 (compliance), NIST SP 800-207 (Zero Trust).

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | CORS should not allow every domain to access your FHIR Service | fe1c9040-c46a-4e81-9aea-c7850fbb3aa6 |  | Cross-Origin Resource Sharing (CORS) should not allow all domains to access your FHIR Service. To protect your FHIR Service, remove access for all domains and explicitly define the domains allowed to connect. | No | No | Audit, Audit, Disabled, Disabled | Audit | Audit | Audit | Healthcare APIs | Undefined | 1.1.0 | BuiltIn | Professional |
| 2 | DICOM Service should use a customer-managed key to encrypt data at rest | 14961b63-a1eb-4378-8725-7e84ca8db0e6 |  | Use a customer-managed key to control the encryption at rest of the data stored in Azure Health Data Services DICOM Service when this is a regulatory or compliance requirement. Customer-managed keys also deliver double encryption by adding a second layer of encryption on top of the default one done with service-managed keys. | No | No | Audit, Disabled | Audit | Audit | Audit | Healthcare APIs | Undefined | 1.0.0 | BuiltIn | Enterprise |
| 3 | FHIR Service should use a customer-managed key to encrypt data at rest | c42dee8c-0202-4a12-bd8e-3e171cbf64dd |  | Use a customer-managed key to control the encryption at rest of the data stored in Azure Health Data Services FHIR Service when this is a regulatory or compliance requirement. Customer-managed keys also deliver double encryption by adding a second layer of encryption on top of the default one done with service-managed keys. | No | No | Audit, Disabled | Audit | Audit | Audit | Healthcare APIs | Undefined | 1.0.0 | BuiltIn | Enterprise |
