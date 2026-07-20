# PolicyWorkshop — orientation

Azure Policy → EPAC tooling. The active project is **`catalogue-builder/`** (a producer + a
consumer). `foundry/` and `lab/` are historical/prototype trees — don't touch them
unless asked.

## Producer vs. consumer

- **Producer** (catalogue-builder): turns Microsoft's official built-in policies into the
  shared, versioned `catalogue-builder/catalogue/`. Runbook is the `/catalogue-builder-run`
  command (`.claude/commands/catalogue-builder-run.md`), phases 1–5.
- **Consumer** (epac-builder / assembler): `flows/epac_builder/assemble_scaffold.py` reads a
  manifest + the shared catalogue and renders a customer's deployable EPAC package. It never
  runs the producer pipeline.

## `customer/` vs. `examples/contoso/` (important)

These two mirror each other — know which is which before editing:

- **`catalogue-builder/customer/`** is the **user's working area**: it *ships* empty — schemas +
  `manifests/manifest.template.jsonc` + `input.example.json` + READMEs, and an empty
  `designs/`, with **no `manifest.example.jsonc`** — a real user fills the template and builds
  their own. But a real (non-sample) deploy package **may be committed here**: `input.json` +
  `<customer>.manifest.jsonc` + rendered `package/` together (none gitignored; EPAC's
  `package/Output/` plan artifact is ignored repo-wide). Such a package is the user's own
  deploy, **not** the contoso fixture — don't treat it as stray. Start at `customer/NOTICE.md`.
- **`catalogue-builder/examples/contoso/`** is the **worked sample** (`manifests/`, `designs/`,
  `package/`, `fixtures/`) **and the CI golden fixture**: `.github/workflows/contoso-epac-build.yml`
  runs `examples/contoso/verify.sh`, which rebuilds the sample for every renderer flavour (json →
  `package/`, terraform → `fixtures/terraform/`, bicep → `fixtures/bicep/`) and diffs each
  byte-for-byte. So those trees are **generated, never hand-edited** — change the manifest/catalogue
  and regenerate.

Schemas are shared: the assembler always loads them from `customer/manifests/`, so both the
empty scaffold and the example validate against the same schemas.

## Working notes

- Session bookkeeping lives in `actions/`: `backlog.md` + dated `sessions/*.md`, plus
  `log/` (periodic `/review` audits) and `feedback/` (consumer feedback logs). The
  `/continue` command orients from them; `/catalogue-builder-run` runs the producer.
- Run assembler/producer scripts from the `catalogue-builder/` directory (paths are relative
  to it).
