# `mcp_server/` — a local (stdio) MCP server over the epac-builder

Exposes the on-disk build/validate flows as [MCP](https://modelcontextprotocol.io) tools so an
author can drive them conversationally instead of shelling out. This is the **local half** of
backlog #17 — a single-user, single-working-tree surface. It ships with one tool
(`validate_manifest`); the other #17 tools drop in as new modules under [`tools/`](tools/).

**Stdlib-only**, like the rest of `flows/`: it hand-rolls JSON-RPC 2.0 over newline-delimited
stdin/stdout rather than depending on the `mcp` PyPI SDK, so the project's `dependencies = []`
contract holds. No `pip install`.

## At a glance

| File | Responsibility |
| --- | --- |
| [`server.py`](server.py) | MCP stdio transport — the JSON-RPC loop (`initialize` / `tools/list` / `tools/call` / `ping`) + tool dispatch. **stdout is the protocol channel**; tools route engine logging into a buffer so nothing else lands there. |
| [`tools/__init__.py`](tools/__init__.py) | the `TOOLS` registry — one line per tool. |
| [`tools/validate_manifest.py`](tools/validate_manifest.py) | the one tool: wraps `assemble_scaffold.py --check` / `--check --strict`, imported (not shelled out) and returned as **structured** JSON. |
| [`test_server.sh`](test_server.sh) | golden smoke test — a canned JSON-RPC session driven at `server.py` with assertions on the responses (house byte-diff style, no pytest). |

## Entry point

```
# from catalogue-builder/ (or anywhere — relative manifest paths resolve against catalogue-builder/)
python flows/mcp_server/server.py
```

The server speaks MCP over stdio, so it's normally launched by a client, not by hand — see
[`.mcp.json`](../../../.mcp.json) at the repo root, which registers it for Claude Code.

## `validate_manifest`

Validates a customer manifest and returns the result as structured data (the CLI flattens the
same detail into one stderr string).

| Arg | Type | Notes |
| --- | --- | --- |
| `manifest` | string (required) | path to the manifest (.jsonc/.json); relative → resolved against `catalogue-builder/`. |
| `strict` | boolean (default `false`) | also run the deploy-ready gate (`--check --strict`): fail if any `<REPLACE:>` value or placeholder scope survives. |

Result shape:
- success → `{ valid: true, initiativesResolved, warnings, note }`
- schema failure → `{ valid: false, stage, errors: [...] }`
- strict-gate failure → `{ valid: false, strictProblems: [...] }`
- other assembler error → `{ valid: false, error }`

**A validation failure is a normal result** (`isError: false`, `valid: false` + the problem list) —
that's what makes it usable feedback for an agent iterating on a manifest. `isError: true` is
reserved for real tool failures (missing path, unexpected crash).

**Read-only.** The tool passes `write_back=False` into the engine, so validating never mutates the
manifest — even the `pacOwnerId` auto-fill that `assemble_scaffold.py --check` performs on the CLI
is suppressed here and surfaced as a `note` instead.

## Conventions

- **stdlib-only** — no third-party runtime dependency (matches `pyproject.toml`).
- stdout carries **only** JSON-RPC; all diagnostics go to stderr, all engine logging is captured.
- Adding a tool = one new `tools/<name>.py` exposing a `TOOL` dict + one line in `tools/__init__.py`.
