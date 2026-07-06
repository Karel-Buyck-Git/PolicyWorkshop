# `tools/` — dev / analyst utilities

Standalone helpers for **developing and auditing** the catalogue. They are **not** part of the
catalogue build and are **not** consumed by clients — nothing in the producer or consumer imports
them. Run them by hand when you change a producer step or want to inspect a catalogue. Each shares
the project paths via [`../shared/paths.py`](../shared/paths.py), so a folder rename never breaks them.

## At a glance

| Tool | What it answers | When to run |
| --- | --- | --- |
| [`check_env.py`](check_env.py) | "is my machine set up to run this tooling?" | first thing after cloning, or when a script dies |
| [`fetch_policy_source.py`](fetch_policy_source.py) | "give me the pinned official policy source everyone builds against" | before a build, or on a schedule |
| [`ab_verify.py`](ab_verify.py) | "was my refactor of step ③ additive-only?" | after changing `create_initiatives.py` |
| [`catalogue_diff.py`](catalogue_diff.py) | "what actually changed between two catalogues?" | after a re-run or a built-ins bump |
| [`summarize_categories.py`](summarize_categories.py) | "what categories exist and how big are they?" | when reviewing the taxonomy |
| [`svg-gen/management-groups/`](svg-gen/management-groups/) | "how do I draw my management-group / scope hierarchy?" | when a consumer designs their MG tree |

## The tools

### [`check_env.py`](check_env.py)
The **environment doctor** — the one tool here you run *before* anything else. Pure stdlib and
standalone (it imports nothing from the repo, and is written to still run on an old interpreter so
it can tell you it's too old), it checks the contributor toolchain — **Python ≥ 3.10**, a bare
`python` on PATH (the MCP server in `.mcp.json` calls it), and `bash`/`diff`/`git` (for `verify.sh`
and the reset flow) — and prints a specific fix for anything missing instead of letting a later
script die with a raw error. It does **not** check deploy-time prerequisites (PowerShell, Az, the
EPAC module); those live in [`../../docs/scaffold-deployment-guide.md`](../../docs/scaffold-deployment-guide.md).
Exit `0` all good · `1` a per-flow tool is missing · `2` Python is too old.

```
python flows/tools/check_env.py
```

### [`fetch_policy_source.py`](fetch_policy_source.py)
The one utility here that **feeds the build** rather than audits it: it materialises the official
Azure Policy source the producer reads. To keep catalogues reproducible, everyone builds against the
**same** upstream commit, pinned in [`../../config/policy-source.json`](../../config/policy-source.json).
`--sync` (default) fetches exactly that commit into a gitignored `.policy-source/` cache (partial +
sparse — only the pinned `policyDefinitions` subdir); [`../shared/paths.py`](../shared/paths.py)'s
`official_policy_source()` then resolves the producer's `--source` default to it. `--check` reports
when upstream `master` has drifted past the pin (exit ≠ 0), without touching the cache — the
reproducible-checkout + drift-signal kernel of a future daily-sync job.

```
python flows/tools/fetch_policy_source.py            # --sync: materialise the pinned source
python flows/tools/fetch_policy_source.py --check     # report drift vs upstream master (no changes)
```

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
