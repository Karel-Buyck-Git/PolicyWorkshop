# Assembly report — contoso

- Engine version: `0.2.0`
- Catalogue version: `2026.07.28` (`sha256:7dc8f59ff7e10968d9aea5e1c24030a9ceaa0d7cf3e6220b39905747a2b061f3`)
- Manifest hash: `sha256:4e5b05decc72caca26f17e9f257b9ece72329adff1668ad88000f390f491aef6`
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
