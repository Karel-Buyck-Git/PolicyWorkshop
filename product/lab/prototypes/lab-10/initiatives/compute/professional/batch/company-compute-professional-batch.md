# Company Compute Professional — Batch

## Tier rationale

**Professional** — Active security posture for Batch: controls that produce signals an operations team must act on. This tier delivers network hardening (public access disabled, VNet integration, firewall rules). Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Configure Batch accounts with private endpoints | 0ef5aac7-c064-427a-b87b-d47b3ddcaf73 |  | Private endpoints connect your virtual network to Azure services without a public IP address at the source or destination. By mapping private endpoints to Batch accounts, you can reduce data leakage risks. Learn more about private links at: https://docs.microsoft.com/azure/batch/private-connectivity. | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | Batch | Compute | 1.0.0 | BuiltIn | Professional | Yes | Yes |
