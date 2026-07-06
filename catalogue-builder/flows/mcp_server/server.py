"""epac-builder MCP server (local, stdio).

    python flows/mcp_server/server.py        # run from catalogue-builder/

A hand-rolled MCP stdio transport: it reads newline-delimited JSON-RPC 2.0 requests
from stdin and writes responses to stdout, one JSON object per line. **stdout is the
protocol channel** — every tool routes engine logging into a captured buffer, so nothing
but JSON-RPC ever reaches it. Diagnostics go to stderr.

Stdlib-only by design (no ``mcp`` SDK). Tools are registered in ``tools/__init__.py``;
this module only implements ``initialize`` / ``tools/list`` / ``tools/call`` / ``ping``
and dispatches by name.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # flows/ root

from mcp_server.tools import TOOLS  # noqa: E402

PROTOCOL_VERSION = "2025-06-18"
SERVER_INFO = {"name": "epac-builder", "version": "0.1.0"}


def _result(mid, result):
    return {"jsonrpc": "2.0", "id": mid, "result": result}


def _error(mid, code, message):
    return {"jsonrpc": "2.0", "id": mid, "error": {"code": code, "message": message}}


def _spec(tool):
    """The client-facing shape of a tool (everything but the handler)."""
    return {k: tool[k] for k in ("name", "description", "inputSchema")}


def _call_tool(mid, params, registry):
    name = params.get("name")
    tool = registry.get(name)
    if tool is None:
        return _error(mid, -32602, f"unknown tool: {name!r}")
    try:
        payload, is_error = tool["handler"](params.get("arguments") or {})
    except Exception as e:  # a tool crash is a tool-level error, not a transport error
        payload, is_error = {"error": f"{type(e).__name__}: {e}"}, True
    return _result(mid, {
        "content": [{"type": "text", "text": json.dumps(payload, indent=2, ensure_ascii=False)}],
        "isError": is_error,
    })


def handle(msg, registry):
    """Route one JSON-RPC message. Returns a response dict, or None for notifications."""
    method = msg.get("method")
    mid = msg.get("id")

    if method == "initialize":
        client_version = (msg.get("params") or {}).get("protocolVersion")
        return _result(mid, {
            "protocolVersion": client_version or PROTOCOL_VERSION,
            "capabilities": {"tools": {}},
            "serverInfo": SERVER_INFO,
        })
    if method == "notifications/initialized":
        return None
    if method == "ping":
        return _result(mid, {})
    if method == "tools/list":
        return _result(mid, {"tools": [_spec(t) for t in TOOLS]})
    if method == "tools/call":
        return _call_tool(mid, msg.get("params") or {}, registry)

    if mid is None:
        return None  # an unknown notification: nothing to answer
    return _error(mid, -32601, f"method not found: {method!r}")


def _write(obj):
    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def main():
    # JSON-RPC is UTF-8; force it regardless of the OS locale (Windows defaults to cp1252,
    # which can't encode some payload characters and would break the protocol channel).
    for stream in (sys.stdin, sys.stdout):
        try:
            stream.reconfigure(encoding="utf-8")
        except AttributeError:
            pass

    registry = {t["name"]: t for t in TOOLS}
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            _write(_error(None, -32700, "parse error"))
            continue
        response = handle(msg, registry)
        if response is not None:
            _write(response)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
