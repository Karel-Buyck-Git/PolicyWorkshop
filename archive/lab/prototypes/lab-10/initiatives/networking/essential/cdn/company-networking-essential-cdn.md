# Company Networking Essential — CDN

## Tier rationale

**Essential** — Baseline hygiene for CDN: the non-negotiable controls every deployment should enforce from day one. This tier delivers TLS / HTTPS enforcement preventing in-transit interception. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Front Door Standard and Premium should be running minimum TLS version of 1.2 | 679da822-78a7-4eff-8fff-a899454a9970 |  | Setting minimal TLS version to 1.2 improves security by ensuring your custom domains are accessed from clients using TLS 1.2 or newer. Using versions of TLS less than 1.2 is not recommended since they are weak and do not support modern cryptographic algorithms. | Audit, Deny, Disabled | Audit | Audit | Deny | CDN | Networking | 1.0.0 | BuiltIn | Essential | No | No |
