# `tests/` — engine unit tests (backlog #38)

Stdlib `unittest`, no third-party runner — `pyproject.toml` keeps `dependencies = []`
and that is deliberate, so the tests must run on a bare Python.

```
cd epac-workbench
python -m unittest discover -s tests -t tests          # all of it, ~0.2s
python -m unittest discover -s tests -t tests -v       # per-test names
python -m unittest discover -s tests -t tests -k anchor  # one theme
```

`-t tests` sets the top-level directory so `import support` / `import _engine_path`
resolve. [`_engine_path.py`](_engine_path.py) puts `engine/` on `sys.path` the same way
the assembler's own entry point does — the engine is not an installed package.

## Why this exists

End-to-end coverage was already strong — [`examples/contoso/verify.sh`](../examples/contoso/verify.sh)
byte-diffs all three renderer flavours and asserts the `--strict` gate fires — but it is
**coarse**: any break in `expand`, `bind`, `build_ir` or a renderer surfaced as "some
file differs", with no indication of which function, and the producer was not exercised
in CI at all. These tests localize a failure to a function and a message.

They **complement** the golden fixture rather than replacing it. The fixture proves the
whole pipeline is deterministic against the real 3,461-policy catalogue; these prove the
individual contracts, including error paths a happy-path fixture can never reach.

## The mini-catalogue fixture

[`fixtures/mini-catalogue/`](fixtures/mini-catalogue/) is a hand-authored catalogue of
three groups, a few KB total:

| Group | Shape it covers |
|---|---|
| `demo/essential/plain` | two built-in members, one required parameter, no remediation |
| `demo/essential/anchor` | **#21/#44**: a custom member whose naming anchor is a bubbled initiative-level `customerAbbreviation` parameter, with the matching `<REPLACE: …>` mock |
| `demo/professional/remediating` | a DeployIfNotExists member with `.roles.json` — managed identity + role assignments |

It pins **no catalogue version** (`source` requires only `initiatives`), so a catalogue
release never invalidates these tests and they never need re-pinning.

