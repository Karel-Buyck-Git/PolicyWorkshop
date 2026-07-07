# Feedback log — EPAC-builder consumer findings

Findings raised from the consumer side (onboarding dry-run against a live demo tenant).
Kept separate from `actions/backlog.md` on purpose — these are to be cross-checked and
triaged in the original engine/catalogue project (e.g. with Claude Code), not mixed into
the Claude Code backlog here.

Context: onboarded customer `vandelabr`, selection
`networking/essential/network` + `management/essential/tags` + `management/essential/naming`,
built with `assemble_scaffold.py`, then ran EPAC `Build-DeploymentPlans` (what-if) on
EnterprisePolicyAsCode 11.4.7 against demo tenant `89ee4175-19ce-415b-8c99-fb858c8782c1`.
Both findings originate in engine/catalogue code that is out of scope for the read-only
onboarding skill, so the generated package was hand-patched only to complete the what-if.

---

## Finding 1 — Renderer emits a schema shape EPAC 11.x rejects (4 gaps)

**Severity:** High — blocks real deployment without manual edits.
**Origin:** engine — `flows/epac_builder/render_json.py` (renderer output).
**Status:** Open — reproduced 2026-07-06.

The assembler produces a package that passes its **own** schema validation but fails
EPAC 11.4.7 at plan time until hand-patched. Four concrete gaps:

1. **`global-settings.jsonc` missing `desiredState`.** EPAC 11.x requires `desiredState`
   **inside each `pacEnvironment`** (not at the top level of the file). The renderer omits
   it entirely.
   - Error: `pacEnvironment epac-dev does not contain required desiredState field`.
2. **Missing `desiredState.strategy`.** Requires a value. Used `"ownedOnly"` so the plan
   won't propose deleting the tenant's pre-existing ALZ policies.
3. **Missing `desiredState.keepDfcSecurityAssignments`.** Required boolean; set to `false`.
4. **Assignments use `"policySetDefinitionName": "<name>"`.** EPAC 11.x expects
   `"definitionEntry": { "policySetName": "<name>" }`. Applies to **every** generated
   assignment file (tags, network, naming).

**Why it matters:** this is the deploy-validation gap already noted as backlog #14 — the
output validates against the project's own schema but does not round-trip through the real
EPAC engine. The proper fix belongs in `render_json.py`; patching the generated package is
not durable (every rebuild wipes the patches, as observed this session).

**Repro:** run `assemble_scaffold.py` → feed the output straight to `Build-DeploymentPlans`
on EPAC ≥ 11.4 with no manual edits → observe the 4 failures in sequence.

**Applied workaround (generated package only, not committed to engine):**
- Added `desiredState` block inside the `epac-dev` pacEnvironment with
  `strategy: "ownedOnly"` and `keepDfcSecurityAssignments: false`.
- Converted `policySetDefinitionName` → `definitionEntry.policySetName` in all 3 assignments.

---

## Finding 2 — `management/essential/naming` hardcodes `customerAbbreviation: "dlw"`

**Severity:** Medium — makes the naming initiative unusable for non-DLW customers as-is.
**Origin:** catalogue producer — `flows/definition_gen/` (baked into
`catalogue/initiatives/management/essential/naming/management-esn-naming.policyset.json`).
**Status:** Open — observed 2026-07-06.

The naming policyset exposes only one initiative-level parameter (`effect`). The customer
abbreviation is **baked to `"dlw"` per-policy** across all 169 definitions
(e.g. `"customerAbbreviation": { "value": "dlw" }`), not surfaced as an initiative parameter.

**Consequence:** for any customer other than DLW (e.g. `vandelabr`), this initiative audits
resources against the `dlw-*` naming anchor and will flag essentially everything. It cannot
be retargeted from the manifest.

**Options:**
- (a) Promote `customerAbbreviation` to an initiative parameter bound from the manifest
  (`prefix` / customer abbreviation), or
- (b) Document that naming is DLW-specific and must be regenerated per customer via
  `definition_gen`.

---

## Finding 3 — No brownfield safety: `desiredState.strategy` is never set (defaults to destructive)

**Severity:** High — risk of deleting a customer's pre-existing policy config on brownfield tenants.
**Origin:** engine — `flows/epac_builder/render_json.py` (`_write_global_settings`) + missing
manifest/config knob (no `desiredState`/`strategy` anywhere in `flows/**` or `config/**`).
**Status:** Open — analysed 2026-07-06.

The renderer's `_write_global_settings` emits only `$schema`, `pacOwnerId`, and
`pacEnvironments`. It never emits `desiredState` — no `strategy`, no `excludedScopes`. There
is also no manifest or config knob to set one (grep of `flows/**` and `config/**` for
`desiredState|strategy|ownedOnly` returns nothing). So the builder does not choose between
"only manage what I own" and "this repo is the complete desired state" — it stays silent and
defers entirely to EPAC's default.

**Consequence (version-dependent, neither outcome is safe):**
- **EPAC 11.4.x (tested):** `desiredState` is required per `pacEnvironment`. The build
  **fails closed** — `pacEnvironment epac-dev does not contain required desiredState field`.
  It cannot run until someone hand-edits `global-settings.jsonc`. Our what-if was only safe
  because the workaround chose `strategy: "ownedOnly"`.
- **EPAC versions where the field is optional:** the historical default is `strategy: full`.
  `full` treats the repo as the complete desired state and will **delete** in-scope policy
  assignments/definitions found in Azure that are not in the repo — including resources this
  EPAC instance does not own (no `pacOwnerId`, or a different owner). On a brownfield tenant
  that means the customer's pre-existing ALZ / hand-made policy config at or below the
  deployment root scope is proposed for **deletion**.

**Notes:**
- The `Audit` effect posture does **not** mitigate this. Strategy governs the assignment/
  definition lifecycle (create/update/delete) and is orthogonal to policy effect.
- A consumer currently has **no supported way** to declare "this is brownfield, only manage
  what I own." They must hand-edit `global-settings.jsonc` after every build, and the edit is
  wiped on each rebuild (same durability problem as Finding 1).

**Recommended fix:**
- Emit `desiredState` from the renderer with a **safe default of `strategy: "ownedOnly"`**.
- Surface `strategy` (and optionally `excludedScopes`) as a manifest field so greenfield
  customers can opt into `full` deliberately, while brownfield stays safe by default.

---

## What-if result (reference, all 3 initiatives, nothing deployed)

| Change type            | Count                                                         |
| ---------------------- | ------------------------------------------------------------ |
| Policy definitions     | 169 new (all from naming)                                    |
| Policy set definitions | 3 new (naming, tags, network)                                |
| Policy assignments     | 3 new                                                        |
| Role assignments       | 2 additions (Network Contributor + Contributor, networking DINE identity) |

`ownedOnly` held — zero deletions of existing tenant policies. Plans written to
`customer/package/Output/plans-epac-dev/`.
