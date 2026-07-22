# CDN Policies

## Tier rationale

**Essential** — Baseline hygiene for CDN: the non-negotiable controls every deployment should enforce from day one. This tier delivers TLS / HTTPS enforcement preventing in-transit interception. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

**Professional** — Active security posture for CDN: controls that produce signals an operations team must act on. This tier delivers network hardening (public access disabled, VNet integration, firewall rules). Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

**Enterprise** — No enterprise-tier policies are defined for CDN in the current built-in policy set.

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Front Door Standard and Premium should be running minimum TLS version of 1.2 | 679da822-78a7-4eff-8fff-a899454a9970 |  | Setting minimal TLS version to 1.2 improves security by ensuring your custom domains are accessed from clients using TLS 1.2 or newer. Using versions of TLS less than 1.2 is not recommended since they are weak and do not support modern cryptographic algorithms. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | CDN | Networking | 1.0.0 | BuiltIn | Essential |
| 2 | Azure Front Door profiles should use Premium tier that supports managed WAF rules and private link | dfc212af-17ea-423a-9dcb-91e2cb2caa6b |  | Azure Front Door Premium supports Azure managed WAF rules and private link to supported Azure origins. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | CDN | Networking | 1.0.0 | BuiltIn | Professional |
| 3 | Secure private connectivity between Azure Front Door Premium and Azure Storage Blob, or Azure App Service | daba2cce-8326-4af3-b049-81a362da024d |  | Private link ensures private connectivity between AFD Premium and Azure Storage Blob or Azure App Service over the Azure backbone network, without the Azure Storage Blob or the Azure App Service being publicly exposed to the internet. | No | No | Audit, Disabled | Audit | Audit | Audit | CDN | Networking | 1.0.0 | BuiltIn | Professional |
