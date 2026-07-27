# Assembly report — contoso

- Engine version: `0.1.0`
- Catalogue version: `2026.07.26` (`sha256:c06199a7a410fc97f0a8f5d1da9db5bc30a631c70aade7a779d7c3d5daef3d5c`)
- Manifest hash: `sha256:3a18fc9e703efcaff6cefb15083608b66003e4d008d50f68a54001c205b499ac`
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
