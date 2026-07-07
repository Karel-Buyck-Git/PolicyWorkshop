# Company Storage Essential — Data Box

## Tier rationale

**Essential** — Baseline hygiene for Data Box: the non-negotiable controls every deployment should enforce from day one. This tier delivers encryption-at-rest with service-managed keys. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Data Box jobs should enable double encryption for data at rest on the device | c349d81b-9985-44ae-a8da-ff98d108ede8 |  | Enable a second layer of software-based encryption for data at rest on the device. The device is already protected via Advanced Encryption Standard 256-bit encryption for data at rest. This option adds a second layer of data encryption. | Audit, Deny, Disabled | Audit | Audit | Deny | Data Box | Storage | 1.0.0 | BuiltIn | Essential | No | No |
