# Company Security Professional — Attestation

## Tier rationale

**Professional** — Active security posture for Attestation: controls that produce signals an operations team must act on. This tier protects against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse for Attestation workloads. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Attestation providers should use private endpoints | 7b256a2d-058b-41f8-bed9-3f870541c40a |  | Private endpoints provide a way to connect Azure Attestation providers to your Azure resources without sending traffic over the public internet. By preventing public access, private endpoints help protect against undesired anonymous access. | AuditIfNotExists, Disabled | AuditIfNotExists | AuditIfNotExists | AuditIfNotExists | Attestation | Security | 1.0.0 | BuiltIn | Professional | No | No |
