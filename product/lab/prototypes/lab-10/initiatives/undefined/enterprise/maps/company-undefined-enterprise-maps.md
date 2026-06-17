# Company undefined Enterprise — Maps

## Tier rationale

**Enterprise** — Zero-trust and regulatory alignment for Maps: controls that require infrastructure investment or map directly to compliance frameworks. This tier delivers private endpoints and private link removing the public attack surface. Together these policies protect against lateral movement, sovereign-data exfiltration, and audit gaps in regulated workloads. Maps to NIS2 Articles 21–23, ISO 27001 A.13.1.3 (network segregation) and A.18 (compliance), NIST SP 800-207 (Zero Trust).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Maps Accounts should use private link. | cb26889c-214c-4b29-811e-6f2109a1959f |  | Azure Private Link lets you connect your virtual networks to Azure services without a public IP address at the source or destination. The Private Link platform handles the connectivity between the consumer and services over the Azure backbone network. By mapping private endpoints to Maps Account, you can reduce data leakage risks. | Audit, Disabled | Audit | Audit | Audit | Maps | undefined | 1.0.0 | BuiltIn | Enterprise | No | No |
| 2 | Configure private DNS zones for private endpoints that connect to Azure Maps Accounts. | a58f2efa-faf4-434a-8fe9-2dca18adb5f5 |  | Private DNS records allow private connections to private endpoints. Private endpoint connections allow secure communication by enabling private connectivity to your Azure Maps Account without a need for public IP addresses at the source or destination. | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | Maps | undefined | 1.0.0 | BuiltIn | Enterprise | Yes | Yes |
| 3 | Public network access should be disabled for Azure Maps Accounts. | a46d869a-f759-4404-8289-7737e7a1f79e |  | Disabling public network access on a Maps Account improves security by ensuring your Maps Account can only be accessed from a private endpoint. | Audit, Deny, Disabled | Audit | Audit | Deny | Maps | undefined | 1.0.0 | BuiltIn | Enterprise | No | No |
