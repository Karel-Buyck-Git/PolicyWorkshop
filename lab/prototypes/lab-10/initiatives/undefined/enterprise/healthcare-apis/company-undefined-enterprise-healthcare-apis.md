# Company undefined Enterprise — Healthcare APIs

## Tier rationale

**Enterprise** — Zero-trust and regulatory alignment for Healthcare APIs: controls that require infrastructure investment or map directly to compliance frameworks. This tier delivers customer-managed keys (CMK / BYOK) for cryptographic sovereignty and direct mapping to regulatory framework controls. Together these policies protect against lateral movement, sovereign-data exfiltration, and audit gaps in regulated workloads. Maps to NIS2 Articles 21–23, ISO 27001 A.13.1.3 (network segregation) and A.18 (compliance), NIST SP 800-207 (Zero Trust).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | DICOM Service should use a customer-managed key to encrypt data at rest | 14961b63-a1eb-4378-8725-7e84ca8db0e6 |  | Use a customer-managed key to control the encryption at rest of the data stored in Azure Health Data Services DICOM Service when this is a regulatory or compliance requirement. Customer-managed keys also deliver double encryption by adding a second layer of encryption on top of the default one done with service-managed keys. | Audit, Disabled | Audit | Audit | Audit | Healthcare APIs | undefined | 1.0.0 | BuiltIn | Enterprise | No | No |
| 2 | FHIR Service should use a customer-managed key to encrypt data at rest | c42dee8c-0202-4a12-bd8e-3e171cbf64dd |  | Use a customer-managed key to control the encryption at rest of the data stored in Azure Health Data Services FHIR Service when this is a regulatory or compliance requirement. Customer-managed keys also deliver double encryption by adding a second layer of encryption on top of the default one done with service-managed keys. | Audit, Disabled | Audit | Audit | Audit | Healthcare APIs | undefined | 1.0.0 | BuiltIn | Enterprise | No | No |
