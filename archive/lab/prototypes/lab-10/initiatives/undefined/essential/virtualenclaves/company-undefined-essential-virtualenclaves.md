# Company undefined Essential — VirtualEnclaves

## Tier rationale

**Essential** — Baseline hygiene for VirtualEnclaves: the non-negotiable controls every deployment should enforce from day one. This tier delivers TLS / HTTPS enforcement preventing in-transit interception. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Do not allow creation of resource types outside of the allowlist | ead33d15-8ff9-44d8-be85-24144ecc859e |  | This policy prevents deployment of resource types outside of the explicitly allowed types, in order to maintain security in a virtual enclave. https://aka.ms/VirtualEnclaves | Audit, Deny, Disabled | Deny | Audit | Deny | VirtualEnclaves | undefined | 1.0.0 | BuiltIn | Essential | No | No |
| 2 | Do not allow creation of specified resource types or types under specific providers | 337ef0ec-0703-499e-a57c-b4155034e606 |  | The resource providers and types specified via parameter list are not allowed to be created without explicit approval from the security team. If an exemption is granted to the policy assignment, the resource can be leveraged within the enclave. https://aka.ms/VirtualEnclaves | Audit, Deny, Disabled | Deny | Audit | Deny | VirtualEnclaves | undefined | 1.0.0 | BuiltIn | Essential | No | No |
