# Company undefined Professional — API for FHIR

## Tier rationale

**Professional** — Active security posture for API for FHIR: controls that produce signals an operations team must act on. This tier protects against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse for API for FHIR workloads. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | CORS should not allow every domain to access your API for FHIR | 0fea8f8a-4169-495d-8307-30ec335f387d |  | Cross-Origin Resource Sharing (CORS) should not allow all domains to access your API for FHIR. To protect your API for FHIR, remove access for all domains and explicitly define the domains allowed to connect. | Audit, Audit, Disabled, Disabled | Audit | Audit | Audit | API for FHIR | undefined | 1.1.0 | BuiltIn | Professional | No | No |
