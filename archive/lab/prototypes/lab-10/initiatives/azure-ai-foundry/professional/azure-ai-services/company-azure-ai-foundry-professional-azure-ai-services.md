# Company Azure AI Foundry Professional — Azure Ai Services

## Tier rationale

**Professional** — Active security posture for Azure AI Services: controls that produce signals an operations team must act on. This tier delivers audit-log and monitoring controls that produce signals for ops teams. Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Diagnostic logs in Azure AI services resources should be enabled | 1b4d1c4e-934c-4703-944c-27c82c06bebb |  | Enable logs for Azure AI services resources. This enables you to recreate activity trails for investigation purposes, when a security incident occurs or your network is compromised | AuditIfNotExists, Disabled | AuditIfNotExists | AuditIfNotExists | AuditIfNotExists | Azure Ai Services | Azure AI Foundry | 1.0.0 | BuiltIn | Professional | No | No |
