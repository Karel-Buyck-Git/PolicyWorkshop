# Company undefined Professional — Healthcare APIs

## Tier rationale

**Professional** — Active security posture for Healthcare APIs: controls that produce signals an operations team must act on. This tier protects against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse for Healthcare APIs workloads. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | CORS should not allow every domain to access your FHIR Service | fe1c9040-c46a-4e81-9aea-c7850fbb3aa6 |  | Cross-Origin Resource Sharing (CORS) should not allow all domains to access your FHIR Service. To protect your FHIR Service, remove access for all domains and explicitly define the domains allowed to connect. | Audit, Audit, Disabled, Disabled | Audit | Audit | Audit | Healthcare APIs | undefined | 1.1.0 | BuiltIn | Professional | No | No |
