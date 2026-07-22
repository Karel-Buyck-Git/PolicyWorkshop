# Company Data Essential — Cache

## Tier rationale

**Essential** — Baseline hygiene for Cache: the non-negotiable controls every deployment should enforce from day one. This tier delivers RBAC and managed-identity controls eliminating shared credentials. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Cache for Redis should not use access keys for authentication | 3827af20-8f80-4b15-8300-6db0873ec901 |  | Not using local authentication methods like access keys and using more secure alternatives like Microsoft Entra ID (recommended) improves security for your Azure Cache for Redis. Learn more at aka.ms/redis/disableAccessKeyAuthentication | Audit, Deny, Disabled | Audit | Audit | Deny | Cache | Data | 1.0.0 | BuiltIn | Essential | No | No |
| 2 | Configure Azure Cache for Redis to disable non SSL ports | 766f5de3-c6c0-4327-9f4d-042ab8ae846c |  | Enable SSL only connections to Azure Cache for Redis. Use of secure connections ensures authentication between the server and the service and protects data in transit from network layer attacks such as man-in-the-middle, eavesdropping, and session-hijacking | Modify, Disabled | Modify | Modify | Modify | Cache | Data | 1.0.0 | BuiltIn | Essential | No | Yes |
| 3 | Only secure connections to your Azure Cache for Redis should be enabled | 22bee202-a82f-4305-9a2a-6d7f44d4dedb |  | Audit enabling of only connections via SSL to Azure Cache for Redis. Use of secure connections ensures authentication between the server and the service and protects data in transit from network layer attacks such as man-in-the-middle, eavesdropping, and session-hijacking | Audit, Deny, Disabled | Audit | Audit | Deny | Cache | Data | 1.0.0 | BuiltIn | Essential | No | No |
