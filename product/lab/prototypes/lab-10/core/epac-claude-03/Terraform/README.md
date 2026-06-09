# Terraform — Azure Policy governance (parity with the EPAC/JSON scaffold)

Implements the same governance as `../Json` (EPAC), but natively in Terraform with the
`azurerm` provider. Same custom policies, initiatives, compliance frameworks, assignments and
exemptions; driven per environment via tfvars.

## Layout

```
Terraform/
├── providers.tf            # azurerm provider + backend stub
├── variables.tf            # inputs + well-known built-in ids (locals)
├── policy_definitions.tf   # 4 custom policies (rules in policies/*.json)
├── policy_set_definitions.tf  # security-baseline + tagging initiatives
├── policy_assignments.tf   # MCSB (+NIST/+PCI), custom baseline, allowed-locations, tagging + role assignments
├── policy_exemptions.tf    # sample sandbox waiver (gated)
├── outputs.tf
├── policies/               # policyRule JSON for each custom policy
├── environments/
│   ├── epac-dev.tfvars
│   └── tenant01.tfvars
└── pipelines/
    ├── AzureDevOps/azure-pipelines.yml
    └── GitHubActions/terraform-cd.yml
```

## Mapping to the EPAC scaffold

| EPAC concept | Terraform equivalent |
|---|---|
| pacEnvironment / deploymentRootScope | a tfvars file + `management_group_id` |
| policyDefinitions/* | `azurerm_policy_definition` |
| policySetDefinitions/* | `azurerm_policy_set_definition` |
| policyAssignments/* | `azurerm_management_group_policy_assignment` |
| policyExemptions/* | `azurerm_management_group_policy_exemption` |
| EPAC auto role assignments | explicit `azurerm_role_assignment` (you maintain them) |
| Build/Deploy plans | `terraform plan` / `terraform apply` |

## Run

```bash
cd Terraform
az login --tenant <tenantId>            # or set ARM_* / OIDC
terraform init

# dev first
terraform plan  -var-file=environments/epac-dev.tfvars -out tfplan
terraform apply tfplan

# then tenant01 (gate behind approval in CI/CD)
terraform plan  -var-file=environments/tenant01.tfvars -out tfplan
terraform apply tfplan
```

Use a **separate state** per environment (separate backend key or workspace) — the two
environments target different management groups.

## Edit before running

- `management_group_id`, `sandbox_management_group_id` per tfvars
- `log_analytics_workspace_id` per tfvars
- `enable_pci` + `pci_policy_set_id` if enabling PCI
- provider auth via `az login` or `ARM_*` env vars

## Caveats vs EPAC

- **Role assignments are not auto-calculated.** This scaffold assigns roles for the custom DINE
  and the tagging Modify. MCSB/NIST contain many DINE/AINE policies; assign their required roles
  to the assignment identities when you move from Audit to remediation.
- Terraform owns only what's in state; it does **not** delete out-of-band policy the way EPAC's
  desired-state engine does.
- The DINE diagnostic template is illustrative — validate apiVersion/log categories.
