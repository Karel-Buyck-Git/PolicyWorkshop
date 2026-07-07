# Company Data Professional — Azure Data Explorer

## Tier rationale

**Professional** — Active security posture for Azure Data Explorer: controls that produce signals an operations team must act on. This tier delivers network hardening (public access disabled, VNet integration, firewall rules). Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Configure Azure Data Explorer clusters with private endpoints | a47272e1-1d5d-4b0b-b366-4873f1432fe0 |  | Private endpoints connect your virtual networks to Azure services without a public IP address at the source or destination.  By mapping private endpoints to Azure Data Explorer, you can reduce data leakage risks.  Learn more at: [ServiceSpecificAKA.ms]. | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | Azure Data Explorer | Data | 1.0.0 | BuiltIn | Professional | Yes | Yes |
| 2 | Virtual network injection should be enabled for Azure Data Explorer | 9ad2fd1f-b25f-47a2-aa01-1a5a779e6413 |  | Secure your network perimeter with virtual network injection which allows you to enforce network security group rules, connect on-premises and secure your data connection sources with service endpoints. | Audit, Deny, Disabled | Audit | Audit | Deny | Azure Data Explorer | Data | 1.0.0 | BuiltIn | Professional | No | No |
