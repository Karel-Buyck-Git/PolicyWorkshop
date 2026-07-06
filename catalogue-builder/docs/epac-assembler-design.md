# The Assembler — Catalogue Consumer (design)

The assembler is a **standalone consumer of the catalogue**, not a fourth phase of the taxonomy
pipeline. Phases 1–3 are a *producer* that builds the shared catalogue (run occasionally — when
Microsoft's built-ins or the taxonomy change). The assembler is a *consumer* that turns a
**customer manifest** + the catalogue into a deployable `Definitions` scaffold, rendered in one or
more IaC flavours (EPAC/JSON, Terraform, Bicep). A customer build needs only a **published
catalogue** — it does NOT re-run phases 1–3.

```
PRODUCER (occasional)                          CONSUMER (per customer, on demand)
extract → enrich → create-initiatives  ──►  catalogue@version  ──►  input → EXPAND → ASSEMBLE → validate → PR → deploy
```

The two systems are joined by a single contract: the **catalogue** (its files + `catalogueVersion`).
The assembler is a **pure, deterministic transform**: same manifest + same catalogue snapshot ⇒
byte-identical output. No Azure calls, no deployment, no taxonomy derivation.

---

## 1. Consumers & invocation

The manifest is authored by a human SE **or** emitted by the upstream app. The assembler is
run locally or in CI:

```
python flows/epac_builder/assemble_scaffold.py --manifest examples/contoso/manifests/manifest.example.jsonc
# optional: --only json|terraform|bicep   --check (validate, write nothing)   --strict (pre-deploy gate: fail on any surviving <REPLACE:>/placeholder scope)   --out <dir> (default: the manifest's output.root — customer/package/ for a real customer manifest, examples/contoso/package/ for the worked example)
```

Chain: `app / human → manifest → assembler → Definitions scaffold (×flavour) → CI validate → deploy`.

---

## 2. Inputs & dependencies

| Input | Role | Required |
|---|---|---|
| `input.example.json` | minimal human input: customer + selection + value-only `parameters` | yes (expand stage) |
| `--manifest` | the expanded customer contract (selection, scopes, bindings, exemptions) | yes (assemble stage) |
| `catalogue/index.json` | group list + `domainMap`; validate selection, expand `category:"*"` | yes |
| `catalogue/catalogue.json` | catalogue version + content fingerprint (pin / verify) | yes |
| `catalogue/initiatives/<domain>/<tier>/<category>/` | generated groups (`.policyset.json`, `.assignment.json`, `.exemptions.json`, `.roles.json`, `.md`) | yes |
| `catalogue/definitions/<category>/policies.md` | lineage + effect lookups | optional |

**Runtime:** Python ≥ 3.10, **stdlib only — no `pip install`**. Schema validation and JSONC parsing
are hand-rolled (`epac_builder/validate.py`, `epac_builder/jsonc.py`) rather than pulled from
`jsonschema` / `json5`, to match the producer's zero-dependency house style.

**Validation contract (three schemas, two states):**

| Schema | Stage | Enforces |
|---|---|---|
| `input.schema.json` | human input | top level closed; `selection` format; `parameters` value-only (no objects) |
| `manifest.input.schema.json` | manifest editing | structure lock (`additionalProperties:false` everywhere); placeholders allowed |
| `manifest.schema.json` | build gate | strict values — GUIDs, enums, scopes, required params filled |

All are JSON Schema 2020-12. "input" state allows `<REPLACE: …>` placeholders and value-only
edits; the "resolved" state (strict) must pass before any rendering.

### Catalogue contract & versioning

The catalogue is the only thing the assembler depends on — it is self-describing:

- **`index.json`** — the group list plus `domainMap` (category → domain), projected from the ONE
  authored hierarchy (`config/azure-domain-hierachy.md`) at build time. Selection validation and
  `category:"*"` expansion read this, never the markdown, so the consumer has no `config/` or
  `docs/` dependency.
- **`catalogue.json`** — the version stamp: a human `catalogueVersion` label, `generatedAt`,
  `inputs` (built-ins git ref, hierarchy hash, tier-rules hash), `counts`, `tools`, and a
  `contentHash` fingerprint over every catalogue file. The manifest pins `source.catalogueVersion`;
  the assembler verifies it matches and can recompute `contentHash` to detect drift.
- **Baked remediation roles** — each group containing a DeployIfNotExists/Modify member carries its
  required `roleDefinitionIds` in the policyset `metadata` and a `<name>.roles.json` sidecar,
  precomputed by phase 3 from the policy repo. The Terraform/Bicep renderers read these; the
  assembler never touches the policy repo.

Single-source guarantee: one authored hierarchy → one parser (`flows/shared/hierarchy.py`) → one generated
`index.json`. The markdown is the source; `index.json` is a derived projection, never hand-edited.

---

## 3. pacOwnerId (gap closed)

EPAC stamps `pacOwnerId` into resource metadata to know what it owns. It is **per EPAC
instance / per customer**, not per environment, and must never change once policy is deployed.

Resolution rule:

1. If `pacOwnerId` is present in the manifest → use it.
2. If absent → the assembler generates a GUID, **writes it back into the manifest**, and logs
   that it did so. This guarantees the next run is reproducible and the customer keeps a stable id.

The value flows into the synthesized `global-settings.jsonc` (JSON flavour) and into resource
`metadata`/tags for the Terraform and Bicep flavours.

---

## 4. Canonical IR (the flavour-neutral model)

All three renderers consume one in-memory model. Building it once is what keeps the flavours
consistent.

```jsonc
{
  "identity":     { "pacOwnerId": "…", "prefix": "contoso", "customer": "contoso" },
  "environments": [ { "selector": "tenant01", "tenantId": "…",
                      "rootScope": "/providers/.../contoso",
                      "managedIdentityLocation": "westeurope",
                      "enforcement": "hardened",
                      "logAnalyticsWorkspaceId": "…",
                      "notScopes": ["…"] } ],
  "initiatives":  [ { "name": "contoso-security-essential-key-vault",
                      "source": "catalogue/initiatives/security/essential/key-vault/…policyset.json",
                      "policyset": { /* the loaded .policyset.json, re-prefixed */ },
                      "hasRemediation": true,
                      "roleDefinitionIds": ["/providers/.../roleDefinitions/…"] } ],  // baked in catalogue
  "assignments":  [ { "initiative": "contoso-security-essential-key-vault",
                      "boundParameters": { "certificates…": 90 },
                      "scopes":   { "tenant01": ["/providers/.../contoso"] },
                      "notScopes":{ "tenant01": ["/providers/.../contoso-sandbox"] },
                      "effectPosture": "hardened",
                      "effectOverrides": [ { "ref": "d8cf8476…", "effect": "Audit" } ],
                      "managedIdentity": { "required": true, "location": "westeurope" } } ],
  "roleAssignments": [ { "assignment": "…", "roleDefinitionId": "…", "scope": "…" } ],
  "exemptions":   [ { "selector": "tenant01", "name": "sandbox-kv-waiver", "…": "…" } ],
  "lineage":      { "manifestHash": "…", "catalogueVersion": "…", "groups": [ … ] }
}
```

Each renderer is a pure function `IR → files`. Adding a fourth flavour = one new renderer.

---

## 5. Algorithm (step pseudocode)

```text
expand_input_to_manifest(input):                 # input.example.json -> <customer>.manifest.jsonc
    data = parse_json(input_path)
    jsonschema.validate(data, input.schema.json)        # FAIL FAST (structure/value-only)
    groups = resolve_selection(data)                    # see below
    required = union(required_params(g) for g in groups)# from each group's .assignment.json
    seed parameters{} / bindings.defaults{} with one <REPLACE: k> per required param k
    emit <customer>.manifest.jsonc (fixed shape, placeholders); structure-locked by
    manifest.input.schema.json. Humans then fill VALUES only.

load_and_validate(manifest):
    data = parse_jsonc(manifest_path)   # strip // and /* */ comments + trailing commas
    jsonschema.validate(data, manifest.input.schema.json)   # structure lock (editing)
    jsonschema.validate(data, manifest.schema.json)         # strict build gate — FAIL FAST
    resolve_pac_owner_id(data, manifest_path)               # see §3

resolve_selection(data):
    index = load(catalogue/index.json)                       # groups + domainMap (no config/ or docs/)
    groups = []
    for sel in data.selection:
        assert sel.domain in index.domains                   # else hard error
        cats = index.categories(sel.domain) if sel.category == "*" else [sel.category]
        tiers = rollup(sel.tier)        # essential⊆professional⊆enterprise
        for cat in cats:
            for tier in tiers:
                g = "catalogue/initiatives/%s/%s/%s" % (sel.domain, tier, cat)
                if exists(g): groups.append(load_group(g, sel))   # else error or warn(undefined)
    return dedup(groups)

bind_parameters(group, data.bindings):
    assignment = load(group.assignment_json)
    values = merge(bindings.defaults, bindings.overrides["%s/%s" % (domain, category)])
    for p, v in assignment.parameters:
        if v is "<REPLACE: …>":
            if p not in values: ERROR("unbound required parameter %s" % p)   # FAIL FAST
            v = values[p]
        typecheck(v, group.policyset.parameters[p])          # type/allowedValues
    return bound_assignment

apply_posture(group, env):
    posture = sel.enforcement or env.enforcement
    if posture == "Audit":   soften all member effects → Audit (EPAC override / TF/Bicep param)
    if posture == "hardened":keep baked effects (Deny/DINE/Modify)
    apply data.effectOverrides matching this group   # surgical
    if group has Modify/DINE: mark managedIdentity.required, attach role needs

build_ir(...):  assemble identity, environments, initiatives, assignments,
                roleAssignments, exemptions, lineage

render(ir, flavour):
    json:      copy re-prefixed .policyset → policySetDefinitions/
               write bound assignment      → policyAssignments/
               synthesize global-settings.jsonc (from environments + pacOwnerId)
               write exemptions per selector → policyExemptions/<selector>/
    terraform: emit azurerm_policy_set_definition / _management_group_policy_assignment /
               _exemption (+ azurerm_role_assignment), per-env tfvars
    bicep:     emit MG-scoped modules + per-env parameter files (+ roleAssignments)

report(ir):  write lineage.json + coverage/validation summary
             if --check or CI: run terraform validate / az bicep build / EPAC schema check
```

---

## 6. Validations (all fail-fast, before any file is written)

1. Input conforms to `input.schema.json`; manifest conforms to `manifest.input.schema.json` (structure) then `manifest.schema.json` (strict values).
2. Every `selection.domain` / `category` exists in the hierarchy (`category:"*"` expands).
3. Every resolved `(domain,tier,category)` group exists under `catalogue/initiatives/`.
4. Every required `<REPLACE: …>` parameter has a binding; values type-check against the policyset schema.
5. Each `environments[].selector` referenced by `scope`/`notScopes`/`exemptions` is declared.
6. `effectOverrides[].policyDefinitionReferenceId` exists in the named group.
7. `Waiver` exemptions have `expiresOn`; scopes are well-formed resource ids.
8. `pacOwnerId` is a valid GUID (or generated).

---

## 7. Outputs

Each selected flavour is rendered as a **self-contained, deployable package** (IaC content +
GitHub Actions pipeline + `docs/` hierarchy diagram + deploy `README.md` + `lineage.json` +
`report.md`). **One** flavour renders FLAT at `output.root`; **several** render one sub-folder
per flavour (`json` → `epac`):

```
customer/package/                    # = output.root  (per-customer; default)

# one flavour (e.g. json) -> FLAT:
├── Definitions/   global-settings.jsonc, policySetDefinitions/, policyAssignments/, policyExemptions/<selector>/
├── .github/workflows/epac.yml       # plan -> deploy-policy -> deploy-roles
├── docs/<customer>-mgmt-groups.*.svg
└── README.md  lineage.json  report.md

# several flavours -> one full package per flavour:
customer/package/{epac, terraform, bicep}/
```

**Input vs output:** the assembler READS the shared `catalogue/` and WRITES the customer's own
`customer/package/` (the `output.root`). Catalogue is never modified. Paths in `source.*` and
`output.root` are resolved **relative to the manifest file**, so `../../catalogue/initiatives`
(read) and `../package` (write) both resolve from `customer/manifests/`.

Determinism: stable key ordering and sorted iteration so re-runs produce clean diffs.

---

## 8. Boundaries (explicitly out of scope)

- No deployment, no live Azure calls, no remediation execution.
- No taxonomy derivation — that is Phases 1–3.
- No invention of policy content — only selection, binding, and rendering of existing groups.
- Remediation role IDs for TF/Bicep are read from the catalogue (baked by phase 3), so the
  assembler needs no policy-repo access. EPAC still computes its own at deploy time and remains
  the most complete for desired-state deletion.

---

## 9. Open items to confirm before coding

- `category: "*"` on a domain with no groups at the chosen tier → warn-and-skip, or error?
- `undefined` domain handling — exclude by default, or require explicit opt-in?
- Whether the TF/Bicep flavours should attempt role-assignment derivation now or defer (Audit-first).
- Output location convention (`generated/<customer>/<flavour>` vs a top-level `generated/` root).

---

## 10. Human input file & `parameters`

The human surface is intentionally tiny: `customer/manifests/input.example.json` holds only
`customer`, `selection` (a string array of `domain/tier/category`), and `parameters`.

```json
{
  "customer": "contoso",
  "selection": [
    "integration/essential/api-management",
    "management/essential/tags"
  ],
  "parameters": {}
}
```

**`parameters`** is a flat, value-only map. Its keys are **generated from the
selection** — one key per required parameter exposed by the selected initiatives'
`.assignment.json` files (e.g. `management/essential/tags` contributes 6 keys;
`integration/essential/api-management` contributes 0). Humans fill the values; they
never add, rename, or remove keys. Kept empty here until the selection is resolved.

### Governance (`input.schema.json`)

The input file is governed by `customer/manifests/input.schema.json`:

- top level is **closed** (`additionalProperties:false`) — no foreign keys;
- `selection` items must match `domain/tier/category` (`category` may be `*`);
- `parameters` values are restricted to scalars or arrays — **objects are rejected**,
  so no structural nesting can be smuggled in.

This enforces the value-only rule at the input stage, mirroring how
`manifest.input.schema.json` enforces it on the expanded manifest.

### Mapping into the manifest

The assembler maps the input into the expanded manifest:

| input key | manifest target |
|---|---|
| `customer` | `customer` |
| `selection[]` (`domain/tier/category`) | `selection[]` objects + group resolution |
| `parameters{}` | `bindings.defaults{}` |

So `parameters` is the human-facing form of `bindings.defaults`: the assembler
seeds it with one placeholder per required parameter, the human fills values, and
the resolved values flow into `bindings.defaults` before the strict build gate.
