# Governance Documentation & Runbooks

Use this to produce deliverables: runbooks, change records, exemption requests, onboarding explainers, and policy documentation. Default output format is **Markdown (`.md`)** — write a file the team can drop into the repo or wiki. Ground all Azure specifics in the live sources (`source-map.md`) and cite them. Fill templates with real, fetched detail; never leave invented policy IDs or effects.

When a polished Word/PDF version is explicitly requested, generate the Markdown first, then convert using the docx/pdf skills — but `.md` is the default.

## General rules

- Be specific: real definition/assignment names, scopes, effects, and IDs (fetched, not guessed).
- Write for the stated audience — an engineer runbook differs from a stakeholder explainer.
- Prefer short prose + tables over walls of text; include a "Sources" footer.
- For anything operational, include rollback and verification steps.

## Template: Remediation runbook

```markdown
# Runbook — Remediate <policy/initiative name>

## Purpose
What this remediates and why (the control, the risk, the trigger).

## Scope
- Assignment: <assignment name / ID>
- Policy/initiative: <name / ID>
- Target scope: <MG / subscription>
- Effect: <DeployIfNotExists | Modify>

## Pre-checks
- Confirm the assignment's managed identity exists and holds the roles in `roleDefinitionIds`.
- Confirm current non-compliance count (portal Compliance blade or `Export-NonComplianceReports`).

## Procedure (EPAC)
1. Identify non-compliant resources: <how>.
2. Create remediation tasks: `New-AzRemediationTasks` for <pacEnvironment / assignment>.
3. Monitor task progress to completion.

## Verification
- Re-run compliance scan; confirm resources moved to compliant.

## Rollback / safety
- DINE/Modify changes resource config; note what each remediation alters and how to revert.

## Sources
- <links used>
```

## Template: Policy change record

```markdown
# Change Record — <short title>

| Field | Value |
|---|---|
| Date | <date> |
| Author | <name> |
| Type | New / Update / Remove policy/assignment/exemption |
| EPAC environment(s) | epac-dev → tenant01 |
| Risk | Low / Medium / High |

## What changed
<files added/modified under Definitions/, the effect, the scope>

## Why
<control / requirement driving the change>

## Deployment plan review
<summary of Build-DeploymentPlans output: resources added/updated/deleted>

## Validation
<how it was validated in epac-dev>

## Rollback
<revert the commit + redeploy plan>

## Sources
- <links>
```

## Template: Exemption request

```markdown
# Exemption Request

| Field | Value |
|---|---|
| Requested by | <name / team> |
| Assignment | <policy assignment ID> |
| Definition reference(s) | <policyDefinitionReferenceIds, if scoping to set members> |
| Scope | <resource / RG / subscription> |
| Category | Waiver | Mitigated |
| Expires on | <date — keep it time-bound> |

## Justification
<why compliance is not possible/appropriate; compensating controls if Mitigated>

## Review
- Approver: <name>   Decision: <approve/deny>   Date: <date>

## Implementation
Add exemption file under `policyExemptions/`, deploy via EPAC.

## Sources
- <links>
```

## Template: Onboarding explainer (for a new engineer)

```markdown
# Azure Policy & EPAC — Team Onboarding

## How we do policy here
We manage all Azure Policy as code with EPAC. The repo is the single source of truth — if a policy isn't in the repo, EPAC will delete it from Azure. Never make policy changes in the portal on managed scopes.

## The lay of the land
- Definitions/ — our policies, initiatives, assignments, exemptions.
- global-settings.jsonc — environments (epac-dev, tenant01) and scopes.
- ALZ baseline — synced from Microsoft's ALZ library; we customize via the structure file.

## How to make a change
1. Branch. 2. Edit/add files under Definitions/. 3. Build-DeploymentPlans against epac-dev. 4. Review the plan. 5. Deploy to epac-dev, validate. 6. PR → main → deploy to tenant01 with approvals.

## Key safety rules
- deploymentRootScope is an intermediate MG, never tenant root.
- Test in epac-dev first.
- Roll guardrails out audit-first, then enforce.

## Where to look things up
- Built-ins & known issues: github.com/Azure/azure-policy
- EPAC: azure.github.io/enterprise-azure-policy-as-code
- CAF/ALZ: learn.microsoft.com/azure/cloud-adoption-framework + aka.ms/alz/policies
```

## Template: Policy documentation

For documenting existing assignments/compliance, prefer EPAC's `Build-PolicyDocumentation` (generates Markdown/CSV) and then edit for narrative. When hand-writing, include per assignment: name, scope, effect, parameters, mapped compliance controls, exclusions/exemptions, and owner.
