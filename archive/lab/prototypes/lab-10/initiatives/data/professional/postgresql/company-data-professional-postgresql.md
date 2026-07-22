# Company Data Professional — PostgreSQL

## Tier rationale

**Professional** — Active security posture for PostgreSQL: controls that produce signals an operations team must act on. This tier delivers audit-log and monitoring controls that produce signals for ops teams. Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Auditing with PgAudit should be enabled for PostgreSQL flexible servers | 4eb5e667-e871-4292-9c5d-8bbb94e0c908 |  | This policy helps audit any PostgreSQL flexible servers in your environment which is not enabled to use pgaudit. | AuditIfNotExists, Disabled | AuditIfNotExists | AuditIfNotExists | AuditIfNotExists | PostgreSQL | Data | 1.0.0 | BuiltIn | Professional | No | No |
| 2 | Log checkpoints should be enabled for PostgreSQL flexible servers | 70be9e12-c935-49ac-9bd8-fd64b85c1f87 |  | This policy helps audit any PostgreSQL flexible servers in your environment without log_checkpoints setting enabled. | AuditIfNotExists, Disabled | AuditIfNotExists | AuditIfNotExists | AuditIfNotExists | PostgreSQL | Data | 1.0.0 | BuiltIn | Professional | No | No |
| 3 | Log connections should be enabled for PostgreSQL flexible servers | 086709ac-11b5-478d-a893-9567a16d2ae3 |  | This policy helps audit any PostgreSQL flexible servers in your environment without log_connections setting enabled. | AuditIfNotExists, Disabled | AuditIfNotExists | AuditIfNotExists | AuditIfNotExists | PostgreSQL | Data | 1.0.0 | BuiltIn | Professional | No | No |
