# Assembly report — contoso

- Catalogue version: `2026.06.21`
- Manifest hash: `sha256:b712285c6454595185d466f30aa56279d10b0fbfe4f5deeff13fda554ce4d617`
- Flavours: json
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
