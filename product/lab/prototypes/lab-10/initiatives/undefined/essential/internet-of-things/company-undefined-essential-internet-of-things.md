# Company undefined Essential — Internet of Things

## Tier rationale

**Essential** — Baseline hygiene for Internet of Things: the non-negotiable controls every deployment should enforce from day one. This tier delivers RBAC and managed-identity controls eliminating shared credentials and TLS / HTTPS enforcement preventing in-transit interception. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure IoT Hub should have local authentication methods disabled for Service Apis | 672d56b3-23a7-4a3c-a233-b77ed7777518 |  | Disabling local authentication methods improves security by ensuring that Azure IoT Hub exclusively require Azure Active Directory identities for Service Api authentication. Learn more at: https://aka.ms/iothubdisablelocalauth. | Audit, Deny, Disabled | Audit | Audit | Deny | Internet of Things | undefined | 1.0.0 | BuiltIn | Essential | No | No |
| 2 | Configure Azure IoT Hub to disable local authentication | 9f8ba900-a70f-486e-9ffc-faf907305376 |  | Disable local authentication methods so that your Azure IoT Hub exclusively require Azure Active Directory identities for authentication. Learn more at: https://aka.ms/iothubdisablelocalauth. | Modify, Disabled | Modify | Modify | Modify | Internet of Things | undefined | 1.0.0 | BuiltIn | Essential | No | Yes |
