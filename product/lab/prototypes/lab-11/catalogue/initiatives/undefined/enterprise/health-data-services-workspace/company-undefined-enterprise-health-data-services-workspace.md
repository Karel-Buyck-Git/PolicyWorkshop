# Company undefined Enterprise — Health Data Services workspace

## Tier rationale

**Enterprise** — Zero-trust and regulatory alignment for Health Data Services workspace: controls that require infrastructure investment or map directly to compliance frameworks. This tier delivers private endpoints and private link removing the public attack surface. Together these policies protect against lateral movement, sovereign-data exfiltration, and audit gaps in regulated workloads. Maps to NIS2 Articles 21–23, ISO 27001 A.13.1.3 (network segregation) and A.18 (compliance), NIST SP 800-207 (Zero Trust).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Health Data Services workspace should use private link | 64528841-2f92-43f6-a137-d52e5c3dbeac |  | Health Data Services workspace should have at least one approved private endpoint connection. Clients in a virtual network can securely access resources that have private endpoint connections through private links. For more information, visit: https://aka.ms/healthcareapisprivatelink. | Audit, Disabled | Audit | Audit | Audit | Health Data Services workspace | undefined | 1.0.0 | BuiltIn | Enterprise | No | No |
