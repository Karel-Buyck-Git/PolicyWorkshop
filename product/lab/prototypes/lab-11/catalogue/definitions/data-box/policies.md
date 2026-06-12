# Data Box Policies

## Tier rationale

**Essential** — Baseline hygiene for Data Box: the non-negotiable controls every deployment should enforce from day one. This tier delivers encryption-at-rest with service-managed keys. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

**Professional** — No professional-tier policies are defined for Data Box in the current built-in policy set.

**Enterprise** — Zero-trust and regulatory alignment for Data Box: controls that require infrastructure investment or map directly to compliance frameworks. This tier delivers customer-managed keys (CMK / BYOK) for cryptographic sovereignty. Together these policies protect against lateral movement, sovereign-data exfiltration, and audit gaps in regulated workloads. Maps to NIS2 Articles 21–23, ISO 27001 A.13.1.3 (network segregation) and A.18 (compliance), NIST SP 800-207 (Zero Trust).

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Data Box jobs should enable double encryption for data at rest on the device | c349d81b-9985-44ae-a8da-ff98d108ede8 |  | Enable a second layer of software-based encryption for data at rest on the device. The device is already protected via Advanced Encryption Standard 256-bit encryption for data at rest. This option adds a second layer of data encryption. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Data Box | Storage | 1.0.0 | BuiltIn | Essential |
| 2 | Azure Data Box jobs should use a customer-managed key to encrypt the device unlock password | 86efb160-8de7-451d-bc08-5d475b0aadae |  | Use a customer-managed key to control the encryption of the device unlock password for Azure Data Box. Customer-managed keys also help manage access to the device unlock password by the Data Box service in order to prepare the device and copy data in an automated manner. The data on the device itself is already encrypted at rest with Advanced Encryption Standard 256-bit encryption, and the device unlock password is encrypted by default with a Microsoft managed key. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Data Box | Storage | 1.0.0 | BuiltIn | Enterprise |
