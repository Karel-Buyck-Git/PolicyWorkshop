# Container Instances Policies

## Tier rationale

**Essential** — No essential-tier policies are defined for Container Instances in the current built-in policy set.

**Professional** — No professional-tier policies are defined for Container Instances in the current built-in policy set.

**Enterprise** — Zero-trust and regulatory alignment for Container Instances: controls that require infrastructure investment or map directly to compliance frameworks. This tier delivers diagnostic settings streaming to Log Analytics / Event Hub / Sentinel. Together these policies protect against lateral movement, sovereign-data exfiltration, and audit gaps in regulated workloads. Maps to NIS2 Articles 21–23, ISO 27001 A.13.1.3 (network segregation) and A.18 (compliance), NIST SP 800-207 (Zero Trust).

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Configure diagnostics for container group to log analytics workspace | 21c469fa-a887-4363-88a9-60bfd6911a15 |  | Appends the specified log analytics workspaceId and workspaceKey when any container group which is missing these fields is created or updated. Does not modify the fields of container groups created before this policy was applied until those resource groups are changed. | Yes | No | Append, Disabled | Append | Append | Append | Container Instances | Containers | 1.0.0 | BuiltIn | Enterprise |
