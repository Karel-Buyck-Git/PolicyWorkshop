# Tier 1 — Ready (Landing Zones & Design Areas)

The CAF **Ready** methodology prepares the Azure environment that everything else builds on. This tier is about the *design decisions* behind a landing zone; the policy implementation of any guardrail belongs to the `epac` skill. Design-area names and the reference architecture change — confirm specifics against the live source (`source-map.md` → Ready) before asserting them.

## What a landing zone is

An Azure landing zone is the pre-provisioned, governed environment (identity, networking, management, governance) into which workloads land. CAF gives a conceptual reference architecture (hub-spoke management-group hierarchy with platform and landing-zone areas) and a set of **design areas** to work through before you deploy. Use the architecture as a starting point and adapt it.

## The design areas

CAF groups the design areas into two sets. Evaluate them in order; revisit as requirements evolve.

**Environment design areas** (the platform foundation):
- **Azure billing & Microsoft Entra tenant** — tenant creation, enrollment, billing setup. Early, foundational.
- **Identity & access management** — the primary security boundary in the cloud; foundation for a secure, compliant architecture.
- **Resource organization** — subscription design and management-group hierarchy; drives governance, operations, and adoption patterns.
- **Network topology & connectivity** — hub/spoke or vWAN, hybrid connectivity, DNS, egress.

**Compliance design areas** (security, governance, ongoing control — where this skill leans):
- **Security** — controls and processes to protect the environment (links to Tier 3 Secure).
- **Management** — a management baseline for visibility, operations compliance, and protect/recover (links to Tier 4 Manage).
- **Governance** — automate auditing and enforcement of governance policies (links to Tier 2 Govern; **implemented via `epac`**).
- **Platform automation & DevOps** — tooling and templates to deploy landing zones and supporting resources.

## How to handle Ready questions

1. Clarify greenfield vs brownfield, and the scale (single team vs enterprise).
2. Walk the relevant design areas in order, surfacing the key decisions and trade-offs for each (don't dump all eight if only a few are in play).
3. Anchor on the CAF reference architecture and the management-group hierarchy (the resource-organization design area).
4. For the Governance / Security / Management compliance areas, give the *design* here and **hand implementation to `epac`** (policy assignments, guardrail JSON) and to Tiers 2–4 for the ongoing methodology.
5. Note the implementation options (portal, Bicep, Terraform, or EPAC-managed) but recommend EPAC for policy lifecycle — defer details to the `epac` skill.
6. Cite the specific design-area pages.

## Boundary reminder

This tier decides *what the landing zone should be and why*. The moment the conversation turns to "write the policy that enforces allowed regions / requires NSGs / denies public IPs," that's the `epac` skill. Keep the design rationale here; keep the policy code there.

## Source pointers (fetch before asserting specifics)

- Ready overview: `https://learn.microsoft.com/azure/cloud-adoption-framework/ready/`
- Design areas (current list + reference architecture): `https://learn.microsoft.com/azure/cloud-adoption-framework/ready/landing-zone/design-areas`
- Resource organization / management groups: `https://learn.microsoft.com/azure/cloud-adoption-framework/ready/landing-zone/design-area/resource-org`
- Implementation options: `https://learn.microsoft.com/azure/cloud-adoption-framework/ready/landing-zone/implementation-options`
- ALZ policy baseline (what's enforced by default): `https://aka.ms/alz/policies`
