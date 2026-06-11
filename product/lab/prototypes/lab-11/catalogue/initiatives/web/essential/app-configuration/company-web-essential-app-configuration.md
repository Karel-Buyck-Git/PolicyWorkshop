# Company Web Essential — App Configuration

## Tier rationale

**Essential** — Baseline hygiene for App Configuration: the non-negotiable controls every deployment should enforce from day one. This tier delivers RBAC and managed-identity controls eliminating shared credentials and TLS / HTTPS enforcement preventing in-transit interception. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | App Configuration should use geo-replication | d242c24b-bac7-439e-8af7-22d7dcfd3c4f |  | Use the geo-replication feature to create replicas in other locations of your current configuration store for enhanced resiliency and availability. Additionally, having multi-region replicas lets you better distribute load, lower latency, protect against datacenter outages, and compartmentalize globally distributed workloads. Learn more at: https://aka.ms/appconfig/geo-replication. | AuditIfNotExists, Disabled | AuditIfNotExists | AuditIfNotExists | AuditIfNotExists | App Configuration | Web | 1.0.0 | BuiltIn | Essential | No | No |
| 2 | App Configuration stores should have local authentication methods disabled | b08ab3ca-1062-4db3-8803-eec9cae605d6 |  | Disabling local authentication methods improves security by ensuring that App Configuration stores require Microsoft Entra identities exclusively for authentication. Learn more at: https://go.microsoft.com/fwlink/?linkid=2161954. | Audit, Deny, Disabled | Audit | Audit | Deny | App Configuration | Web | 1.0.1 | BuiltIn | Essential | No | No |
| 3 | Configure App Configuration stores to disable local authentication methods | 72bc14af-4ab8-43af-b4e4-38e7983f9a1f |  | Disable local authentication methods so that your App Configuration stores require Microsoft Entra identities exclusively for authentication. Learn more at: https://go.microsoft.com/fwlink/?linkid=2161954. | Modify, Disabled | Modify | Modify | Modify | App Configuration | Web | 1.0.1 | BuiltIn | Essential | No | Yes |
