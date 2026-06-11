# Company undefined Enterprise — Health Deidentification Service

## Tier rationale

**Enterprise** — Zero-trust and regulatory alignment for Health Deidentification Service: controls that require infrastructure investment or map directly to compliance frameworks. This tier delivers private endpoints and private link removing the public attack surface. Together these policies protect against lateral movement, sovereign-data exfiltration, and audit gaps in regulated workloads. Maps to NIS2 Articles 21–23, ISO 27001 A.13.1.3 (network segregation) and A.18 (compliance), NIST SP 800-207 (Zero Trust).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Health Data Services de-identification service should use private link | d9b2d63d-a233-4123-847a-7f7e5f5d7e7a |  | Azure Health Data Services de-identification service should have at least one approved private endpoint connection. Clients in a virtual network can securely access resources that have private endpoint connections through private links. | Audit, Disabled | Audit | Audit | Audit | Health Deidentification Service | undefined | 1.0.0 | BuiltIn | Enterprise | No | No |
