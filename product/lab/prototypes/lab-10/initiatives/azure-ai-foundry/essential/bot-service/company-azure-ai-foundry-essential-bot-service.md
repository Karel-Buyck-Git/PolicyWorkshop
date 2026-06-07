# Company Azure AI Foundry Essential — Bot Service

## Tier rationale

**Essential** — Baseline hygiene for Bot Service: the non-negotiable controls every deployment should enforce from day one. This tier delivers RBAC and managed-identity controls eliminating shared credentials. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Bot Service should have isolated mode enabled | 52152f42-0dda-40d9-976e-abb1acdd611e |  | Bots should be set to 'isolated only' mode. This setting configures Bot Service channels that require traffic over the public internet to be disabled. | Audit, Audit, Deny, Deny, Disabled, Disabled | Audit | Audit | Deny | Bot Service | Azure AI Foundry | 2.1.0 | BuiltIn | Essential | No | No |
| 2 | Bot Service should have local authentication methods disabled | ffea632e-4e3a-4424-bf78-10e179bb2e1a |  | Disabling local authentication methods improves security by ensuring that a bot uses AAD exclusively for authentication. | Audit, Deny, Disabled | Audit | Audit | Deny | Bot Service | Azure AI Foundry | 1.0.0 | BuiltIn | Essential | No | No |
