# `tools/` — dev / analyst utilities

Standalone helpers for **developing and auditing** the catalogue. They are **not** part of the
catalogue build and are **not** consumed by clients — nothing in the producer or consumer imports
them. Run them by hand when you change a producer step or want to inspect a catalogue. Each shares
the project paths via [`../shared/paths.py`](../shared/paths.py), so a folder rename never breaks them.

## At a glance

| Tool | What it answers | When to run |
| --- | --- | --- |
| [`ab_verify.py`](ab_verify.py) | "was my refactor of step ③ additive-only?" | after changing `create_initiatives.py` |
| [`catalogue_diff.py`](catalogue_diff.py) | "what actually changed between two catalogues?" | after a re-run or a built-ins bump |
| [`summarize_categories.py`](summarize_categories.py) | "what categories exist and how big are they?" | when reviewing the taxonomy |
| [`svg-gen/management-groups/`](svg-gen/management-groups/) | "how do I draw my management-group / scope hierarchy?" | when a consumer designs their MG tree |

## The tools

### [`ab_verify.py`](ab_verify.py)
A **regression / diff-check harness** that proves a past refactor of `create_initiatives.py` is
**additive-only**. It mechanically strips the deliberately-added bits (the `catalogueVersion` /
`hasRemediation` / `roleDefinitionIds` metadata, the `.roles.json` sidecar, the `index.json` /
`catalogue.json` finalize) to reconstruct a synthetic "pre-refactor" generator, runs **both** old
and new against the *same* `catalogue/definitions`, and diffs. **PASS** = `.md` / `.assignment.json`
/ `.exemptions.json` byte-identical, `.policyset.json` identical after removing the added metadata,
and the only post-exclusive files are `.roles.json` plus the root manifests.

```
python flows/tools/ab_verify.py            # empty param index — isolates the grouping path
python flows/tools/ab_verify.py --source "<official policy repo>"   # also bakes roles
```

### [`catalogue_diff.py`](catalogue_diff.py)
A **catalogue drift detector** — compares two catalogues at the policy-asset level (keyed on policy
GUID) and reports exactly which policies were **added, removed, re-tiered, re-categorised, or had
their baked effect changed**, then attributes the cause from each side's `catalogue.json`
provenance (source git ref, tool hashes, content fingerprint). Works on a catalogue root or an
`initiatives/` directory directly.

```
python flows/tools/catalogue_diff.py OLD NEW [--out report.json] [--limit 20]
```

### [`summarize_categories.py`](summarize_categories.py)
A **taxonomy inspector** — walks every `policies.md` under `catalogue/definitions/`, parses the
table (via [`../shared/mdtable.py`](../shared/mdtable.py)), and summarizes the `Category` column
(counts and distribution). Prints to stdout, or writes a markdown report with `--md <file>` (see
the companion [`summarize_categories.md`](summarize_categories.md)).

```
python flows/tools/summarize_categories.py [--source <folder>] [--md <file>]
```

### [`svg-gen/management-groups/`](svg-gen/management-groups/)
A **consumer-facing** generator (the exception to the "not consumed by clients" note above)
that turns an Azure **management-group / scope hierarchy** into theme-aware SVGs — a
`minimal-` (names only) and a `rich-` (scope ids, subscriptions, resource groups) variant.
The hierarchy can be given as indented text, `Parent -> Child` edges, canonical JSON, or a
real tenant inventory export (`.csv` / `.xlsx`) — all auto-detected. It is **self-contained**
(unlike the other tools here it doesn't import `../shared/`): SVGs default into its own
`output/` folder. See the folder's own [`README.md`](svg-gen/management-groups/README.md).

```
# picks up every file in the tool's input/ folder (or pass --input <path>)
python flows/tools/svg-gen/management-groups/generate_svg.py \
    [--input <path>] [--format auto|indent|edges|json|csv|xlsx] [--variant both|minimal|rich] [--out-dir <dir>]
```
