# Durable Task Policies

| # | Policy | Tag | Description | Allowed Values | Default Value | MVP Value | Category | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Durable Task schedulers should not allow open IP allowlists |  | Deny Durable Task schedulers that include 0.0.0.0/0 in their IP allowlist to prevent exposure to the public internet. Remove the open entry so that only trusted networks can reach the scheduler. | Audit, Deny, Disabled | Audit | Deny | Durable Task | 1.0.0 | BuiltIn | Professional |
