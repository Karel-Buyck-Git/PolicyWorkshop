# epac-claude-03 — hydration-style EPAC scaffold

A pre-built EPAC repository that mimics the output of `Install-HydrationEpac`, so you can fill
in placeholders and deploy quickly instead of running the interactive installer.

See **IMPLEMENTATION-PLAN.md** for the phased rollout and the CAFv3 management-group model.

## Structure

```
epac-claude-03/
├── IMPLEMENTATION-PLAN.md
├── README.md
├── .gitignore
├── Definitions/
│   ├── global-settings.jsonc                 # tenant01 + epac-dev environments
│   ├── policyDefinitions/
│   │   ├── Security/    deny-public-ip.json, require-tag-owner.json
│   │   ├── Networking/  restrict-nsg-rules.json
│   │   └── Monitoring/  deploy-diagnostic-settings.json  (DINE)
│   ├── policySetDefinitions/
│   │   ├── Security/    security-baseline-initiative.json
│   │   └── Governance/  tagging-initiative.json
│   ├── policyAssignments/
│   │   ├── Security/    compliance-frameworks.jsonc (MCSB + NIST), pci-dss.jsonc (stub), security-baseline.jsonc
│   │   └── Governance/  allowed-locations.jsonc, tagging.jsonc
│   ├── policyExemptions/
│   │   ├── epac-dev/    exemptions.jsonc (empty)
│   │   └── tenant01/    exemptions.jsonc (sample waiver)
│   └── policyStructures/   (optional: Defender for Cloud / docs)
├── Output/                 # generated plans (git-ignored)
└── pipelines/
    ├── AzureDevOps/        azure-pipelines.yml
    └── GitHubActions/      epac-dev-ci.yml, epac-tenant-cd.yml
```

## Mimics these hydration choices

- Two EPAC environments: `tenant01` (main) and isolated `epac-dev`.
- CAFv3 management-group scopes (`contoso` + platform/landingzones/decommissioned/sandbox; dev copy `epac-dev-contoso`).
- **MCSB always assigned** at root; **NIST 800-53 R5** included (Audit). **PCI-DSS** provided as a disabled stub.
- Governance starters (allowed locations with sandbox excluded, tag governance).
- Custom policy examples + a custom security initiative.
- StarterKit-style CI/CD for both platforms.

## Quick start

1. Edit `Definitions/global-settings.jsonc`: `pacOwnerId` (GUID), `tenantId`, the two `deploymentRootScope`s, `managedIdentityLocation`.
2. Replace remaining `REPLACE-` tokens: MG IDs in assignment files, Log Analytics workspace IDs in `security-baseline.jsonc`, subscription ID in `policyExemptions/tenant01/exemptions.jsonc`. Replace the PCI-DSS policy set ID only if you want to enable it.
3. Ensure the management groups exist (or run the real Hydration Kit to build the `epac-dev` copy).
4. Deploy to dev, review, then promote:

```powershell
Install-Module EnterprisePolicyAsCode -Scope CurrentUser
Connect-AzAccount -Tenant <tenantId>

Build-DeploymentPlans -PacEnvironmentSelector "epac-dev" -DefinitionsRootFolder ./Definitions -OutputFolder ./Output
Deploy-PolicyPlan     -PacEnvironmentSelector "epac-dev" -DefinitionsRootFolder ./Definitions -InputFolder ./Output
Deploy-RolesPlan      -PacEnvironmentSelector "epac-dev" -DefinitionsRootFolder ./Definitions -InputFolder ./Output

# then tenant01 (gate behind approval in CI/CD)
Build-DeploymentPlans -PacEnvironmentSelector "tenant01" -DefinitionsRootFolder ./Definitions -OutputFolder ./Output
Deploy-PolicyPlan     -PacEnvironmentSelector "tenant01" -DefinitionsRootFolder ./Definitions -InputFolder ./Output
Deploy-RolesPlan      -PacEnvironmentSelector "tenant01" -DefinitionsRootFolder ./Definitions -InputFolder ./Output
```

## CI/CD

- **Azure DevOps:** `pipelines/AzureDevOps/azure-pipelines.yml` — create the WIF service connections and `epac-dev` / `tenant01` Environments (approvals on tenant01).
- **GitHub Actions:** copy the two files from `pipelines/GitHubActions/` into `.github/workflows/`. Configure OIDC app registrations and the secrets/environments referenced in each file.

## Caveats

- The DINE template (`deploy-diagnostic-settings`) is illustrative — validate API version and log categories.
- Built-in IDs for MCSB, NIST, Allowed Locations and tag inheritance are well-known and stable; the PCI-DSS ID is intentionally a placeholder.
- `Build-DeploymentPlans` against `epac-dev` is the real validation. EPAC is desired-state and will delete out-of-band policy in its root scope — review every plan.
