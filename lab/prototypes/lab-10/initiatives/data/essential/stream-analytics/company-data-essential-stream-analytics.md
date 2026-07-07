# Company Data Essential — Stream Analytics

## Tier rationale

**Essential** — Baseline hygiene for Stream Analytics: the non-negotiable controls every deployment should enforce from day one. This tier delivers RBAC and managed-identity controls eliminating shared credentials. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Stream Analytics job should connect to trusted inputs and outputs | fe8684d6-3c5b-45c0-a08b-fa92653c2e1c |  | Ensure that Stream Analytics jobs do not have arbitrary Input or Output connections that are not defined in the allow-list. This checks that Stream Analytics jobs don't exfiltrate data by connecting to arbitrary sinks outside your organization. | Deny, Disabled, Audit | Audit | Audit | Deny | Stream Analytics | Data | 1.1.0 | BuiltIn | Essential | No | No |
| 2 | Stream Analytics job should use managed identity to authenticate endpoints | ea6c4923-510a-4346-be26-1894919a5b97 |  | Ensure that Stream Analytics jobs only connect to endpoints using managed identity authentication. | Deny, Disabled, Audit | Audit | Audit | Deny | Stream Analytics | Data | 1.0.0 | BuiltIn | Essential | No | No |
