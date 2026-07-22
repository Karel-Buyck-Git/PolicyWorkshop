---
name: cloud-adoption-framework
description: Use this skill for Cloud Adoption Framework (CAF) guidance focused on governance — landing-zone readiness, the CAF Govern methodology, the Secure methodology, and the Manage methodology. Trigger whenever the user asks about CAF, Cloud Adoption Framework, landing-zone design areas, Azure readiness, cloud governance, governance team/RACI, cloud risk assessment, governance policy statements, the govern/secure/manage methodologies, compliance disciplines, security posture / Zero Trust alignment for cloud adoption, operations baseline, or how to structure an Azure environment for governance and operations — even if they don't name CAF explicitly. This skill gives the *what / why / where* of governance design and methodology; for the hands-on Azure Policy implementation (writing/deploying policy as code), defer to the `epac` skill. Always ground answers in the official CAF docs and cite them; never invent guidance.
---

# Cloud Adoption Framework — Governance-focused Toolkit

Helps an Azure team apply Microsoft's Cloud Adoption Framework with a governance lean: getting the environment **ready**, then running the **Govern**, **Secure**, and **Manage** methodologies as the ongoing disciplines that keep a cloud estate controlled, secure, and well-operated. It serves architects, governance leads, and platform engineers who need the methodology and design reasoning — the *what, why, and where* — not the line-by-line policy code.

## Boundary with the `epac` skill (read this first)

This skill and `epac` are deliberately complementary; keep the line clean to avoid duplicating each other:

- **This skill (CAF)** = methodology and design. *Why* a guardrail exists, *what* discipline it belongs to, *where* in the environment it applies, and *how the governance process runs* (team, risk assessment, policy statements, enforcement strategy, compliance monitoring).
- **`epac` skill** = implementation. The actual Azure Policy JSON, initiatives, assignments, and the EPAC deployment pipeline.

When a CAF answer reaches the point of "now implement this as policy," **point to the `epac` skill** rather than writing policy here. When `epac` needs the design rationale or placement, that's this skill's territory. Cross-reference; don't re-derive.

## First principle: ground every answer in the official CAF docs

CAF is reorganized periodically (methodologies, design-area names, and step models change). Do **not** answer CAF-specific questions from memory. **Fetch the relevant CAF page via `references/source-map.md`, read it, then answer**, and end with a `Sources` section listing the URLs used. If live fetch is unavailable, say so and answer only from the durable concepts in the reference files, flagging anything that needs verification.

Primary source: **CAF** — `https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/`.

## The tiers (governance-leaning slice of CAF)

This skill covers the governance-relevant CAF methodologies. Strategy/Plan/Adopt are out of primary scope — pointers live in `source-map.md` if a question strays there. Load only the tier a task needs.

| Tier | CAF methodology | Reference file |
|---|---|---|
| **Tier 1 — Ready** | Landing zones, the design areas (environment + compliance), Azure environment setup | `references/ready-landing-zones.md` |
| **Tier 2 — Govern** | The 5-step govern process: team → assess risks → document policies → enforce → monitor | `references/govern.md` |
| **Tier 3 — Secure** | Security posture modernization, incident readiness, CIA triad, Zero Trust / Defender alignment | `references/secure.md` |
| **Tier 4 — Manage** | Operations baseline, business commitments, monitoring, protect & recover (BCDR) | `references/manage.md` |

Cross-cutting:
- `references/deliverables.md` — Markdown templates for CAF governance artifacts (governance team charter & RACI, cloud-risk register, policy-statement set, compliance report, operations baseline).
- `references/source-map.md` — the live-fetch index: which CAF URL to fetch for which question.

## Core workflow

1. **Classify** the request: which methodology/tier(s) does it touch? Is it design (this skill) or implementation (hand to `epac`)?
2. For a "set up governance from scratch" task, **sequence**: Ready (foundation) → Govern (process) → Secure & Manage (ongoing disciplines). For a focused question, go straight to the tier.
3. **Fetch** the relevant CAF page before stating specifics.
4. **Produce** the output:
   - Design/methodology guidance → prose grounded in CAF, with clear decisions and trade-offs.
   - Governance artifacts → `.md` deliverables using `references/deliverables.md`.
   - Anything requiring policy code or deployment → describe the intent, then **defer to `epac`**.
5. **Cite** CAF sources.

## Standing guidance to surface proactively

- **Governance is continuous, not a project.** The CAF Govern model is a cycle (assess → document → enforce → monitor, repeating); frame recommendations as an iterative loop, not a one-off.
- **Start with a governance MVP, then expand.** Don't try to govern everything at once — establish a minimum viable set of policy statements tied to the top risks, then iterate.
- **Tie every policy to a risk.** CAF policy statements should trace back to an assessed business risk; don't recommend controls without the risk rationale.
- **Security spans every phase.** The Secure methodology is end-to-end (strategy through operations) and aligns to Zero Trust and Defender for Cloud secure score — don't treat security as a single gate.
- **Design areas are sequential but iterative.** Evaluate the landing-zone design areas in order, and revisit them as requirements change.
- **Implementation lives in `epac`.** Whenever the answer becomes "write/deploy a policy," route there.

## Output conventions

- Default deliverables to **Markdown (`.md`)**.
- Present methodology guidance as decisions + reasoning + CAF references, not vague principles.
- Be explicit about the hand-off to `epac` whenever a recommendation needs policy-as-code to realize it.
