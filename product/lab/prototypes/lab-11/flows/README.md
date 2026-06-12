# `flows/` — the EPAC scaffold generator

This folder holds the **producer pipeline**: the scripts that turn Azure's
built-in policy definitions into a versioned, customer-facing **catalogue**.

The end-to-end design is drawn in
[`../docs/epac-scaffold-generator-flow.svg`](../docs/epac-scaffold-generator-flow.svg).
It has two halves joined by one contract (the catalogue):

- **Producer** (this folder, runs *occasionally* — when Microsoft's built-ins or
  the taxonomy change): `extract → enrich → create-initiatives → catalogue@version`.
- **Consumer** (the *assembler*, runs *per customer, on demand*): expands a
  customer manifest against the catalogue and renders EPAC/JSON, Terraform and
  Bicep scaffolds. **Not built yet** — see the placeholder at the bottom.

```
PRODUCER — taxonomy pipeline (this folder)          CATALOGUE @version (the contract)
                                                     ┌─────────────────────────────────┐
  Azure built-in policies ┐                          │ catalogue.json  version·hash     │
                          ├─► ① extract ─► ② enrich ─►③ create-initiatives ─►          │
  config/ hierarchy ──────┘     dedup ·      validate    group · bake roles  │ index.json     groups·domainMap │
                                first-pass    tier ·     · stamp version      │ initiatives/<domain>/<tier>/<cat>/ │
                                tier          rationale                       │ definitions/   policies.md       │
                                                                             └─────────────────────────────────┘
                                                                                          │
CONSUMER — assembler (per customer, on demand)  ◄──────────────────────────────────────── ┘
  input.json ─► EXPAND ─► manifest ─► Resolve+Bind ─► Canonical IR ─► render {EPAC/JSON · Terraform · Bicep}
                                                                          └─► customer/initiatives/ ─► Validate ─► PR ─► Deploy
            ░░░  TO BE BUILT — see § "Phase 4 — the assembler"  ░░░
```

---

## At a glance

| File | Role | Used in catalogue build? | Used by client/consumer? |
|---|---|---|---|
| [`extract_policies.py`](extract_policies.py) | **Producer step ①** — extract + dedup | ✅ yes | — |
| [`enrich_policies.py`](enrich_policies.py) | **Producer step ②** — validate tier + rationale | ✅ yes | — |
| [`create_initiatives.py`](create_initiatives.py) | **Producer step ③** — group + bake + stamp | ✅ yes | — |
| [`paths.py`](paths.py) | **Shared module** — canonical paths | ✅ (imported) | — |
| [`hierarchy.py`](hierarchy.py) | **Shared module** — the ONE hierarchy parser | ✅ (imported) | — |
| [`tiers.py`](tiers.py) | **Shared module** — the ONE tier engine (parses `tier-rules.yaml`) | ✅ (imported) | — |
| [`ab_verify.py`](ab_verify.py) | **Tool** — A/B regression / diff check | ❌ no | ❌ no |
| [`catalogue_diff.py`](catalogue_diff.py) | **Tool** — catalogue drift / diff report | ❌ no | ❌ no |
| `assemble_scaffold.py` | **Consumer (Phase 4)** — *not built yet* | — | ✅ (the consumer) |

---

## Naming convention (governance)

All scripts in this folder are **snake_case** so every file is a valid Python
module name and can be imported as well as run. The rule is keyed on what the
file *is*, not how it happens to be invoked:

| Kind | Convention | Imported? | Examples |
|---|---|---|---|
| **Pipeline entry points** (the producer steps) | `snake_case`, `verb_noun.py` | runnable *and* importable | `extract_policies.py`, `enrich_policies.py`, `create_initiatives.py` |
| **Shared library modules** | `snake_case`, `noun.py` | yes | `paths.py`, `hierarchy.py` |
| **Dev / validation tools** | `snake_case`, `verb_noun.py` | runnable | `ab_verify.py`, `catalogue_diff.py` |
| **Consumer entry point** (Phase 4) | `snake_case`, `verb_noun.py` | runnable | `assemble_scaffold.py` *(planned)* |

Rules:

1. **No hyphens.** A hyphen makes a file impossible to `import` (Python reads `-`
   as minus), which is what forced `ab_verify.py` to copy-and-subprocess the
   generator instead of importing it. snake_case keeps every file importable.
