# Assembly report — contoso

- Engine version: `0.1.0`
- Catalogue version: `2026.07.25` (`sha256:980e174466a47618c518e412ce2787298b6eed73b53151e75cfeee4cc1e0fa40`)
- Manifest hash: `sha256:3afbac9fd951be744b4b7b5b645636a63c4dbb3ab087d4eb7bfb9bf176d8d163`
- Flavours: terraform
- Initiatives: 2 (1 remediating)
- Parameters bound: 6
- Exemptions: 0
- Role assignments: 2

## Groups

| Group | Initiative | Policies | Remediation |
| --- | --- | --- | --- |
| integration/essential/api-management | contoso-integration-esn-apim | 11 | yes |
| management/essential/tags | contoso-management-esn-tags | 4 | no |

## Warnings

- management/essential/tags: no managementGroup or scope set — emitted placeholder scope '/providers/Microsoft.Management/managementGroups/REPLACE-set-managementGroup-in-manifest'. Set selection.managementGroup (or selection.scope), or remove this selection; Azure will reject the placeholder at deploy.
