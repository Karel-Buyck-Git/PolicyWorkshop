# Demo EPAC Package — Session Feedback Log

**Date:** 2026-07-07
**Goal:** Build a small customer EPAC package for a testing setup on the Azure "demo" tenant and get it ready to deploy to the `Demo` management group.
**Status:** Package built and **verified deployable** via a local EPAC plan. Nothing committed/pushed yet — changes left in the working tree for review on another device.

---

## 1. Reference values (for picking this up elsewhere)

| Item | Value |
| --- | --- |
| Customer / prefix | `demo` |
| `pacOwnerId` (stable — keep for life of package) | `d52e9de2-35b6-4451-88ba-6ff4fca1b01f` |
| Tenant (Delaware Demo Tenant) | `89ee4175-19ce-415b-8c99-fb858c8782c1` |
| Deployment root scope | `/providers/Microsoft.Management/managementGroups/Demo` (note capital **D**) |
| pacSelector / environment | `epac-dev` |
| Enforcement | `Audit` (report-only) |
| Region | `westeurope` |
| Policy selection | `management/essential/tags` (4 policies), `management/essential/naming` (169 policies) |
| GitHub repo | `buyckka_dlwr/azure-policy` |
| Deploy branch | `alpha/epac-builder/demo` |

### Service principals (created in Entra, roles assigned at `Demo` MG)

| App | Client ID | Azure role @ `Demo` MG | Federated credential subject |
| --- | --- | --- | --- |
| `demo-spn-epac-plan` | `d5bc66f6-5653-4c62-b299-ef2db4a0926d` | Reader | `repo:buyckka_dlwr/azure-policy:ref:refs/heads/alpha/epac-builder/demo` |
| `demo-spn-epac-policy` | `9f386ace-c39a-49dc-9226-2454a4b9fba6` | Resource Policy Contributor | `repo:buyckka_dlwr/azure-policy:environment:epac-policy` |
| `demo-spn-epac-roles` | `65200692-d053-46aa-a169-6bc9595cdd2c` | Role Based Access Control Administrator | `repo:buyckka_dlwr/azure-policy:environment:epac-roles` |

All three federated-credential subjects were **fixed this session** (they previously contained the literal placeholder `repo:<org>/<repo>:...`).

---

## 2. What we accomplished

1. **Generated the demo input + manifest**
   - `customer/manifests/demo.input.json` (tracked) — customer + selections + tag parameters.
   - `customer/manifests/demo.manifest.jsonc` (**gitignored** — generated working file) — filled with real tenant ID, `Demo` MG scope (corrected casing), Audit enforcement, per-selection `scope` overrides (so no separate management-group design file was needed).
2. **Built the package** → `customer/package/` (EPAC `Definitions/`, workflow, `lineage.json`, `report.md`). `--check --strict` passes.
3. **Set a proper stable `pacOwnerId`** (`d52e9de2-…`).
4. **Wired GitHub OIDC deployment** (guide: `docs/scaffold-deployment-guide.md` §12–13):
   - Confirmed the 3 SPN role assignments at the `Demo` MG.
   - Fixed all 3 federated-credential subjects to the real org/repo/branch.
   - Added a **repo-root** workflow `.github/workflows/epac-demo.yml` (the package's bundled `.github/workflows/epac.yml` can't run from a subfolder — GitHub only discovers workflows at the repo root). It points `DEFINITIONS` at `catalogue-builder/customer/package/Definitions` and triggers on the demo branch / manual dispatch.
5. **Verified deployable** with a local `Build-DeploymentPlans -PacEnvironmentSelector epac-dev` (PowerShell 7 + EPAC 11.4.7):
   > 169 policy definitions + 2 policy sets + 2 assignments — all **New** at `/managementGroups/Demo`; no role changes.

---

## 3. Findings / issues discovered (need addressing)

### 3.1 Builder bugs in the JSON renderer (FIXED this session, pending review)

The generated package was **not deployable as-is** against EPAC v11.4.7. Fixes applied in `flows/epac_builder/render_json.py`:

| # | Symptom (EPAC error) | Fix |
| --- | --- | --- |
| 1 | `pacEnvironment epac-dev does not contain required desiredState field` | Emit `desiredState.strategy = "ownedOnly"` per environment |
| 2 | `...does not contain required desiredState.keepDfcSecurityAssignments field` | Emit `desiredState.keepDfcSecurityAssignments = false` |
| 3 | `Leaf Node //…: each tree branch must define either a definitionEntry or a non-empty definitionEntryList` | Replace invalid top-level `policySetDefinitionName` with EPAC's `definitionEntry: { policySetName, displayName }` |

**Design decision to revisit:** `desiredState.strategy` was hardcoded to `ownedOnly` (safe / non-destructive default for a generated customer scaffold). EPAC's canonical model for a dedicated root MG is `full` (EPAC owns and deletes anything not in the repo). Consider making this **manifest-driven** (per-environment) rather than hardcoded, and likewise `keepDfcSecurityAssignments`.

