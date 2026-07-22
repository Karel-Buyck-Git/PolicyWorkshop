# AGENTS.md — for any AI assistant working in this repo

Whatever tool you are (Claude, Copilot, Codex, Cursor, …), the instructions live in this repo as
Markdown — not in any one vendor's config. Read these, in order:

1. [`README.md`](README.md) — what this repo is, the environment contract (Python ≥ 3.10, stdlib-only,
   no `pip`), and who does what.
2. [`CLAUDE.md`](CLAUDE.md) — the working mental model: **producer** (builds the catalogue) vs
   **consumer** (assembles a customer package); `customer/` (the user's empty working area) vs
   `examples/contoso/` (the read-only worked sample **and** the CI golden fixture, so it is generated,
   never hand-edited). Despite the filename this is orientation for *any* assistant, not just Claude.

## Ground rules

- **Run tooling from `epac-workbench/`** — paths are relative to it.
- **Stdlib-only.** Do not add third-party Python dependencies or a `pip`/lockfile step; `engine/`
  imports only the standard library, on purpose. Match that (the repo hand-rolls its YAML/JSON-Schema/
  JSONC parsers rather than take a dependency).
- **Don't touch `foundry/` or `lab/`** — historical/prototype trees.
- **`examples/contoso/` and `catalogue/` are generated** — change the manifest/catalogue and
  regenerate; never hand-edit the outputs (CI diffs them byte-for-byte).
- Verify a change the way the repo does: `bash epac-workbench/examples/contoso/verify.sh`.

## Optional: the MCP server

[`.mcp.json`](.mcp.json) registers a local MCP server (`epac-builder`) exposing builder tools such as
`validate_manifest`. It's **convenience only** — if your assistant supports MCP, register the same
`python epac-workbench/engine/mcp_server/server.py` command; if not, every tool is also a CLI
(`python engine/epac_builder/assemble_scaffold.py --check [--strict]`). Nothing here depends on it.

First thing on a fresh clone: `python epac-workbench/engine/tools/check_env.py` to confirm the
toolchain.
