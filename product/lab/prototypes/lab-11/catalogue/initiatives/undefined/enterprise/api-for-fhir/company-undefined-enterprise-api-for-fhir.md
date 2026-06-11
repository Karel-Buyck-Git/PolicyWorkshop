# Company undefined Enterprise — API for FHIR

## Tier rationale

**Enterprise** — Zero-trust and regulatory alignment for API for FHIR: controls that require infrastructure investment or map directly to compliance frameworks. This tier delivers private endpoints and private link removing the public attack surface, customer-managed keys (CMK / BYOK) for cryptographic sovereignty, and direct mapping to regulatory framework controls. Together these policies protect against lateral movement, sovereign-data exfiltration, and audit gaps in regulated workloads. Maps to NIS2 Articles 21–23, ISO 27001 A.13.1.3 (network segregation) and A.18 (compliance), NIST SP 800-207 (Zero Trust).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure API for FHIR should use a customer-managed key to encrypt data at rest | 051cba44-2429-45b9-9649-46cec11c7119 |  | Use a customer-managed key to control the encryption at rest of the data stored in Azure API for FHIR when this is a regulatory or compliance requirement. Customer-managed keys also deliver double encryption by adding a second layer of encryption on top of the default one done with service-managed keys. | Audit, Audit, Disabled, Disabled | Audit | Audit | Audit | API for FHIR | undefined | 1.1.0 | BuiltIn | Enterprise | No | No |
| 2 | Azure API for FHIR should use private link | 1ee56206-5dd1-42ab-b02d-8aae8b1634ce |  | Azure API for FHIR should have at least one approved private endpoint connection. Clients in a virtual network can securely access resources that have private endpoint connections through private links. For more information, visit: https://aka.ms/fhir-privatelink. | Audit, Disabled | Audit | Audit | Audit | API for FHIR | undefined | 1.0.0 | BuiltIn | Enterprise | No | No |
