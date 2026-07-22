# `epac-builder-onboarding-agent` — consumer onboarding skill

A self-contained skill that onboards a **new consumer** to EPAC Builder: an engineer, developer, or
other user who wants to generate their own deployable Azure Policy scaffold from the shared catalogue —
**without** modifying the engine.

It runs four phases: **Explain** (how the catalogue/EPAC builders work and what the package contains)
→ **Interview** (collect *every* input up front, no silent defaults) → **Generate** (drive the real
`assemble_scaffold.py` to fill `customer/` and render `customer/package/`) → **Hand off**.

**Hard boundary:** the skill is **read-only on the engine**. It only writes under
`epac-workbench/customer/` and calls the existing assembler; it never edits `engine/**`,
`catalogue/**`, the shared schemas, or workflows — even if asked mid-session. Engine changes go
through the normal dev workflow (repo-root `README.md` + `CLAUDE.md`, `/catalogue-builder-run`, the backlog).

The instructions live in [`SKILL.md`](SKILL.md). Invoke it whenever someone wants to start using
EPAC Builder as a consumer — via the thin slash command **`/epac-builder-onboard`**
(`.claude/commands/epac-builder-onboard.md`), which points here.

It also ships a **`/reset-customer-package`** command
([`reset-customer-package.md`](reset-customer-package.md), exposed via
`.claude/commands/reset-customer-package.md`) that undoes an onboarding — restoring `customer/` to its
clean empty-scaffold state, with a destructive-action confirmation and a "stop rather than guess"
safety check when the folder has unexpected changes.

See the worked reference customer at [`../../examples/contoso/`](../../examples/contoso/) for what a
completed onboarding produces.
