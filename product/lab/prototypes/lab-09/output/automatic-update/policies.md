# Automatic Update Policies

## Tier rationale

**Essential** — No essential-tier policies are defined for Automatic Update in the current built-in policy set.

**Professional** — No professional-tier policies are defined for Automatic Update in the current built-in policy set.

**Enterprise** — Zero-trust and regulatory alignment for Automatic Update: controls that require infrastructure investment or map directly to compliance frameworks. This tier delivers zone-redundant deployments backing the 99.99% SLA. Together these policies protect against lateral movement, sovereign-data exfiltration, and audit gaps in regulated workloads. Maps to NIS2 Articles 21–23, ISO 27001 A.13.1.3 (network segregation) and A.18 (compliance), NIST SP 800-207 (Zero Trust).

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Virtual Machine Scale Sets with more than 2 availability zones should have automatic AZ rebalancing enabled | 40d17f6f-a9d2-4f1d-8c37-a699a5372a87 | Preview | This policy enables automatic AZ rebalancing for Virtual Machine Scale Sets that are otherwise zone resilient. Automatic zone rebalancing helps to ensure that your Virtual Machine Scale Sets are evenly distributed across the zones in the region. | Modify, Disabled | Modify | Modify | Automatic Update | Management | 1.0.0-preview | BuiltIn | Enterprise |
