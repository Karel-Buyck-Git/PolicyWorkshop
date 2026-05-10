# Tier classification rules

Assign each policy to the highest-fit tier. If a policy matches more than one
rule, pick the **most specific** match (Enterprise > Professional > Essential
when in doubt).

## Essential — Foundational governance & security

Match if the policy is primarily about:

- governance baselines (allowed locations, allowed resource types, naming)
- managed identity adoption
- cryptography defaults (TLS minimum version, encryption-in-transit)
- standard protocol enforcement (HTTPS-only, FTPS-only)
- data protection backups (soft delete, purge protection)
- tagging and resource hierarchy
- SAS / shared-key / local-auth disablement (when not network-scoped)
- MFA, RBAC hygiene
- SKU governance (allowed SKUs, deny non-Premium where mandated)

## Professional — Hardened virtual datacenter

Match if the policy is primarily about:

- public network access controls (disable, restrict)
- VNet integration / network injection
- CORS configuration
- resilience and availability (zones, replicas, geo-redundancy)
- recovery (failover, restore) — see note below
- Privileged Identity Management (PIM) controls

> **Note on "recovery"**: this term has historically appeared under both
> Essential and Professional. Treat it as **Professional** unless the policy
> is purely a data-protection backup policy (then Essential).

## Enterprise — Advanced enterprise isolation

Match if the policy is primarily about:

- audit / AuditIfNotExists for security posture surfacing
- diagnostic logging, resource logs, Log Analytics integration
- private endpoint / private link enforcement
- managed private endpoint approval
- platform version enforcement (e.g., stv2)
- Conditional Access integration
- micro-segmentation / advanced traffic inspection

## Tie-breakers

1. If a policy mentions "private endpoint" or "private link", it is **Enterprise**, regardless of effect.
2. If a policy enforces a TLS minimum version or HTTPS-only, it is **Essential**.
3. If a policy enables/configures diagnostic settings or resource logs, it is **Enterprise**.
4. If a policy disables public network access, it is **Professional**.
5. If a policy configures managed identity or local-auth disablement, it is **Essential**.

## Out-of-scope signals (do not classify)

- Display name starts with `[Deprecated]`
- Display name contains `[Preview]`
- Policy has no display name
