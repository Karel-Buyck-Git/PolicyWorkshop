# Company Data Essential — Data Lake

## Tier rationale

**Essential** — Baseline hygiene for Data Lake: the non-negotiable controls every deployment should enforce from day one. This tier delivers encryption-at-rest with service-managed keys. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Require encryption on Data Lake Store accounts | a7ff3161-0087-490a-9ad9-ad6217f4f43a |  | This policy ensures encryption is enabled on all Data Lake Store accounts | Deny | Deny | Deny | Deny | Data Lake | Data | 1.0.0 | BuiltIn | Essential | No | No |
