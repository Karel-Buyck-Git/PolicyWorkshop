# Migrate Policies

## Tier rationaleHardened

**Essential** — No essential-tier policies are defined for Migrate in the current built-in policy set.

**Professional** — No professional-tier policies are defined for Migrate in the current built-in policy set.

**Enterprise** — Zero-trust and regulatory alignment for Migrate: controls that require infrastructure investment or map directly to compliance frameworks. This tier delivers private endpoints and private link removing the public attack surface. Together these policies protect against lateral movement, sovereign-data exfiltration, and audit gaps in regulated workloads. Maps to NIS2 Articles 21–23, ISO 27001 A.13.1.3 (network segregation) and A.18 (compliance), NIST SP 800-207 (Zero Trust).

| #   | Policy                                                     | Policy ID                            | Tag | Description                                                                                                                                                                                                           | Allowed Values              | Default Value     | Hardened Value    | Category | Version | Type    | Tier       |
| --- | ---------------------------------------------------------- | ------------------------------------ | --- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------- | ----------------- | ----------------- | -------- | ------- | ------- | ---------- |
| 1   | Configure Azure Migrate resources to use private DNS zones | 7590a335-57cf-4c95-babd-ecbc8fafeb1f |     | Use private DNS zones to override the DNS resolution for a private endpoint. A private DNS zone links to your virtual network to resolve to your Azure Migrate project. Learn more at: https://aka.ms/privatednszone. | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | Migrate  | 1.0.0   | BuiltIn | Enterprise |
