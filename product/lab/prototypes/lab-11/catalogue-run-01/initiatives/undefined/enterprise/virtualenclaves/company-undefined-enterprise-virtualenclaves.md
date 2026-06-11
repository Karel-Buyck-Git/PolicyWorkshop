# Company undefined Enterprise — VirtualEnclaves

## Tier rationale

**Enterprise** — Zero-trust and regulatory alignment for VirtualEnclaves: controls that require infrastructure investment or map directly to compliance frameworks. This tier delivers private endpoints and private link removing the public attack surface. Together these policies protect against lateral movement, sovereign-data exfiltration, and audit gaps in regulated workloads. Maps to NIS2 Articles 21–23, ISO 27001 A.13.1.3 (network segregation) and A.18 (compliance), NIST SP 800-207 (Zero Trust).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Configure Storage Accounts to restrict network access through network ACL bypass configuration only. | 41a72361-06e3-4e80-832a-690bd0708bc1 |  | To improve the security of Storage Accounts, enable access only through network ACL bypass. This policy should be used in combination with a private endpoint for storage account access. | Modify, Disabled | Modify | Modify | Modify | VirtualEnclaves | undefined | 1.0.0 | BuiltIn | Enterprise | No | Yes |
| 2 | Storage Accounts should restrict network access through network ACL bypass configuration only. | 7809fda1-ba27-48c1-9c63-1f5aee46ba89 |  | To improve the security of Storage Accounts, enable access only through network ACL bypass. This policy should be used in combination with a private endpoint for storage account access. | Audit, Deny, Disabled | Audit | Audit | Deny | VirtualEnclaves | undefined | 1.0.0 | BuiltIn | Enterprise | No | No |
