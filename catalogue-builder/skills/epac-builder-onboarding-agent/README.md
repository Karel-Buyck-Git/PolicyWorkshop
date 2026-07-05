# `epac-builder-onboarding-agent` — consumer onboarding skill

A self-contained skill that onboards a **new consumer** to EPAC Builder: an engineer, developer, or
other user who wants to generate their own deployable Azure Policy scaffold from the shared catalogue —
**without** modifying the engine.

It runs four phases: **Explain** (how the catalogue/EPAC builders work and what the package contains)
→ **Interview** (collect *every* input up front, no silent defaults) → **Generate** (drive the real
`assemble_scaffold.py` to fill `customer/` and render `customer/package/`) → **Hand off**.

**Hard boundary:** the skill is **read-only on the engine**. It only writes under
`catalogue-builder/customer/` and calls the existing assembler; it never edits `flows/**`,
`catalogue/**`, the shared schemas, or workflows — even if asked mid-session. Engine changes go
through the normal dev workflow (`catalogue-builder/CLAUDE.md`, `/catalogue-builder-run`, the backlog).

The instructions live in [`SKILL.md`](SKILL.md). Invoke it whenever someone wants to start using
EPAC Builder as a consumer.

See the worked reference customer at [`../../examples/contoso/`](../../examples/contoso/) for what a
completed onboarding produces.
