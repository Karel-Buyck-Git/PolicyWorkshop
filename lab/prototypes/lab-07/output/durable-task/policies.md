# Durable Task Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | MVP Value | Category | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Durable Task schedulers should not allow open IP allowlists | d82527a7-91cd-409f-b96e-049600b16b9e |  | Deny Durable Task schedulers that include 0.0.0.0/0 in their IP allowlist to prevent exposure to the public internet. Remove the open entry so that only trusted networks can reach the scheduler. | Audit, Deny, Disabled | Audit | Deny | Durable Task | 1.0.0 | BuiltIn | Professional |
