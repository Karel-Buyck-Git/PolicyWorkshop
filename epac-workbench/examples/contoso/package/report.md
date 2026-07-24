# Assembly report — contoso

- Engine version: `0.1.0`
- Catalogue version: `2026.07.18` (`sha256:60384fdf0750880b3f77943b12d6a39c693338276a3215201c3975dff8f7ffe4`)
- Manifest hash: `sha256:f772c3c51ebd26c98982ea5d7d879d1701a5437a1b333f03754f007616045be2`
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
