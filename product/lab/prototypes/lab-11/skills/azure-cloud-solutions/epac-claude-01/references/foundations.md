# Tier 1 — Azure Foundations

The background a teammate needs before authoring or placing policy. Keep this conceptual and durable; confirm any specific limits, role names, or built-in behaviour against the live sources in `source-map.md`. Use this tier when someone is new to Azure governance or when a question reveals a gap in the scope/MG/RBAC model — then move up the tiers.

## The scope hierarchy (where everything attaches)

Azure resources live in a four-level hierarchy. Policy and RBAC both attach to a scope and **inherit downward**:

```
Management group(s)   ← policy & RBAC assigned here cascade to everything below
  └── Subscription
        └── Resource group
              └── Resource
```

Key consequences for policy:
- Assign a guardrail at the **highest scope where it's universally true** so every child inherits it (fewer assignments, consistent enforcement).
- Management groups can nest (up to several levels); design the hierarchy first (Tier 2), then decide guardrail altitude.
- Inheritance is cumulative and **most-restrictive wins** — overlapping Deny policies from different scopes both apply.

## Management groups

Containers above subscriptions used to organize and govern at scale. The **Tenant Root Group** sits at the very top; you should generally *not* assign broad guardrails (or root EPAC) there — use an **intermediate root** management group for flexibility and to avoid lockout. Designing the MG tree is a CAF topic (Tier 2); for foundations, just know: MGs are the primary altitude for landing-zone guardrails, and a subscription belongs to exactly one MG.

## RBAC vs Policy (two different control planes)

Newcomers conflate these — keep them distinct:
- **RBAC** controls *who can do what* (identity → permissions on a scope). Roles like `Owner`, `Contributor`, `Resource Policy Contributor`.
- **Azure Policy** controls *what the resources themselves are allowed to be* (configuration guardrails), regardless of who's acting.

They intersect for **DINE/Modify** policies: those deploy/change resources using a **managed identity**, which needs an RBAC role (declared in the policy's `roleDefinitionIds`) to act. So a policy can require RBAC to function. EPAC's deploy flow reflects this — a separate roles-deployment step (`Deploy-RolesPlan`) needs `Role Based Access Control Administrator`.

## How Azure Policy evaluates (mental model)

- A definition has a single **effect** in its `policyRule` (audit, deny, deployIfNotExists, modify, etc. — see `policy-authoring.md`).
- On **create/update**, Policy evaluates matching assignments before the resource provider acts; Deny blocks non-compliant writes, Append/Modify can alter the request.
- For **existing** resources, compliance is assessed on a periodic scan (and on-demand). DINE/Modify don't retroactively fix existing resources without a **remediation task**.
- **Aliases** are how a policy references a resource property (e.g. `Microsoft.Storage/storageAccounts/supportsHttpsTrafficOnly`). They must exist for the API version, or the condition silently never matches — verify aliases live.
- The Azure Policy repo's **Known Issues** list documents resource types that bypass evaluation, have read-only aliases, or can't be reliably denied — always cross-check unusual targets there.

## Built-in vs custom

- **Built-in policies/initiatives** are maintained by Microsoft (the `Azure/azure-policy` repo is their canonical source). Prefer them.
- **Initiatives (policy sets)** bundle many definitions behind one assignment and one parameter surface — how the ALZ baseline and most compliance frameworks (CIS, NIST, ISO) are delivered.
- **Custom** definitions are a maintenance cost; write one only when no built-in/baseline equivalent exists.

## Where this leads

Once the foundations are clear, the natural progression is: **Tier 2** to design the MG hierarchy and decide guardrail placement, **Tier 3** for the specific guardrail patterns, **Tier 4** to deploy them as code with EPAC. Authoring mechanics live in `policy-authoring.md`; documentation in `docs-and-runbooks.md`.

## Source pointers (fetch before asserting specifics)

- Scope concept: `https://learn.microsoft.com/azure/governance/policy/concepts/scope`
- Management groups overview: `https://learn.microsoft.com/azure/governance/management-groups/overview`
- Azure Policy overview: `https://learn.microsoft.com/azure/governance/policy/overview`
- Azure RBAC overview: `https://learn.microsoft.com/azure/role-based-access-control/overview`
