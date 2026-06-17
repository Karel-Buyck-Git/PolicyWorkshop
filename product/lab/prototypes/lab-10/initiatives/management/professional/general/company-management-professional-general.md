# Company Management Professional — General

## Tier rationale

**Professional** — Active security posture for General: controls that produce signals an operations team must act on. This tier delivers auto-remediation deployments. Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Configure subscriptions to set up preview features | e624c84f-2923-4437-9fd9-4115c6da3888 |  | This policy evaluates existing subscription's preview features. Subscriptions can be remediated to register to a new preview feature. New subscriptions will not be automatically registered. | AuditIfNotExists, DeployIfNotExists, Disabled | DeployIfNotExists | AuditIfNotExists | DeployIfNotExists | General | Management | 1.0.1 | BuiltIn | Professional | Yes | Yes |