### 3.2 Same wrong format exists in the producer catalogue (NOT yet fixed)

The catalogue's own `*.assignment.json` scaffolds (≈98 files under `catalogue/initiatives/**`) also use the invalid top-level `policySetDefinitionName`. These are producer-generated reference scaffolds (see `flows/catalogue_builder/create_initiatives.py` and `flows/definition_gen/scaffold.py`, both of which emit `policySetDefinitionName`). If those scaffolds are ever meant to be directly EPAC-deployable, the producer needs the same `definitionEntry` fix. Out of scope this session (producer pipeline / `/catalogue-builder-run`).

### 3.3 Contoso golden fixture regenerated

Because the renderer changed, `examples/contoso/package/` was regenerated to stay byte-consistent with CI (`examples/contoso/verify.sh` diffs it). Only the JSON flavour changed (global-settings + 2 assignments); terraform/bicep fixtures unaffected. **Review this** — it's a change to shared tooling output, not just the demo.

### 3.4 Housekeeping before committing

- `customer/package/Output/` (EPAC plan artifact from the local test run) is **not gitignored** and would otherwise be committed. Add an ignore rule (e.g. `package/Output/` in a `customer/.gitignore`) before committing.
- **Convention tension:** `customer/` is normally the "empty scaffold"; the committed worked sample lives in `examples/contoso/`. Committing a real package into `customer/package/` is intentional for the deploy branch but diverges from the repo's usual pattern. Decide whether the demo should instead live as its own example or in a separate deployment repo.
- `demo.manifest.jsonc` is gitignored, so the committed sources are `demo.input.json` + the rendered `package/`. Deployment works from the package, but the manifest itself won't be in git — confirm that's acceptable, or adjust the ignore for this case.

---

## 4. Environment / tooling notes

- **EPAC requires PowerShell 7+** (`pwsh`). The default terminal here is Windows PowerShell 5.1, which **cannot** load `EnterprisePolicyAsCode` (min version 7.0). Run EPAC cmdlets via `pwsh`.
- EPAC uses the **Az PowerShell** context (`Connect-AzAccount` / `Get-AzContext`), not the `az` CLI. During the session the Az context was `karel@dlwaemsptemp.onmicrosoft.com` on tenant `89ee4175-…`.
- `check_env.py` warns that **bash + diff are missing** on this machine — needed to run `examples/contoso/verify.sh` locally (install Git for Windows to get them). Could not run the byte-for-byte fixture verification here; relied on direct regeneration instead.
- Modules installed this session (CurrentUser): `EnterprisePolicyAsCode` 11.4.7.

---

## 5. Uncommitted changes in the working tree (7 real content diffs)

- `flows/epac_builder/render_json.py` — builder fix (§3.1)
- `customer/package/Definitions/global-settings.jsonc` + `policyAssignments/{management-esn-tags,management-esn-naming}.json` — regenerated demo
- `examples/contoso/package/Definitions/global-settings.jsonc` + `policyAssignments/{management-esn-tags,integration-esn-apim}.json` — regenerated fixture
- New (untracked): `.github/workflows/epac-demo.yml`, `customer/package/Output/` (do not commit)
- New (untracked): `customer/manifests/demo.input.json`, `customer/manifests/demo.manifest.jsonc` (manifest is gitignored)

---

## 6. Next steps (proposed for the follow-up session)

1. Review §3.1 builder fixes and decide: hardcoded `ownedOnly` vs manifest-driven `desiredState` (and `keepDfcSecurityAssignments`).
2. Decide the producer-side fix for §3.2 (catalogue `*.assignment.json` format) — separate producer task.
3. Add the `Output/` gitignore rule (§3.4).
4. Decide commit scope & location (customer/ vs a dedicated deploy repo/example) and commit + push to `alpha/epac-builder/demo`.
5. Run the workflow: GitHub → Actions → **EPAC deploy (demo)** → Run workflow (branch `alpha/epac-builder/demo`, `pacEnvironment=epac-dev`); approve the `epac-policy` / `epac-roles` environment gates.
   - `deploy-roles` is a **no-op** for this package (tags + naming have no DINE/Modify policies).
6. Move a subscription under the `Demo` MG to get actual compliance results (the MG is currently empty — assignments deploy but nothing is evaluated).

### Local deploy alternative (no pipeline)
```powershell
# PowerShell 7 (pwsh), Az context connected to tenant 89ee4175-…
Import-Module EnterprisePolicyAsCode -Force
Build-DeploymentPlans -PacEnvironmentSelector epac-dev `
  -DefinitionsRootFolder "<repo>\catalogue-builder\customer\package\Definitions" `
  -OutputFolder "<repo>\catalogue-builder\customer\package\Output"      # review the plan
Deploy-PolicyPlan     -PacEnvironmentSelector epac-dev `
  -DefinitionsRootFolder "<repo>\catalogue-builder\customer\package\Definitions" `
  -InputFolder "<repo>\catalogue-builder\customer\package\Output"       # applies (Audit-only)
```
