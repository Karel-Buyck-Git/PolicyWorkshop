# Company Management Essential — Portal

## Tier rationale

**Essential** — Baseline hygiene for Portal: the non-negotiable controls every deployment should enforce from day one. This tier delivers encryption-at-rest with service-managed keys. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Shared dashboards should not have markdown tiles with inline content | 04c655fe-0ac7-48ae-9a32-3a2e208c7624 |  | Disallow creating a shared dashboard that has inline content in markdown tiles and enforce that the content should be stored as a markdown file that's hosted online. If you use inline content in the markdown tile, you cannot manage encryption of the content. By configuring your own storage, you can encrypt, double encrypt and even bring your own keys. Enabling this policy restricts users to use 2020-09-01-preview or above version of shared dashboards REST API. | Audit, Deny, Disabled | Audit | Audit | Deny | Portal | Management | 1.1.0 | BuiltIn | Essential | No | No |
