# Company undefined Essential — Azure Edge Hardware Center

## Tier rationale

**Essential** — Baseline hygiene for Azure Edge Hardware Center: the non-negotiable controls every deployment should enforce from day one. This tier delivers encryption-at-rest with service-managed keys. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Edge Hardware Center devices should have double encryption support enabled | 08a6b96f-576e-47a2-8511-119a212d344d |  | Ensure that devices ordered from Azure Edge Hardware Center have double encryption support enabled, to secure the data at rest on the device. This option adds a second layer of data encryption. | Audit, Deny, Disabled | Audit | Audit | Deny | Azure Edge Hardware Center | undefined | 2.0.0 | BuiltIn | Essential | No | No |
