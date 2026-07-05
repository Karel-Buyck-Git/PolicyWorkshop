# `customer/designs/` — your management-group design

Put your customer's management-group hierarchy here. The manifest points at it via
`source.managementGroups` (e.g. `../designs/<customer>-mgmt-groups.json`), and the assembler
resolves each `selection.managementGroup` **name** to a scope id from this file.

Expected files (this folder starts empty — you add them):

| File | Role |
| ---- | ---- |
| `<customer>-mgmt-groups.json` | the hierarchy (scope ids + names). **Required** if any selection sets `managementGroup`. |
| `<customer>-mgmt-groups.rich.svg` | optional diagram. If present, the assembler copies it verbatim into `package/docs/` and links it from the package README. |

`package.py` locates this folder as the manifest's `parents[1]/designs` and picks the SVG by
the manifest's `customer` field (`<customer>-mgmt-groups.*.svg`), so keep the names aligned
with `customer`.

Generate the SVG from a spreadsheet/JSON with the svg-gen tool — see
`flows/tools/svg-gen/management-groups/README.md`.

For a filled example, see [`../../examples/contoso/designs/`](../../examples/contoso/designs/).
