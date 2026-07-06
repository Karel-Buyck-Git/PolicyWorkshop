"""Tool registry for the epac-builder MCP server.

Each tool module exposes a ``TOOL`` dict: ``{name, description, inputSchema, handler}``.
Adding a future #17 tool is one new module here plus one line in ``TOOLS``. The server
(``mcp_server/server.py``) has already put the ``flows/`` root on ``sys.path`` before it
imports this package, so the tool modules can ``import`` the engine directly.
"""
from mcp_server.tools import validate_manifest

TOOLS = [
    validate_manifest.TOOL,
]
