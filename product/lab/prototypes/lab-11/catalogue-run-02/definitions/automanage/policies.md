# Automanage Policies

## Tier rationale

**Essential** — Baseline hygiene for Automanage: the non-negotiable controls every deployment should enforce from day one. This tier delivers RBAC and managed-identity controls eliminating shared credentials and TLS / HTTPS enforcement preventing in-transit interception. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

**Professional** — No professional-tier policies are defined for Automanage in the current built-in policy set.

**Enterprise** — No enterprise-tier policies are defined for Automanage in the current built-in policy set.

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | A managed identity should be enabled on your machines | e4953962-5ae4-43eb-bb92-d66fd5563487 | Preview | Resources managed by Automanage should have a managed identity. | Audit, Disabled | Audit | Audit | Audit | Automanage | Management | 1.0.0-preview | BuiltIn | Essential | No | No |
| 2 | Automanage Configuration Profile Assignment should be Conformant | fd4726f4-a5fc-4540-912d-67c96fc992d5 | Preview | Resources managed by Automanage should have a status of Conformant or ConformantCorrected. | AuditIfNotExists, Disabled | AuditIfNotExists | AuditIfNotExists | AuditIfNotExists | Automanage | Management | 1.0.0-preview | BuiltIn | Essential | No | No |
| 3 | Boot Diagnostics should be enabled on virtual machines | fb97d6e1-5c98-4743-a439-23e0977bad9e | Preview | Azure virtual machines should have boot diagniostics enabled. | Audit, Disabled | Audit | Audit | Audit | Automanage | Management | 1.0.0-preview | BuiltIn | Essential | No | No |
| 4 | Configure virtual machines to be onboarded to Azure Automanage | f889cab7-da27-4c41-a3b0-de1f6f87c550 |  | Azure Automanage enrolls, configures, and monitors virtual machines with best practice as defined in the Microsoft Cloud Adoption Framework for Azure. Use this policy to apply Automanage to your selected scope. | AuditIfNotExists, DeployIfNotExists, Disabled | DeployIfNotExists | AuditIfNotExists | DeployIfNotExists | Automanage | Management | 2.4.0 | BuiltIn | Essential | No | Yes |
| 5 | Configure virtual machines to be onboarded to Azure Automanage with Custom Configuration Profile | b025cfb4-3702-47c2-9110-87fe0cfcc99b |  | Azure Automanage enrolls, configures, and monitors virtual machines with best practice as defined in the Microsoft Cloud Adoption Framework for Azure. Use this policy to apply Automanage with your own customized Configuration Profile to your selected scope. | AuditIfNotExists, DeployIfNotExists, Disabled | DeployIfNotExists | AuditIfNotExists | DeployIfNotExists | Automanage | Management | 1.4.0 | BuiltIn | Essential | Yes | Yes |
| 6 | Hotpatch should be enabled for Windows Server Azure Edition VMs | 6d02d2f7-e38b-4bdc-96f3-adc0a8726abc |  | Minimize reboots and install updates quickly with hotpatch. Learn more at https://docs.microsoft.com/azure/automanage/automanage-hotpatch | Audit, Deny, Disabled | Audit | Audit | Deny | Automanage | Management | 1.0.0 | BuiltIn | Essential | No | No |