2. **No leading underscore** unless the module is genuinely *private* (an
   implementation detail that must never be imported from outside this folder).
   Shared helpers that siblings import — `paths.py`, `hierarchy.py` — are part of
   the internal API and do **not** get a `_` prefix. (This is why `_paths.py` was
   renamed to `paths.py`: it was the same kind of module as `hierarchy.py` but
   was wearing a `_` the other one wasn't — inconsistent.)
3. **Pipeline steps read as `verb_noun`** (`extract_policies`); **modules read as
   `noun`** (`hierarchy`); **tools read as `verb_noun`** (`catalogue_diff`).

> The *conceptual* pipeline steps are still written `extract → enrich →
> create-initiatives` in prose/diagrams; that's a step label, not a filename. Only
> the files are snake_case.

---

## Producer — the catalogue pipeline (3 steps)

Run from this folder, in order. Each step is idempotent; defaults target this lab
(via [`paths.py`](paths.py)), so no flags are needed for a normal run.

### ① [`extract_policies.py`](extract_policies.py)
**Reads** the official built-in policy JSON (`--source`, default the shared
`Official Azure Policy` repo) and **writes** one `policies.md` table per Azure
resource category to `catalogue/definitions/<category>/`.

- Extracts key fields (display name, GUID, effect allowed/soft/hardened, version, …).
- Drops `[Deprecated]` policies; **deduplicates** by Policy ID keeping the highest
  version (semver-aware, pre-release loses to GA).
- Looks up each category's **Domain** from the authored hierarchy (via
  [`hierarchy.py`](hierarchy.py)); no match → `undefined`.
- Assigns a **first-pass Tier** via the shared engine ([`tiers.py`](tiers.py));
  step ② re-runs the same engine as the authoritative pass.
- `--jsonl` mode emits a flat extraction instead (no tier, for agent consumption).

### ② [`enrich_policies.py`](enrich_policies.py)
**Re-reads** every `policies.md`, **corrects the Tier**, adds a rationale, and
rewrites the file. This is the canonical Phase 2 mechanism; the tier rules it
applies live in the authored [`config/tier-rules.yaml`](../config/tier-rules.yaml)
(parsed by [`tiers.py`](tiers.py)), which is hashed into `catalogue.json` as
`tierRulesHash`.

- Tier rules (authored in `tier-rules.yaml`): Defender/threat/vulnerability →
  **Professional**; private endpoint/link → **Enterprise**;
  zone-redundancy/availability-zone → **Enterprise**;
  diagnostic-pipeline/CMK/regulatory → **Enterprise**; backup/resiliency →
  **Essential**. Edit the YAML to change the tiering — no code change needed.
- Generates a `## Tier rationale` section (theme-aware, per resource), with
  compliance-framework references (NIS2 / ISO 27001 / CIS / NIST).
- Re-sorts rows by (tier, name). Idempotent: same input ⇒ same output.

### ③ [`create_initiatives.py`](create_initiatives.py)
**Reads** all enriched `policies.md`, joins each policy (on Policy ID) against a
parameter index built from the policy repo, **groups** rows by
`(Domain, Tier, Category)` — tiers are *exclusive* here — and writes up to five
EPAC-ready artifacts per group under
`catalogue/initiatives/<domain>/<tier>/<category>/`:

| Artifact | Contents |
|---|---|
| `.md` | tier rationale + a `## Usage` deployment guide + the full policy table |
| `.policyset.json` | EPAC `policySetDefinition`; hardened effects baked, required params bubbled up |
| `.assignment.json` | EPAC assignment scaffold with mock tenant references |
| `.exemptions.json` | EPAC exemptions template stub |
| `.roles.json` | *only* for Modify/DeployIfNotExists groups: deduped remediation `roleDefinitionIds` |

> Generated in one pass: each EPAC-native JSON (`.policyset`/`.assignment`/`.exemptions`) is stamped with a `$schema` reference as its first key, and each `.md` gets a `## Usage` deployment guide (between the rationale and the policy table) — no separate post-processing step.

