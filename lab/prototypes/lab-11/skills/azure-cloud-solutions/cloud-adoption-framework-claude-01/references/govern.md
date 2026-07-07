# Tier 2 — Govern

The CAF **Govern** methodology is the heart of this skill. It defines *how* an organization controls its cloud use through guardrails — policies, procedures, and tools that keep cloud usage aligned with business goals, mitigate risk, and ensure compliance. Confirm current step names and tooling against the live source (`source-map.md` → Govern) before asserting specifics.

## Governance is a continuous cycle, not a project

CAF frames governance as an ongoing loop. You build the team once, then repeat the rest continuously to adapt to new tech, evolving risks, and changing requirements. Always present governance work as iterative.

## The five steps

1. **Build a cloud governance team.** A small, cross-functional, executive-sponsored team accountable for managing cloud risk, developing policies, and reporting on governance. Define its function, members, authority, and scope. Use a **RACI** to clarify who is Responsible/Accountable/Consulted/Informed across governance tasks (typically: governance team is Accountable for policy development; platform/workload teams are Responsible for implementing and enforcing controls).
2. **Assess cloud risks.** Identify and evaluate cloud-specific risks across domains — security, regulatory compliance, cost, operations, data, resource consistency, and emerging areas like AI. Output a prioritized risk register.
3. **Document cloud governance policies.** Write clear **policy statements** that address the assessed risks. Each statement should trace to a risk, be enforceable, and be reviewed periodically. This is the bridge to implementation.
4. **Enforce cloud governance policies.** Apply the policy statements as automated guardrails wherever possible. **In Azure this is Azure Policy — and in this team, that means the `epac` skill.** Govern decides *what* to enforce and *why*; `epac` builds and deploys the actual policy.
5. **Monitor cloud compliance.** Establish metrics and reporting — compliance levels, policy violations, incident response times, even user satisfaction. Review regularly, feed findings back into risk assessment (step 2). This closes the loop.

## Start with a governance MVP

Don't try to govern everything at once. Establish a **minimum viable** set of policy statements covering the top risks, enforce those, monitor, then expand in iterations. This keeps governance from blocking the business while still reducing the highest risks first.

## The govern → epac hand-off (be explicit)

This is the most important boundary in the toolkit:
- **Here (Govern):** identify the risk → write the policy statement → decide enforcement scope/altitude and effect intent (audit vs deny) → define the compliance metric.
- **`epac` skill:** translate the policy statement into an Azure Policy definition/initiative, assign it at the right scope, deploy via the EPAC pipeline, and surface compliance.

When a user asks "how do we enforce X," give the governance reasoning and the enforcement intent here, then route the implementation to `epac`.

## How to handle Govern questions

1. Identify which of the five steps the user is on.
2. For team/authority/scope questions → step 1, offer a RACI.
3. For "what should our policies be" → steps 2–3: assess risks first, then derive policy statements (never controls without risks).
4. For "how do we apply them" → step 4: design intent here, implementation via `epac`.
5. For "are we compliant / how do we track it" → step 5: metrics, reporting, the feedback loop.
6. Cite the specific govern pages.

## Source pointers (fetch before asserting specifics)

- Govern overview / build the team: `https://learn.microsoft.com/azure/cloud-adoption-framework/govern/`
- Assess cloud risks: `https://learn.microsoft.com/azure/cloud-adoption-framework/govern/assess-cloud-risks`
- Document policies: `https://learn.microsoft.com/azure/cloud-adoption-framework/govern/document-cloud-governance-policies`
- Enforce policies (Azure governance tools): `https://learn.microsoft.com/azure/cloud-adoption-framework/govern/enforce-cloud-governance-policies`
- Monitor compliance: `https://learn.microsoft.com/azure/cloud-adoption-framework/govern/monitor-cloud-governance`
