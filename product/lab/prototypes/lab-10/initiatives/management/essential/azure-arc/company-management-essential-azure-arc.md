# Company Management Essential — Azure Arc

## Tier rationale

**Essential** — Baseline hygiene for Azure Arc: the non-negotiable controls every deployment should enforce from day one. This tier delivers TLS / HTTPS enforcement preventing in-transit interception. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Configure Azure Arc-enabled Servers to enable automatic upgrades | f9dfba6f-7430-4214-a666-342b3d3d0d62 |  | The Automatic Upgrade feature allows servers to stay updated with no action from the user after opting in. This policy ensures that Azure Arc-enabled servers are configured to be opted in for automatic upgrades. | Modify, Disabled | Modify | Modify | Modify | Azure Arc | Management | 1.0.0 | BuiltIn | Essential | No | Yes |
| 2 | Deny Extended Security Updates (ESUs) license creation or modification. | 4c660f31-eafb-408d-a2b3-6ed2260bd26c | Preview | This policy enables you to restrict the creation or modification of ESU licenses for Windows Server 2012 Arc machines. For more details on pricing please visit https://aka.ms/ArcWS2012ESUPricing | Deny, Disabled | Deny | Deny | Deny | Azure Arc | Management | 1.0.0-preview | BuiltIn | Essential | No | No |
| 3 | Enable Extended Security Updates (ESUs) license to keep Windows 2012 machines protected after their support lifecycle has ended. | 4864134f-d306-4ff5-94d8-ea4553b18c97 | Preview | Enable Extended Security Updates (ESUs) license to keep Windows 2012 machines protected even after their support lifecycle has ended. Learn How to prepare to deliver Extended Security Updates for Windows Server 2012 through AzureArc please visit https://learn.microsoft.com/en-us/azure/azure-arc/servers/prepare-extended-security-updates. For more details on pricing please visit https://aka.ms/ArcWS2012ESUPricing | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | Azure Arc | Management | 1.0.0-preview | BuiltIn | Essential | Yes | Yes |