Finally writes the two catalogue manifests at the catalogue root — **`index.json`**
(groups + `domainMap` + tiers) and **`catalogue.json`** (the version stamp:
`catalogueVersion`, `generatedAt`, `inputs`, `counts`, `tools`, `contentHash`).
These two files plus the `initiatives/` and `definitions/` folders are the
**catalogue contract** the consumer depends on.

---

## Shared modules (imported by the pipeline, not run directly)

### [`paths.py`](paths.py)
Single source of truth for lab paths (`CATALOGUE_DIR`, `DEFINITIONS_DIR`,
`INITIATIVES_DIR`, `HIERARCHY_FILE`, …), all derived from this folder's location.
Every script imports these constants so a folder rename is a one-line change.

### [`hierarchy.py`](hierarchy.py)
The **one** parser for the authored domain hierarchy
(`config/azure-domain-hierachy.md`). Exposes `load_domain_map()` (`{category: domain}`)
and `load_hierarchy()` (`{domain: [categories]}`). One authored hierarchy → one
parser → one generated `index.json`; no second copy means no drift.

### [`tiers.py`](tiers.py)
The **one** tier-classification engine. Parses the authored
[`config/tier-rules.yaml`](../config/tier-rules.yaml) (with a small built-in
YAML-subset parser — no PyYAML dependency) and exposes `classify(name,
description, category=None)`. Both `extract_policies.py` and `enrich_policies.py`
import it, so the Essential/Professional/Enterprise rules have a single authored
source and no second copy can drift. The YAML uses plain keyword phrases (a space
matches whitespace, a hyphen matches space-or-hyphen, a trailing `*` is a stem,
and `...` is an arbitrary gap) — see the comments at the top of the file.

---

## Tools (not part of the catalogue build, not consumed by clients)

### [`ab_verify.py`](ab_verify.py)
A **regression / diff-check harness** — a developer tool, *not* a pipeline step.
It proves a past refactor of `create_initiatives.py` was **additive-only**: it
mechanically strips the deliberately-added bits (the `catalogueVersion` /
`hasRemediation` / `roleDefinitionIds` metadata keys, the `.roles.json` sidecar,
and the `index.json` / `catalogue.json` finalize) to reconstruct a synthetic
"pre-refactor" generator, runs **both** old and new against the *same*
`catalogue/definitions`, and diffs the output.

**PASS** means: `.md` / `.assignment.json` / `.exemptions.json` are byte-identical;
`.policyset.json` match after removing the added metadata keys; the only
post-exclusive files are `.roles.json` plus the root manifests. Run it after any
change to step ③ to confirm grouping/enrichment behaviour is unchanged:

```
python flows/ab_verify.py            # empty param index — isolates the grouping path
python flows/ab_verify.py --source "<official policy repo>"   # also bakes roles
```

### [`catalogue_diff.py`](catalogue_diff.py)
A **catalogue drift detector** — compares two catalogues at the policy-asset level
(keyed on policy GUID) and reports exactly which policies were **added, removed,
re-tiered, re-categorised, or had their baked effect changed**, then attributes the
cause from each side's `catalogue.json` provenance (source git ref, tool hashes,
content fingerprint). Works on a catalogue root or an `initiatives/` directory
directly. Use it to review what a re-run or a built-ins bump actually changed:

```
python flows/catalogue_diff.py OLD NEW [--out report.json] [--limit 20]
```

---

## Phase 4 — the assembler (to be built)  ░ placeholder ░

The bottom half of the SVG — the **consumer** — is not implemented yet. It is a
standalone, deterministic transform `manifest + catalogue@version → IaC scaffold`,
designed in [`../docs/phase-4-assembler-design.md`](../docs/phase-4-assembler-design.md).
Planned entry point:

```
python flows/assemble_scaffold.py --manifest customer/manifests/<customer>.manifest.jsonc
        # --only json|terraform|bicep   --check (validate, write nothing)   --out <dir>
```

It will: **expand** a tiny `input.json` (customer · selection · parameters) into a
manifest (seeding required params from `index.json`), **resolve + bind** the
selection against the catalogue (tier roll-up, parameter binding, effect posture),
build a flavour-neutral **canonical IR**, and **render** EPAC/JSON + Terraform +
Bicep into `customer/initiatives/`, then validate → PR → deploy. It reads the
catalogue only (roles are already baked by step ③) and never re-runs the producer.

When implemented, add its row to the table above and a step section here.
