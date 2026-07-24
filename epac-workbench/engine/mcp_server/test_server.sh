#!/usr/bin/env bash
#
# Smoke test for the epac-builder MCP server (stdio).
#
# Feeds a canned newline-delimited JSON-RPC session at server.py and asserts the
# responses. Deterministic and stdlib-only (a Python parser inline), matching the
# house testing style (no pytest). Runnable from anywhere — it locates its own
# epac-workbench/ root and drives the committed contoso manifest, which passes
# a plain --check but FAILS --strict on its intentionally-unmapped tags selection.
#
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CB="$(cd "$HERE/../.." && pwd)"   # epac-workbench/
cd "$CB"

MANIFEST="examples/contoso/manifests/manifest.example.jsonc"

session() {
  printf '%s\n' \
    '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{}}}' \
    '{"jsonrpc":"2.0","method":"notifications/initialized"}' \
    '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' \
    "{\"jsonrpc\":\"2.0\",\"id\":3,\"method\":\"tools/call\",\"params\":{\"name\":\"validate_manifest\",\"arguments\":{\"manifest\":\"$MANIFEST\"}}}" \
    "{\"jsonrpc\":\"2.0\",\"id\":4,\"method\":\"tools/call\",\"params\":{\"name\":\"validate_manifest\",\"arguments\":{\"manifest\":\"$MANIFEST\",\"strict\":true}}}" \
    '{"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"validate_manifest","arguments":{"manifest":"does/not/exist.jsonc"}}}'
}

OUT="$(mktemp)"
trap 'rm -f "$OUT"' EXIT
session | python engine/mcp_server/server.py > "$OUT"

# Parse the captured responses. The script comes from the heredoc; the response file is
# argv[1] — so stdin stays free (piping into `python - <<PY` would feed it the heredoc,
# not the data).
python - "$OUT" <<'PY'
import json, sys

resp = {}
with open(sys.argv[1], encoding="utf-8") as fh:
    for line in fh:
        line = line.strip()
        if not line:
            continue
        try:
            m = json.loads(line)
        except json.JSONDecodeError:
            sys.exit(f"[test] FAIL: non-JSON on stdout (protocol contamination): {line!r}")
        resp[m.get("id")] = m

def fail(msg):
    sys.exit(f"[test] FAIL: {msg}")

def result(i, what):
    """The ``result`` object for request id ``i``, or a legible FAIL.

    A server that dies partway through — or answers with a JSON-RPC error object,
    which carries ``error`` and no ``result`` — must produce this script's own
    ``[test] FAIL: …`` line, not a KeyError traceback pointing at the harness. CI
    reads these messages (#30).
    """
    m = resp.get(i)
    if m is None:
        fail(f"no response for id {i} ({what}) — the server exited or never answered "
             f"(ids seen: {sorted(k for k in resp if k is not None)})")
    if "result" not in m:
        fail(f"id {i} ({what}) returned no result: {m.get('error', m)}")
    return m["result"]

# 1. initialize
if result(1, "initialize").get("serverInfo", {}).get("name") != "epac-builder":
    fail("initialize: unexpected serverInfo")

# 2. tools/list advertises validate_manifest
names = [t["name"] for t in result(2, "tools/list")["tools"]]
if "validate_manifest" not in names:
    fail(f"tools/list missing validate_manifest (got {names})")

# 3. non-strict check on the contoso manifest -> valid
r3 = result(3, "validate_manifest, non-strict")
p3 = json.loads(r3["content"][0]["text"])
if r3["isError"]:
    fail("non-strict call set isError")
if not p3.get("valid"):
    fail(f"non-strict expected valid:true, got {p3}")

# 4. strict gate -> valid:false, names the tags selection, but NOT a tool error
r4 = result(4, "validate_manifest, strict")
p4 = json.loads(r4["content"][0]["text"])
if r4["isError"]:
    fail("strict validation failure must be isError:false (a normal result)")
if p4.get("valid"):
    fail("strict expected valid:false on the unmapped selection")
if "tags" not in json.dumps(p4):
    fail(f"strict expected a 'tags' problem, got {p4}")

# 5. bad path -> tool error
if not result(5, "bad manifest path")["isError"]:
    fail("missing manifest path should set isError:true")

print("[test] OK - 5/5 assertions passed (initialize, tools/list, check, strict gate, bad path)")
PY
