# `tools/` — dev / analyst utilities

Standalone helpers for **developing and auditing** the catalogue. They are **not** part of the
catalogue build and are **not** consumed by clients — nothing in the producer or consumer imports
them. Run them by hand when you change a producer step or want to inspect a catalogue — with two
exceptions: [`check_catalogue_stamp.py`](check_catalogue_stamp.py) also runs in CI on every push,
and [`release.py`](release.py) is the one tool here that **writes tracked source files** (`version.py`,
`pyproject.toml`) and creates git tags, rather than only reading and reporting.
Each shares
the project paths via [`../shared/paths.py`](../shared/paths.py), so a folder rename never breaks them.

## At a glance

| Tool | What it answers | When to run |
| --- | --- | --- |
| [`check_env.py`](check_env.py) | "is my machine set up to run this tooling?" | first thing after cloning, or when a script dies |
| [`fetch_policy_source.py`](fetch_policy_source.py) | "give me the pinned official policy source everyone builds against" | before a build, or on a schedule |
| [`ab_verify.py`](ab_verify.py) | "was my refactor of step ③ additive-only?" | after changing `create_initiatives.py` |
| [`catalogue_diff.py`](catalogue_diff.py) | "what actually changed between two catalogues?" | after a re-run or a built-ins bump |
| [`catalogue_changelog.py`](catalogue_changelog.py) | "record what changed in this release, and why" | at every catalogue release, after phase 5 |
| [`release.py`](release.py) | "what engine version does this become, and what tags it?" | at every release — **before** regenerating the catalogue |
| [`check_catalogue_stamp.py`](check_catalogue_stamp.py) | "is the committed catalogue still the one this engine produces?" | **in CI on every push**, and after any producer change |
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
python engine/tools/check_env.py
```

### [`check_catalogue_stamp.py`](check_catalogue_stamp.py)
The **drift alarm** between the two builders, and the one tool here that is **not** hand-run only:
[`../../../.github/workflows/contoso-epac-build.yml`](../../../.github/workflows/contoso-epac-build.yml)
runs it on every push. `verify.sh` exercises the **consumer** — so a producer script can change
with no catalogue regeneration and every check stays green while `catalogue.json` fingerprints a
file that no longer exists (exactly what happened for a day on 2026-07-23, backlog #26). This
recomputes every fingerprint the catalogue claims — the authored inputs (hierarchy, tier rules,
generator registry), the four producer tool files, the upstream pin, and the whole-tree
`contentHash` — and fails if any moved. It works **without running the producer** because #27
made the hashes reproducible ([`../shared/hashing.py`](../shared/hashing.py) normalizes newlines
first), so it costs seconds.

A stamp key the producer adds but this tool doesn't know is reported as **uncovered**, not
skipped — the check can't quietly start verifying less than it claims. A catalogue built by an
older engine is a `note`, not a failure: that is accurate provenance, and anything it actually
depends on is already covered above.

This is the cheap slice of backlog **#8**, not a replacement — #8 re-runs the producer and diffs
the result, the only way to catch a change in what the tools *produce*. Exit `0` in sync · `1`
drift (re-run the producer and commit the regenerated catalogue) · `2` no readable catalogue.

```
python engine/tools/check_catalogue_stamp.py
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
python engine/tools/fetch_policy_source.py            # --sync: materialise the pinned source
python engine/tools/fetch_policy_source.py --check     # report drift vs upstream master (no changes)
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
python engine/tools/ab_verify.py            # empty param index — isolates the grouping path
python engine/tools/ab_verify.py --source "<official policy repo>"   # also bakes roles
```

### [`catalogue_diff.py`](catalogue_diff.py)
A **catalogue drift detector** — compares two catalogues at the policy-asset level (keyed on policy
GUID) and reports exactly which policies were **added, removed, re-tiered, re-categorised, or had
their baked effect changed**, then attributes the cause from each side's `catalogue.json`
provenance (source git ref, tool hashes, content fingerprint). Works on a catalogue root or an
`initiatives/` directory directly.

```
python engine/tools/catalogue_diff.py OLD NEW [--out report.json] [--limit 20] [--allow-unreadable]
```

**It refuses to diff a tree it cannot fully read** (#46). A policyset that fails to parse is not
neutral: every policy inside it vanishes from its side and reappears as **added** against the
other, inventing changes that never happened — and the file *count* still looks right, because
that comes from the directory listing rather than from what was parsed. This bit for real on
2026-07-25, when a catalogue staged under a deep temp path crossed the Windows **260-char
`MAX_PATH`** limit and the changelog reported 39 phantom "added" policies. The error now names the
files, the reason, and (on Windows, for long paths) the likely cause. `--allow-unreadable` opts
into a best-effort diff of a knowingly damaged tree: it warns loudly and sets `unreadable` in the
JSON report. [`catalogue_changelog.py`](catalogue_changelog.py) has **no such flag** on purpose — a
console report is something you read, but a committed changelog entry is a durable claim, and a
wrong one is indistinguishable from a real record.

### [`catalogue_changelog.py`](catalogue_changelog.py)
The **release recorder** — turns a `catalogue_diff` into a durable, customer-readable
`catalogue/CHANGELOG.md` entry attributed to its driver (upstream Microsoft policy changes,
taxonomy/curation, or engine changes). Run it as the last step of a release, diffing the previous
catalogue tree against the new one; omit `--old` for a baseline entry.

```
python engine/tools/catalogue_changelog.py --old <path/to/previous/catalogue> [--write]
```

Stage the previous catalogue at a **short path** — a deep temp path is what triggered the #46
`MAX_PATH` failure, and this tool has no `--allow-unreadable` escape hatch by design.

**It is also the release ledger the #48 version guard reads.** `CHANGELOG.md` is the only record
of which labels were actually *released* and what each one meant, so the producer consults it
before stamping ([`../definition_gen/apply_overlays.py`](../definition_gen/apply_overlays.py)) and
this tool consults it again before writing. `--write` therefore **refuses** (exit 2) to record a
label already present with a different `contentHash`, and **skips** — rather than duplicating — a
label already present with the same one.

### [`release.py`](release.py)
The **engine release helper** — decides the next engine SemVer, writes it to
[`../shared/version.py`](../shared/version.py) + `pyproject.toml`, and cuts the annotated `v*` tag.
The number is not hand-picked: it is derived from the Conventional-Commit prefixes since the last
`v*` tag (`feat!:`/`BREAKING CHANGE` → major, `feat:` → minor, `fix:`/`perf:` → patch;
`docs`/`chore`/`refactor`/`test` imply no release on their own). The only judgement a human makes is
*"is this breaking?"* — the `!` you already type in the commit.

```
python engine/tools/release.py                 # dry-run: analyse and print the proposal
python engine/tools/release.py --apply         # write version.py + pyproject.toml
python engine/tools/release.py --apply --tag   # also commit the bump and create v<x.y.z>
```

> ⚠️ **Run it BEFORE regenerating the catalogue.** `producedByEngine` is stamped into
> `catalogue.json` during producer phases 3–4, so a bump applied afterwards leaves the catalogue —
> and every package `lineage.json` built from it — claiming the **previous** engine. That is exactly
> the under-reporting backlog **#53** was opened for: for three days after `v0.1.0` was cut, the
> artifacts said `0.1.0` while the engine carried two behavioural commits past the tag. The full
> ordering lives in **Phase 6** of the `/catalogue-builder-run` runbook.

The tag itself is **not** stamped into any artifact — the `version.py` constant is, deliberately, so
the stamps are byte-reproducible on any checkout with no runtime `git` call and no CI shallow-clone
fragility. The tag's two jobs are being the auto-SemVer fencepost (before the first `v*` tag there is
nothing to measure from) and the public release marker for `git describe`.

### [`summarize_categories.py`](summarize_categories.py)
A **taxonomy inspector** — walks every `policies.md` under `catalogue/definitions/`, parses the
table (via [`../shared/mdtable.py`](../shared/mdtable.py)), and summarizes the `Category` column
(counts and distribution). Prints to stdout, or writes a markdown report with `--md <file>` (see
the companion [`summarize_categories.md`](summarize_categories.md)).

```
python engine/tools/summarize_categories.py [--source <folder>] [--md <file>]
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
python engine/tools/svg-gen/management-groups/generate_svg.py \
    [--input <path>] [--format auto|indent|edges|json|csv|xlsx] [--variant both|minimal|rich] [--out-dir <dir>]
```
