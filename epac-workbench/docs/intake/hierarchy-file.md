# The management-group hierarchy file

The manifest points `source.managementGroups` at a design file, and the assembler resolves
each `selection[].managementGroup` **name** to a real Azure scope id through it. Without
it you must write raw scope ids into every selection.

Loaded by `engine/epac_builder/mgscopes.py::load_mg_index`, which delegates to the
self-contained svg-gen tool — so **the same file** that targets your selections also
renders the diagram shipped in the package's `docs/`.

## The shape

Canonical JSON is a tree of `{name, kind, scopeId, children}`:

```json
{
  "name": "Tenant Root Group",
  "kind": "mg",
  "scopeId": "/providers/Microsoft.Management/managementGroups/<tenant-guid>",
  "children": [
    {
      "name": "mg-lv1-platform",
      "kind": "mg",
      "scopeId": "/providers/Microsoft.Management/managementGroups/mg-lv1-platform",
      "children": [
        {
          "name": "sub-hub-prod",
          "kind": "sub",
          "scopeId": "/subscriptions/00000000-0000-0000-0000-000000000000"
        }
      ]
    }
  ]
}
```

- `kind` is `mg` or `sub`.
- **`scopeId` is what matters.** `load_mg_index` walks the tree and indexes *only* nodes
  that carry one; a node without a `scopeId` is structure, not a target.
- `name` is what the manifest selects on. Matching is case-insensitive, so
  `"managementGroup": "MG-LV2-Integration"` finds `mg-lv2-integration`.
- A name the hierarchy does not contain is a **hard error** listing what is available —
  never a silent skip.

Worked example: [`examples/contoso/designs/contoso-mgmt-groups.json`](../../examples/contoso/designs/contoso-mgmt-groups.json).

## Converting the `az` output

`az account management-group show --expand --recurse` returns a different shape
(`displayName`, `type`, `id`, `children`). Convert it:

```python
# python convert.py mg-tree.raw.json > designs/<customer>-mgmt-groups.json
import json, sys

def node(n):
    kind = "sub" if str(n.get("type", "")).endswith("subscriptions") else "mg"
    out = {"name": n.get("displayName") or n["name"], "kind": kind, "scopeId": n["id"]}
    kids = [node(c) for c in (n.get("children") or [])]
    if kids:
        out["children"] = kids
    return out

json.dump(node(json.load(open(sys.argv[1], encoding="utf-8"))),
          sys.stdout, indent=2, ensure_ascii=False)
```

Then **read it**. The conversion is mechanical; whether the tree is the one you want to
govern is a judgement call, and it is much cheaper to catch here than in a plan run.

> Other input formats are accepted (`indent`, `edges`, `csv`, `xlsx`) — see
> [`engine/tools/svg-gen/management-groups/README.md`](../../engine/tools/svg-gen/management-groups/README.md).
> The indent format is quicker to hand-write when you are sketching a target hierarchy
> rather than capturing an existing one.

## Rendering the diagram

```bash
cd epac-workbench
python engine/tools/svg-gen/management-groups/generate_svg.py --input customer/designs/<customer>-mgmt-groups.json
```

The packaging step copies a `<customer>-mgmt-groups.*.svg` from the manifest's `designs/`
folder into the package's `docs/`, so the customer receives the picture of the hierarchy
their policy was scoped to. If no matching SVG is found the build says so and carries on —
watch for that line, it means the package ships without the diagram.

## Checks worth doing before you build

- [ ] Every `scopeId` is a full resource id (`/providers/Microsoft.Management/managementGroups/…`
      or `/subscriptions/…`)
- [ ] The `deploymentRootScope` from the intake sheet appears in this tree
- [ ] The dev root is a **separate branch**, not nested under the prod root
- [ ] Every name used in `selection[].managementGroup` exists here — otherwise the build
      fails with the list of available names, which is the fast way to check
