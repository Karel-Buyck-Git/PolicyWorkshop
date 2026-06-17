# CAF / Azure Landing Zone Architecture

Use this for design and review questions: management-group hierarchy, where guardrails assign, the ALZ policy baseline, and CAF design areas. Architecture guidance evolves — confirm specifics against CAF docs and the ALZ policy list in `source-map.md`, and present recommendations as CAF-aligned defaults the team can adapt, not absolutes.

## Mental model

Azure Landing Zones (ALZ) are the CAF's opinionated, policy-driven foundation: a management-group hierarchy with guardrails (Azure Policy) assigned at the right altitude so every subscription inherits the right controls. Policy is the enforcement layer of the landing zone — design the hierarchy first, then decide which guardrails assign where.

## Reference management-group hierarchy

CAF's conceptual ALZ hierarchy (adapt names to the org):

```
Tenant Root Group
└── Intermediate root (e.g. "contoso")     ← EPAC deploymentRootScope lives here, NOT tenant root
    ├── Platform
    │   ├── Management      (logging, monitoring, automation)
    │   ├── Identity        (domain controllers, identity services)
    │   └── Connectivity    (hubs, firewalls, DNS, ExpressRoute/VPN)
    ├── Landing Zones
    │   ├── Corp            (internal, no direct internet)
    │   └── Online          (internet-facing)
    ├── Decommissioned
    └── Sandbox
```

Why an **intermediate root** and not Tenant Root Group: flexibility, blast-radius control, and avoiding lockout (also why EPAC roots here). Confirm the current CAF hierarchy at the management-groups design-area page.

## Where guardrails assign (altitude matters)

Policy inheritance flows downward, so assign each control at the highest scope where it's universally true:

- **Intermediate root** — org-wide guardrails: allowed locations, required tags, deny classic resources, baseline security/Defender, diagnostic settings to central Log Analytics.
- **Platform** — controls specific to platform subscriptions (e.g. stricter networking, key management).
- **Connectivity** — network guardrails (deny public IPs except where intended, NSG/route requirements).
- **Corp** — no public endpoints / private-only data plane, stricter egress.
- **Online** — allow controlled internet exposure but enforce WAF/TLS/DDoS.
- **Sandbox** — light guardrails; often audit-only to allow experimentation.
- **Decommissioned** — deny new resources, enforce shutdown.

Use **excluded scopes / `notScopes`** for narrow carve-outs and **exemptions** (time-bound) for legitimate exceptions — never loosen a high-level assignment to accommodate one subscription.

## The ALZ policy baseline

Microsoft maintains the ALZ policy baseline (Policies, Sets, Assignments) at `https://aka.ms/alz/policies` — the source of truth across portal, Bicep, and Terraform deployments. When designing, start from this baseline rather than inventing guardrails: identify which baseline initiatives map to each MG, then add org-specific custom policies on top. With EPAC, pull the baseline via the ALZ library sync (see `epac-operations.md`) and customize through the structure file.

When asked "what does ALZ enforce at X" or "is there a baseline policy for Y", **fetch the ALZ policy list** and answer from it — don't assert from memory.

## CAF design areas (for broader design questions)

The landing-zone design areas frame trade-offs beyond policy: identity & access, network topology & connectivity, resource organization, governance, management, security, platform automation & DevOps. Governance is where Azure Policy lives, but design questions often touch several — fetch the design-areas page and reason across them. Pair policy guardrails with the relevant design area (e.g. a "deny public IP" guardrail belongs to the network-topology + governance discussion).

## How to handle design requests

1. Clarify scope: greenfield ALZ, or adjusting an existing one (brownfield)?
2. Anchor on the CAF hierarchy and the ALZ baseline (fetch both).
3. Recommend MG structure + which guardrails sit at which altitude, with reasoning.
4. Note enforcement mechanics: inheritance, exclusions vs exemptions, audit-first rollout (`enforcementMode: DoNotEnforce` or `Audit` effects) before flipping to `Deny`.
5. Connect to delivery: how it gets deployed via EPAC, and what documentation/runbook should accompany it (`docs-and-runbooks.md`).
6. Cite CAF + ALZ sources.

## Rollout pattern that avoids breaking workloads

Introduce guardrails **audit-first**: assign with `Audit`/`AuditIfNotExists` or `enforcementMode = DoNotEnforce`, review compliance, communicate to resource owners, remediate, then promote to `Deny`/enforced. This is especially important for brownfield landing zones where existing resources may be non-compliant.
