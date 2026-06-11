# Company Container Services Essential — Container Apps

## Tier rationale

**Essential** — Baseline hygiene for Container Apps: the non-negotiable controls every deployment should enforce from day one. This tier delivers RBAC and managed-identity controls eliminating shared credentials and TLS / HTTPS enforcement preventing in-transit interception. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Authentication should be enabled on Container Apps | 2b585559-a78e-4cc4-b1aa-fb169d2f6b96 |  | Container Apps Authentication is a feature that can prevent anonymous HTTP requests from reaching the Container App, or authenticate those that have tokens before they reach the Container App | AuditIfNotExists, Disabled | AuditIfNotExists | AuditIfNotExists | AuditIfNotExists | Container Apps | Container Services | 1.0.1 | BuiltIn | Essential | No | No |
| 2 | Container App should configure with volume mount | 7c9f3fbb-739d-4844-8e42-97e3be6450e0 |  | Enforce the use of volume mounts for Container Apps to ensure availability of persistent storage capacity. | Audit, Deny, Disabled | Audit | Audit | Deny | Container Apps | Container Services | 1.0.1 | BuiltIn | Essential | No | No |
| 3 | Container Apps should disable external network access | 783ea2a8-b8fd-46be-896a-9ae79643a0b1 |  | Disable external network access to your Container Apps by enforcing internal-only ingress. This will ensure inbound communication for Container Apps is limited to callers within the Container Apps environment. | Audit, Deny, Disabled | Audit | Audit | Deny | Container Apps | Container Services | 1.1.0 | BuiltIn | Essential | No | No |
| 4 | Container Apps should only be accessible over HTTPS | 0e80e269-43a4-4ae9-b5bc-178126b8a5cb |  | Use of HTTPS ensures server/service authentication and protects data in transit from network layer eavesdropping attacks. Disabling 'allowInsecure' will result in the automatic redirection of requests from HTTP to HTTPS connections for container apps. | Audit, Deny, Disabled | Audit | Audit | Deny | Container Apps | Container Services | 1.0.1 | BuiltIn | Essential | No | No |
| 5 | Managed Identity should be enabled for Container Apps | b874ab2d-72dd-47f1-8cb5-4a306478a4e7 |  | Enforcing managed identity ensures Container Apps can securely authenticate to any resource that supports Azure AD authentication | Audit, Deny, Disabled | Audit | Audit | Deny | Container Apps | Container Services | 1.0.1 | BuiltIn | Essential | No | No |
