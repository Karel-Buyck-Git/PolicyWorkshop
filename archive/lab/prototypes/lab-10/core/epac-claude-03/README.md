# epac-claude-03 — Azure Policy as Code, three ways

The same Azure Policy governance implemented in three parallel approaches for comparison.
Each folder is self-contained with its own README, environment config, and CI/CD pipelines.

| Folder | Approach | Engine | Deploy command |
|---|---|---|---|
| `Json/` | EPAC (Enterprise Policy as Code) | PowerShell `EnterprisePolicyAsCode` | `Build-DeploymentPlans` / `Deploy-PolicyPlan` / `Deploy-RolesPlan` |
| `Terraform/` | Terraform + azurerm | `terraform` | `terraform plan` / `apply` |
| `Bicep/` | Bicep (ARM) | `az` CLI | `az deployment mg what-if` / `create` |

## Shared governance (identical across all three)

- **Two environments:** `epac-dev` (isolated) and `tenant01` (production), CAFv3 scopes.
- **Custom policies:** deny public IP, require Owner tag, restrict NSG rules, deploy NSG diagnostics (DINE).
- **Custom initiatives:** security baseline, tagging governance.
- **Compliance:** MCSB always; NIST 800-53 R5 on; PCI-DSS optional.
- **Governance:** Allowed Locations (sandbox excluded), tag governance.
- **Exemptions:** sample time-boxed sandbox waiver.

## Key differences to highlight in the workshop

| Capability | EPAC (Json) | Terraform | Bicep |
|---|---|---|---|
| Desired-state with **deletion** of out-of-band policy | Yes (within root scope) | Only what's in state | No (additive) |
| **Remediation role assignments** auto-calculated | Yes | No (manual) | No (manual) |
| Multi-environment model | native `pacSelector` | tfvars + separate state | parameter files + target MG |
| Plan/preview | `Build-DeploymentPlans` | `terraform plan` | `az deployment mg what-if` |
| State to manage | none (reads Azure) | tfstate backend | none (reads Azure) |
| Best fit | policy-at-scale governance teams | existing Terraform estates | existing ARM/Bicep estates |

See each subfolder's README for run instructions. Start any of them against `epac-dev` /
the dev MG, review the plan/what-if, then promote to `tenant01`.
