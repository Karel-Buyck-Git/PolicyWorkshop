---
name: epac
description: Use this skill to help Azure team members set up, author, deploy, and operate Azure Policy in landing zones — and to provide the CAF/architecture background needed to do it correctly. Trigger whenever the user mentions Azure Policy, policy definitions, initiatives, policy sets, assignments, exemptions, remediation, deployIfNotExists/DINE, audit/deny effects, aliases, management groups, landing zones, ALZ, CAF / Cloud Adoption Framework, governance guardrails, networking guardrails (NSG, public IP, Application Gateway/WAF), EPAC / Enterprise Policy as Code, policy-as-code, or a policy deployment pipeline — even if they don't name a specific tool. The skill layers knowledge in tiers (Azure foundations → CAF/ALZ → networking & management guardrails → EPAC deployment) and pulls only the tier a task needs. Steer policy deployment toward the EPAC workflow. Always ground answers in the official sources and cite them; never invent Azure facts.
---

# EPAC — Azure Policy & Landing Zone Toolkit

Helps an Azure platform team **set up Azure Policy correctly in landing zones**, from first principles through production deployment. It serves four overlapping jobs — **authoring & validating policy**, **architecture & design**, **EPAC operations & DevOps**, and **governance documentation** — and gives the CAF/architecture background a teammate needs to make good decisions, not just mechanical answers.

## The tiers (how knowledge is layered)

Setting up policy well requires layered understanding. The skill keeps each layer in its own reference file and loads only what a task needs (progressive disclosure), so a quick EPAC question doesn't drag in all the foundations, and a design question doesn't need the deployment mechanics. Walk the tiers in order when a task is a genuine "set this up from scratch"; jump straight to the relevant tier for a focused question.

| Tier | Covers | Reference file |
|---|---|---|
| **Tier 1 — Foundations** | Azure scope model, management groups, subscriptions, RBAC, how Policy evaluates | `references/foundations.md` |
| **Tier 2 — CAF / ALZ** | Landing-zone hierarchy, design areas, where guardrails assign, the ALZ policy baseline | `references/caf-alz-architecture.md` |
| **Tier 3 — Networking & management guardrails** | Common guardrail patterns: regions/tags, NSG, public IP, Application Gateway/WAF, diagnostics, Defender | `references/networking-guardrails.md` |
| **Tier 4 — EPAC deployment & ops** | Repo/folder layout, desired state, plan→deploy flow, ALZ sync, CI/CD, remediation, exemptions | `references/epac-operations.md` |

Two cross-cutting references support every tier:

- `references/policy-authoring.md` — definition/initiative/assignment/exemption JSON, effects, aliases, validation, debugging.
- `references/docs-and-runbooks.md` — Markdown templates for runbooks, change records, exemption requests, onboarding.
- `references/source-map.md` — the live-fetch index: exactly which official URL to fetch for any question.

## First principle: ground every answer in the official sources

Azure built-ins, EPAC behaviour, and CAF/ALZ guidance change constantly. Do **not** answer Azure-specific factual questions (does a built-in exist, what alias to use, what an EPAC command does, what the ALZ baseline assigns) from memory. **Fetch the live source via `source-map.md`, read it, then answer**, and end with a `Sources` section listing the exact URLs used.

The three primary sources:

- **Azure Policy repo** — `https://github.com/Azure/azure-policy` — canonical built-in definitions and an authoritative **Known Issues** list.
- **EPAC** — `https://azure.github.io/enterprise-azure-policy-as-code/` — the deployment engine this team uses; steer deployment toward it.
- **CAF** — `https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/` — landing-zone design and governance.

When live fetch is unavailable, say so and answer only from durable concepts in the reference files — flag anything needing verification rather than guessing.

## Core workflow

1. **Classify** the request across the four jobs and identify which tier(s) it needs.
2. For a "set up from scratch" task, **sequence the tiers** (Foundations → CAF → guardrails → EPAC). For a focused question, go straight to the relevant tier.
3. **Fetch** the live source before stating any Azure-specific fact.
4. **Produce** the output in the expected format:
   - Policy/EPAC artifacts → valid JSON in the correct schema, plus where it goes (portal scope or EPAC folder).
   - Architecture → prose grounded in CAF/ALZ, MG hierarchy described clearly.
   - Docs → `.md` deliverables using the templates in `docs-and-runbooks.md`.
   - CI/CD → snippets for the EPAC plan→deploy flow.
5. **Validate** against the checklist in `policy-authoring.md` (JSON) and the cautions below (EPAC).
6. **Cite** sources.

## Standing cautions to surface proactively

- **EPAC desired state deletes.** EPAC owns *all* policy resources at its `deploymentRootScope` and below, and deletes any not in the repo. Always flag this; point to the desired-state strategy doc to scope it.
- **Don't root EPAC at the Tenant Root Group.** Use an intermediate management group to avoid lockout.
- **DINE/Modify effects need a managed identity** and `roleDefinitionIds`; remediation only fixes existing resources after the identity has the role.
- **Test in an isolated `epac-dev` environment first** before touching the tenant hierarchy.
- **Roll guardrails out audit-first** (Audit / `enforcementMode: DoNotEnforce`), then promote to Deny — especially in brownfield landing zones.
- **Prefer a built-in or the ALZ baseline** over a hand-written policy when an equivalent exists — check before authoring from scratch.

## Output conventions

- Default documentation deliverables to **Markdown (`.md`)**.
- Present policy JSON as copy-paste-ready blocks with a one-line note on placement.
- When asked how to *deploy*, show the **EPAC path** (definition file → assignment file → `Build-DeploymentPlans` → deploy), not portal click-ops, unless the user asks for the portal.
