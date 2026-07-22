# PolicyWorkshop — Azure Policy → EPAC tooling

Turns Microsoft's official built-in Azure policies into a shared, versioned **catalogue**, then
assembles that catalogue into a customer's deployable **EPAC** package (JSON / Terraform / Bicep).
The active project is [`epac-workbench/`](epac-workbench/). For the mental model — *producer*
(builds the catalogue) vs *consumer* (assembles a customer package), and `customer/` vs
`examples/contoso/` — read [`CLAUDE.md`](CLAUDE.md).

New here? Two minutes: check your setup (below), find your role, go.

## Environment contract — what you need to *run* the tooling

The engine is **stdlib-only Python: there is no `pip install`, no lockfile, no virtualenv.** You need:

| Requirement | Why | Missing on Windows? |
|---|---|---|
| **Python ≥ 3.10** | every `engine/` script; the one hard requirement | install from python.org |
| **`bash` + GNU `diff` + `mktemp`** | `examples/contoso/verify.sh` and the health check | install **Git for Windows** — its Git Bash bundles all three |
| **`git`** | the reset flow and normal work | Git for Windows |

That's it. This is separate from **deploy-time** prerequisites (PowerShell 7.4+, the Az and
EnterprisePolicyAsCode modules) — those only matter once you push a generated package to an Azure
tenant, and they live in [`docs/scaffold-deployment-guide.md`](epac-workbench/docs/scaffold-deployment-guide.md) §3.

### Verify your setup

```
python epac-workbench/engine/tools/check_env.py
```

The **doctor** checks the toolchain and prints a specific fix for anything missing (e.g. *"your
Python is 3.9 — need 3.10+"*, *"install Git Bash for `diff`"*), instead of letting a script die
later with a raw error. Green + exit `0` = you're ready. Run it first thing after cloning, or any
time a command fails oddly.

## Who are you? Find your path

The repo has three roles. Your job title maps onto one of them:

| If you're a… | Your role | Start here |
|---|---|---|
| **engineer / developer** building the catalogue or the assembler | **Producer / maintainer** | doctor → `/epac-builder-start` (daily health-check + orient) → [`actions/backlog.md`](actions/backlog.md). Produce the catalogue with `/catalogue-builder-run`. |
| **integration specialist / security operator / architect** standing up your *own* policy scaffold | **Consumer** | `/epac-builder-onboard` — it interviews you and generates your package under `epac-workbench/customer/`. **Read-only on the engine**; you never edit `engine/**`. |
| **manager / sales / support** who just needs the catalogue's contents | **Reader** | browse [`epac-workbench/catalogue/`](epac-workbench/catalogue/) and the tier/product docs in [`epac-workbench/docs/`](epac-workbench/docs/). No clone-and-run needed. |

`customer/` is **your** empty working area; [`examples/contoso/`](epac-workbench/examples/contoso/)
is the read-only worked sample (and the CI golden fixture). Don't hand-edit the example — change the
manifest/catalogue and regenerate.

Almost everything runs from the `epac-workbench/` directory (paths are relative to it).

## Working with AI assistants

Most work here is AI-assisted, and the team uses different tools (Claude, Copilot, Codex, Cursor).
The rule that keeps that sane:

> **The source of truth is the Markdown in this repo.** Each assistant's own config just *points* at
> it — it never forks the instructions.

- **Claude Code** is wired in: [`CLAUDE.md`](CLAUDE.md) (project instructions) + [`.mcp.json`](.mcp.json),
  which registers a local MCP server exposing builder tools (starting with `validate_manifest`).
  See [`epac-workbench/engine/mcp_server/README.md`](epac-workbench/engine/mcp_server/README.md).
- **Any other assistant** starts from [`AGENTS.md`](AGENTS.md), a vendor-neutral pointer to the same
  docs. If your tool supports MCP, register the *same* command from `.mcp.json`; if it doesn't, every
  MCP tool is also a plain CLI (e.g. `python engine/epac_builder/assemble_scaffold.py --check`), so
  nothing is gated on the MCP server.

The MCP server is a **convenience layer, never a requirement** — a colleague with only Python, bash,
and git can do everything from the command line.
