# Backlog

Living list of action items for catalogue-builder / epac-builder. Sourced from reviews in
`log/`. Update at the start/end of every session — see `actions/sessions/`.

Status: `todo` / `in-progress` / `done`

| # | Item | Effort | Status | Source |
|---|---|---|---|---|
| 1 | Test suite / CI on the builder (golden-fixture diff against `customer/package/`) | low | done (2026-07-03) | log/review-07-03-26.md |
| 1a | Add `requirements.txt`/`pyproject.toml` marker (stdlib-only, but make it explicit) | low | todo | log/review-07-03-26.md |
| 1b | Drop committed `__pycache__`, add to `.gitignore` | low | todo | log/review-07-03-26.md |
| 2 | Manifest completion guardrail: `--strict`/pre-deploy gate that fails when any `<REPLACE:>` or placeholder-scope survives into output | medium | todo | log/review-07-03-26.md |
| 3 | Catalogue customer-clean: resolve/remove `undefined`-domain policies, drop `builtinpolicytest` so the catalogue can be regenerated reproducibly | high | todo | log/review-07-03-26.md |
| 4 | `customer/package/docs/*.svg` is stale vs. `customer/designs/*.svg` (byte-diff, same commit) — CI's golden-fixture diff excludes `docs/` because of this; resync so the exclusion can be dropped | low | todo | discovered building CI, 2026-07-03 |
| 5 | Producer's `--source` default is hard-coded to a local clone path (`C:\GIT\Official Azure Policy\...`) — breaks for anyone but Karel running without `--source`. In `extract_policies.py` (`DEFAULT_SOURCE`, ~line 270; docstring line 17; argparse default line 292) and `create_initiatives.py` (`DEFAULT_SOURCE`, ~line 55; argparse default line 659). `--source` already exists as an override, so the fix is just: stop defaulting to a personal path — require `--source` explicitly (fail with a clear message) or read an env var (e.g. `AZURE_POLICY_REPO`), then update the two docstrings, `flows/catalogue_builder/README.md`, and `docs/az-taxonomy-pipeline.md`. Producer-only; doesn't touch the customer-facing epac-builder path | low | done (2026-07-03) | Karel, 2026-07-03 |
| 6 | Pinned-commit fetch for the official policy source: `config/policy-source.json` pin + `flows/tools/fetch_policy_source.py` (`--sync` / `--check`) materialising a gitignored `.policy-source/` cache; `official_policy_source()` defaults to it. Gives everyone one reproducible version (builds match committed `builtInsRef`). Kernel of the future daily-sync system | medium | done (2026-07-04) | Karel, 2026-07-04 |
| 7 | Daily-sync system: schedule `fetch_policy_source.py --sync` + `--check` (GitHub Action / cron) and wire the `--check` drift signal (exit 2) into a notification. Builds on #6 | medium | todo | discovered building #6, 2026-07-04 |
| 8 | Producer-side CI: now that the source is reproducible (#6), add a workflow that runs `fetch_policy_source.py` then regenerates the catalogue and diffs it (extend/complement `.github/workflows/test.yml`, which currently only exercises the consumer/assembler) | medium | todo | discovered building #6, 2026-07-04 |

## Notes

- Item 1's CI workflow diffs everything the assembler actually computes
  (`Definitions/`, `lineage.json`, `report.md`, `README.md`, `.github/workflows/epac.yml`
  inside the generated package). `docs/` is excluded — see #4.
- Item 5 was split out of the review's original #3 ("decouple producer from hard-coded
  path") once the code was checked — it's a two-file default-value fix, not a curation
  task, so it's tracked and estimated separately from the catalogue-cleanup work.
- Re-run `actions/review-prompt.md` periodically; reconcile new findings into this table.
