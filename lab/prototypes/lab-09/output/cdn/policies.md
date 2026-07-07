# CDN Policies

## Tier rationale

**Essential** — Baseline hygiene for CDN: the non-negotiable controls every deployment should enforce from day one. This tier delivers TLS / HTTPS enforcement preventing in-transit interception. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

**Professional** — No professional-tier policies are defined for CDN in the current built-in policy set.

**Enterprise** — Zero-trust and regulatory alignment for CDN: controls that require infrastructure investment or map directly to compliance frameworks. This tier delivers private endpoints and private link removing the public attack surface. Together these policies protect against lateral movement, sovereign-data exfiltration, and audit gaps in regulated workloads. Maps to NIS2 Articles 21–23, ISO 27001 A.13.1.3 (network segregation) and A.18 (compliance), NIST SP 800-207 (Zero Trust).

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Front Door Standard and Premium should be running minimum TLS version of 1.2 | 679da822-78a7-4eff-8fff-a899454a9970 |  | Setting minimal TLS version to 1.2 improves security by ensuring your custom domains are accessed from clients using TLS 1.2 or newer. Using versions of TLS less than 1.2 is not recommended since they are weak and do not support modern cryptographic algorithms. | Audit, Deny, Disabled | Audit | Deny | CDN | Networking | 1.0.0 | BuiltIn | Essential |
| 2 | Azure Front Door profiles should use Premium tier that supports managed WAF rules and private link | dfc212af-17ea-423a-9dcb-91e2cb2caa6b |  | Azure Front Door Premium supports Azure managed WAF rules and private link to supported Azure origins. | Audit, Deny, Disabled | Audit | Deny | CDN | Networking | 1.0.0 | BuiltIn | Enterprise |
| 3 | Secure private connectivity between Azure Front Door Premium and Azure Storage Blob, or Azure App Service | daba2cce-8326-4af3-b049-81a362da024d |  | Private link ensures private connectivity between AFD Premium and Azure Storage Blob or Azure App Service over the Azure backbone network, without the Azure Storage Blob or the Azure App Service being publicly exposed to the internet. | Audit, Disabled | Audit | Audit | CDN | Networking | 1.0.0 | BuiltIn | Enterprise |
