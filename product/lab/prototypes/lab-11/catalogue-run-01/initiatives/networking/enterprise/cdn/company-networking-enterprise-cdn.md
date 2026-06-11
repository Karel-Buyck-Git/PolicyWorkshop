# Company Networking Enterprise — CDN

## Tier rationale

**Enterprise** — Zero-trust and regulatory alignment for CDN: controls that require infrastructure investment or map directly to compliance frameworks. This tier delivers private endpoints and private link removing the public attack surface. Together these policies protect against lateral movement, sovereign-data exfiltration, and audit gaps in regulated workloads. Maps to NIS2 Articles 21–23, ISO 27001 A.13.1.3 (network segregation) and A.18 (compliance), NIST SP 800-207 (Zero Trust).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Front Door profiles should use Premium tier that supports managed WAF rules and private link | dfc212af-17ea-423a-9dcb-91e2cb2caa6b |  | Azure Front Door Premium supports Azure managed WAF rules and private link to supported Azure origins. | Audit, Deny, Disabled | Audit | Audit | Deny | CDN | Networking | 1.0.0 | BuiltIn | Enterprise | No | No |
| 2 | Secure private connectivity between Azure Front Door Premium and Azure Storage Blob, or Azure App Service | daba2cce-8326-4af3-b049-81a362da024d |  | Private link ensures private connectivity between AFD Premium and Azure Storage Blob or Azure App Service over the Azure backbone network, without the Azure Storage Blob or the Azure App Service being publicly exposed to the internet. | Audit, Disabled | Audit | Audit | Audit | CDN | Networking | 1.0.0 | BuiltIn | Enterprise | No | No |
