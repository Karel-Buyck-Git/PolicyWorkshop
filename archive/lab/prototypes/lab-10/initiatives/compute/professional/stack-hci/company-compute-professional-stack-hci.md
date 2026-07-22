# Company Compute Professional — Stack HCI

## Tier rationale

**Professional** — Active security posture for Azure Stack HCI: controls that produce signals an operations team must act on. This tier delivers Microsoft Defender plans surfacing threat signals. Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Stack HCI servers should have consistently enforced application control policies | dad3a6b9-4451-492f-a95c-69efc6f3fada | Preview | At a minimum, apply the Microsoft WDAC base policy in enforced mode on all Azure Stack HCI servers. Applied Windows Defender Application Control (WDAC) policies must be consistent across servers in the same cluster. | Audit, Disabled, AuditIfNotExists | AuditIfNotExists | Audit | AuditIfNotExists | Stack HCI | Compute | 1.0.0-preview | BuiltIn | Professional | No | No |