**Why a fixture rather than the real naming initiative (#44):** that initiative is 169
members / 111 KB. Covering the anchor path through the golden fixtures would commit
~330 KB across the three flavour trees — the rendered policyset in json, all 169 members
inlined into terraform's `main.tf`, and another copy for bicep's `loadJsonContent` — and
re-churn it on every catalogue release that touches naming. For a break that would still
report as a byte-diff.

`test_expand.py` is the deliberate exception: it drives the **real** catalogue and the
**real** schemas, because half its job is proving the shipped schemas still accept what
the shipped code generates. That pairing is exactly what broke in #42. It reads its
selection out of `index.json` at runtime rather than hardcoding group names.

## What each module pins

| Module | Covers | Regression it guards |
|---|---|---|
| `test_bind.py` | binding, the bubbled anchor, type checks, effect posture | **#21**, **#44** |
| `test_writeutil.py` | the writers emit LF on every host | **#52** |
| `test_catalogue.py` | tier roll-up, `*` expansion, fail-fast resolve messages | |
| `test_ir.py` | scopes, warnings, remediation, lineage provenance | #2, **#20** (safe `desiredState`), #27 |
| `test_strict.py` | the deploy-readiness gate, both halves | #2 |
| `test_render_json.py` | EPAC shape: `desiredState`, `definitionEntry` | **#20(a)**, **#20(b)** |
| `test_render_iac.py` | terraform + bicep shape, HCL escaping | #13, #33/#34 |
| `test_expand.py` | `input.json` → manifest, against the shipped schemas | **#42**, **#48** |
| `test_shared.py` | naming limits, tier rules, hierarchy, release ledger | **#48**, Azure hard limits |
| `test_producer.py` | producer phases 1–3 end to end on a fixture source tree | **#26**, #22, #27 determinism |
| `test_producer_finalize.py` | phases 4–5: overlays, the finalize gate, the release guard | **#48**, #22, #26 |
| `test_release_driver.py` | a whole release, rehearsed against a scratch workbench | **#51** — stops the driver rotting |

## The scratch workbench

[`workbench.py`](workbench.py) assembles a throwaway workbench and points the engine at it
with `EPAC_WORKBENCH_ROOT`. That override exists for exactly this: `apply_overlays`,
`quality_control` and the release driver read **fixed paths**, which is why they had no
coverage — exercising them meant writing to the real `catalogue/`.

It is a real workbench, not a mock: `engine/` and the schemas are copied verbatim, and
`config/` keeps the **real** hierarchy, tier rules and abbreviation map so classification and
naming behave as in production. Two deliberate substitutions: the policy source is the
4-policy fixture (via `AZURE_POLICY_REPO`), and `definition-gens.md` is rewritten per test —
all generators off by default (the documented built-in-only mode), or just `dlw-az-tagging`
for the overlay path, because the real naming generator emits 169 definitions and would
dominate a 4-policy run.

## The release rehearsal

`test_release_driver.py` drives a **complete release** — stage, phases, stamp, changelog,
re-pin, fixture rebuild — on every push.

It exists because of arithmetic, not distrust: a monthly tool gets ~12 real executions a year
while the engine underneath it changes weekly, so the driver would otherwise be discovered
broken *on release day*, which is exactly when hand-running becomes the fast path and the
tool quietly dies. The rehearsal passes `--no-battery`: the battery's four commands are
already run directly by CI, and what nothing else covers is the **sequence** — in particular
that staging happens *before* phase 3 destroys what it stages.

It also enforces the anti-drift contract. The release sequence now lives in two places, the
driver's `STEPS` and the runbook's Phase 6 prose — the same "written down in one place only"
failure mode as #51/#53, one level up. `STEPS` is the authority for order; the runbook owns
the why; `TestRunbookAndDriverAgree` fails if a step exists in one and not the other.

## The producer fixture

`fixtures/producer/` ships a **4-policy source tree** and **its own hierarchy**, so phases
1–3 run hermetically: an edit to `config/azure-domain-hierachy.md` cannot break these tests,
and a failure in them cannot be mistaken for a taxonomy change. Each policy earns its place —
a no-default parameter (bubbles to an initiative parameter), a customer-managed-key policy
(must tier Enterprise), a DeployIfNotExists with `roleDefinitionIds` (remediating, gets
`.roles.json`), and one whose category is absent from the fixture hierarchy (the `undefined`
catch-bucket).

These shell out to the three phase scripts and are the slow part of the suite (~1.5s of the
~1.7s total). They never touch the real `catalogue/`.

> **They found a bug on their first run**, which is the argument for having them: a category
> with no entry in `config/azure-category-abbreviation.md` kills Phase 3 with a raw `KeyError`
> traceback *after* the `initiatives/` tree has been wiped, leaving it half-rebuilt. Filed as
> **#55** — it is on the critical path of the monthly upstream sync, since categories come
> from Microsoft and the abbreviation map is authored by us.
>
> One authored input is still in play here for that reason: `shared/naming.py` reads the
> abbreviation file from a fixed path, so the fixture cannot override it.

## A test that cannot fail proves nothing

Both guards above were verified by breaking the code and watching them go red, not by
watching them go green:

- remove `newline="\n"` from `writeutil.py` → 3 failures in `test_writeutil`;
- remove `customerAbbreviation` from `support.DEFAULT_BINDINGS` → 4 errors, each a
  `BindError` naming the key **and** the manifest path to fix it.

Do the same when you add one.

## Coverage now, and what is still uncovered

Consumer, `shared/`, **all five producer phases**, and the release driver are covered.
Still not:

- **`engine/tools/`** as units — `catalogue_diff` and `catalogue_changelog` are exercised
  *through* the release rehearsal but have no tests of their own (notably `catalogue_diff`'s
  `_attribute` driver logic and #46's unreadable-catalogue refusal). `check_catalogue_stamp`
  runs in CI against the real catalogue every push, which is its own coverage.
- **`engine/mcp_server/`** — covered by its own shell smoke test, not from here.

## Runtime

~18s, most of it the producer and rehearsal suites spawning real phase scripts. The
consumer + `shared/` tests are still ~0.2s, so `-k` is worth using while iterating:

```
python -m unittest discover -s tests -t tests -k bind        # fast inner loop
python -m unittest discover -s tests -t tests -k rehearsal   # just the release drive
```
