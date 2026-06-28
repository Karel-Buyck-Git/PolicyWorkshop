# CAF Governance Deliverables

Markdown templates for the artifacts a governance effort produces. Default output is **Markdown (`.md`)** — a file the team can drop into its repo or wiki. Fill templates with real, fetched CAF detail and the org's actual risks/decisions; cite sources. When a control needs policy code to realize it, describe the intent and **hand off to the `epac` skill**.

## Template: Cloud governance team charter (+ RACI)

```markdown
# Cloud Governance Team Charter

## Function
What the team is accountable for: engage stakeholders, assess cloud risks, develop & update policies, monitor compliance.

## Members
Cross-functional, small. Roles: program lead, cloud architecture, security, compliance, FinOps/cost.

## Authority
Executive sponsor: <name/role>. Mandate to define policy and require corrective action for non-compliance.

## Scope
Boundaries vs IT governance / platform / workload teams.

## RACI
| Task | Governance team | Exec sponsor | Platform team | Workload teams |
|---|---|---|---|---|
| Engage stakeholders | R,A | I | C | C |
| Assess cloud risks | A | I | R | R |
| Develop/update policies | R,A | I | C | C |
| Enforce policies | A,C | I | R | R |
| Monitor compliance | A,C | I | R | R |

## Sources
- <CAF govern links>
```

## Template: Cloud risk register

```markdown
# Cloud Risk Register

| ID | Risk | Domain (security/compliance/cost/ops/data/AI) | Likelihood | Impact | Priority | Owner | Mitigating policy statement |
|---|---|---|---|---|---|---|---|
| R-01 | <risk> | Security | High | High | P1 | <owner> | PS-01 |

Notes: prioritize P1s for the governance MVP. Each risk should map to at least one policy statement.

## Sources
- <CAF assess-cloud-risks link>
```

## Template: Policy statement set (the govern → epac bridge)

```markdown
# Cloud Governance Policy Statements

For each: the risk it addresses, the statement, the enforcement intent, and the implementation hand-off.

## PS-01 — <short title>
- **Risk addressed:** R-01
- **Statement:** <e.g. "All data-tier storage must disallow public network access.">
- **Scope / altitude:** <e.g. Corp management group>
- **Enforcement intent:** Audit first, then Deny
- **Implementation:** Azure Policy — build & deploy via the `epac` skill (definition + assignment + EPAC pipeline)
- **Compliance metric:** % compliant storage accounts in scope

## Sources
- <CAF document-policies link>
```

## Template: Compliance / governance status report

```markdown
# Governance Compliance Report — <period>

## Summary
Overall posture, notable changes since last period.

## Compliance by policy statement
| Policy statement | Scope | Compliant | Non-compliant | Trend |
|---|---|---|---|---|

## Violations & incidents
<key violations, response times>

## Actions & feedback into risk assessment
<what feeds back into the govern loop>

## Sources
- <CAF monitor link; epac Build-PolicyDocumentation / non-compliance reports>
```

## Template: Operations baseline definition

```markdown
# Operations Management Baseline

## Baseline (whole estate)
- Inventory & visibility: <how>
- Monitoring: diagnostics → central Log Analytics (enforced via epac DINE policy)
- Patch/update management: <approach>
- Backup: <policy>

## Per-workload commitments
| Workload | Criticality | SLA | RTO | RPO | Extra ops/resilience |
|---|---|---|---|---|---|

## Implementation hand-off
Baseline guardrails (diagnostics, backup, monitoring agents) → enforce as Azure Policy via the `epac` skill.

## Sources
- <CAF manage links>
```
