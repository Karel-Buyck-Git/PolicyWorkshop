# Assembly report — contoso

- Engine version: `0.1.0`
- Catalogue version: `2026.07.24` (`sha256:2a35c9768296ac43dfb91a63fd8973486570eaa757643fd683db3f84dc3eb3fb`)
- Manifest hash: `sha256:1cd3850a8768ceabb7aec8b82cdfc254ad52b670871a5152180793d536ebe5fd`
- Flavours: bicep
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
