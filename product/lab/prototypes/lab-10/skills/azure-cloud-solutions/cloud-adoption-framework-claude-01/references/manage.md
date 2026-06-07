# Tier 4 — Manage

The CAF **Manage** methodology establishes how the cloud estate is operated day to day — a management baseline that delivers visibility, operational compliance, and the ability to protect and recover. This skill carries the operational-governance design; specific monitoring/BCDR policy enforcement is implemented via `epac` and Azure tooling. Confirm specifics against the live source (`source-map.md` → Manage).

## The shape of Manage

Manage builds an **operations baseline** first, then layers richer commitments for important workloads. Think of it as three moves:

1. **Establish a management baseline.** The minimum operational footprint applied across the whole estate: inventory and visibility, monitoring (Azure Monitor / Log Analytics), security operations integration, patch/update management, and backup. This is the "everything gets at least this" layer — and the diagnostic-settings / monitoring guardrails that enforce it are implemented via `epac`.
2. **Define business commitments.** For each workload, agree the operational commitment (criticality, SLA, RTO/RPO). This maps workloads to the level of operations management and resilience they actually need, rather than over- or under-investing uniformly.
3. **Operations management & resilience.** Above the baseline: deeper monitoring and alerting, **protect & recover** (business continuity and disaster recovery — backup, replication, failover), platform and workload operations, and operational compliance.

## Operational governance, not just tooling

Manage is where governance meets operations: the management baseline is itself a set of guardrails (every resource sends diagnostics to a central workspace, every VM is backed up, etc.). Design those expectations here; **enforce them as Azure Policy via `epac`** (DINE policies for diagnostic settings, backup, monitoring agents). Monitor compliance feeds back into the Govern loop (Tier 2, step 5).

## How to handle Manage questions

1. Distinguish baseline (whole estate) vs per-workload commitment (criticality-driven).
2. For "how do we make sure everything is monitored/backed up" → baseline guardrail design here, implementation via `epac` (DINE diagnostic settings / backup), remediation via EPAC remediation tasks.
3. For resilience/BCDR → business-commitment framing (RTO/RPO) then the Azure protect-and-recover services.
4. Connect operational compliance back to the Govern monitoring step.
5. Cite the specific Manage pages.

## Source pointers (fetch before asserting specifics)

- Manage overview: `https://learn.microsoft.com/azure/cloud-adoption-framework/manage/`
- Management baseline: `https://learn.microsoft.com/azure/cloud-adoption-framework/manage/azure-management-guide/`
- Business commitments / operations management: `https://learn.microsoft.com/azure/cloud-adoption-framework/manage/considerations/`
- Protect & recover (BCDR): `https://learn.microsoft.com/azure/cloud-adoption-framework/manage/protect`
- Azure Monitor: `https://learn.microsoft.com/azure/azure-monitor/`
