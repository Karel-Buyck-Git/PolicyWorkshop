"""mcp_server — a local (stdio) MCP server over the epac-builder working tree.

Stdlib-only, like the rest of ``engine/``: it hand-rolls JSON-RPC 2.0 over
newline-delimited stdin/stdout rather than depending on the ``mcp`` PyPI SDK, so the
project's ``dependencies = []`` contract holds. Tools live under ``tools/`` and each
wraps an existing flow (starting with ``validate_manifest``); the server just routes.
"""
