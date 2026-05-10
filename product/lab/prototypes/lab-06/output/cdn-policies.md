# CDN Policies

| # | Policy | Tag | Description | Allowed Values | Default Value | MVP Value | Category | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Front Door profiles should use Premium tier that supports managed WAF rules and private link |  | Azure Front Door Premium supports Azure managed WAF rules and private link to supported Azure origins. | Audit, Deny, Disabled | Audit | Deny | CDN | 1.0.0 | BuiltIn | Enterprise |
| 2 | Secure private connectivity between Azure Front Door Premium and Azure Storage Blob, or Azure App Service |  | Private link ensures private connectivity between AFD Premium and Azure Storage Blob or Azure App Service over the Azure backbone network, without the Azure Storage Blob or the Azure App Service being publicly exposed to the internet. | Audit, Disabled | Audit | Audit | CDN | 1.0.0 | BuiltIn | Enterprise |
| 3 | Azure Front Door Standard and Premium should be running minimum TLS version of 1.2 |  | Setting minimal TLS version to 1.2 improves security by ensuring your custom domains are accessed from clients using TLS 1.2 or newer. Using versions of TLS less than 1.2 is not recommended since they are weak and do not support modern cryptographic algorithms. | Audit, Deny, Disabled | Audit | Deny | CDN | 1.0.0 | BuiltIn | Essential |
