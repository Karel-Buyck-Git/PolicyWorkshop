# Company Monitoring Essential — Managed Grafana

## Tier rationale

**Essential** — Baseline hygiene for Managed Grafana: the non-negotiable controls every deployment should enforce from day one. This tier protects against credential theft, unencrypted data exposure, and accidental data loss for Managed Grafana workloads. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Managed Grafana workspaces should disable email settings | b6752a42-6fc3-46cb-8a15-33aa109407b1 |  | Disables SMTP settings configuration of email contact point for alerting in Grafana workspace. | Audit, Deny, Disabled | Audit | Audit | Deny | Managed Grafana | Monitoring | 1.0.0 | BuiltIn | Essential | No | No |
| 2 | Azure Managed Grafana workspaces should disable Grafana Enterprise upgrade | a08f2347-fe9c-482b-a944-f6a0e05124c0 |  | Disables Grafana Enterprise upgrade in Grafana workspace. | Audit, Deny, Disabled | Audit | Audit | Deny | Managed Grafana | Monitoring | 1.1.0 | BuiltIn | Essential | No | No |
| 3 | Azure Managed Grafana workspaces should disable service account | 0656cf40-485c-427b-b992-703a4ecf4f88 |  | Disables API keys and service account for automated workloads in Grafana workspace. | Audit, Deny, Disabled | Audit | Audit | Deny | Managed Grafana | Monitoring | 1.0.0 | BuiltIn | Essential | No | No |
| 4 | Configure Azure Managed Grafana workspaces to disable email settings | f757d603-5178-4168-ac45-5223f681023f |  | Disable SMTP settings configuration of email contact point for alerting in Grafana workspace. | Modify, Disabled | Modify | Modify | Modify | Managed Grafana | Monitoring | 1.0.0 | BuiltIn | Essential | No | Yes |
| 5 | Configure Azure Managed Grafana workspaces to disable service account | cc4dfa24-c7df-47e4-80ff-3728adb3f9a0 |  | Disable API keys and service account for automated workloads in Grafana workspace. | Modify, Disabled | Modify | Modify | Modify | Managed Grafana | Monitoring | 1.0.0 | BuiltIn | Essential | No | Yes |
