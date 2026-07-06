"""MCP tool: ``validate_manifest`` — wraps the epac-builder ``--check`` / ``--check --strict``.

Validates a customer manifest against the schemas (and, with ``strict=true``, the
deploy-ready gate) and returns the result as *structured data* — the CLI flattens the
same detail into a single stderr string. Writes nothing and, unlike the CLI, never
mutates the manifest (``write_back=False`` — see ``assemble_scaffold.resolve_pac_owner_id``).

A validation *failure* is a normal result (``valid: false`` + the problem list, ``isError``
false); ``isError`` is reserved for real tool failures (missing path, unexpected crash).
"""
from pathlib import Path

# catalogue-builder/ root — relative manifest paths resolve against it, so the tool behaves
# identically regardless of the working directory the MCP client launches the server from.
CB_ROOT = Path(__file__).resolve().parents[3]

from epac_builder import validate
from epac_builder.assemble_scaffold import assemble, AssemblerError
from epac_builder.bind import BindError
from epac_builder.catalogue import ResolveError
from epac_builder.mgscopes import HierarchyError
from epac_builder.strict import StrictGateError

NAME = "validate_manifest"

DESCRIPTION = (
    "Validate an epac-builder customer manifest. Runs the same checks as "
    "`assemble_scaffold.py --check` (structure + build-gate schemas); with strict=true it also "
    "runs the deploy-ready gate (`--check --strict`), failing if any <REPLACE:> placeholder or "
    "placeholder management-group scope survives into the output. Read-only: writes no files and "
    "never mutates the manifest. Returns structured JSON — on success the resolved initiative "
    "count and any warnings; on failure the exact schema errors or the list of residual "
    "placeholders."
)

INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "manifest": {
            "type": "string",
            "description": "path to the customer manifest (.jsonc/.json); relative paths resolve "
                           "against the catalogue-builder/ root, or pass an absolute path",
        },
        "strict": {
            "type": "boolean",
            "default": False,
            "description": "also run the deploy-ready gate: fail if any <REPLACE:> value or "
                           "placeholder scope survives",
        },
    },
    "required": ["manifest"],
    "additionalProperties": False,
}


def handler(args):
    """(payload, is_error). is_error only for tool failures, not validation failures."""
    manifest = args.get("manifest")
    if not manifest:
        return {"error": "missing required argument 'manifest'"}, True
    strict = bool(args.get("strict", False))

    path = Path(manifest)
    if not path.is_absolute():
        path = CB_ROOT / path
    if not path.exists():
        return {"error": f"manifest not found: {manifest}"}, True

    logs = []  # capture engine [warn]/[check]/[pacOwnerId]/… lines off stdout
    try:
        ir = assemble(str(path), check=True, strict=strict, write_back=False, log=logs.append)
    except validate.ValidationError as e:
        stage = str(e).split(" failed validation")[0]
        return {"valid": False, "stage": stage, "errors": e.errors}, False
    except StrictGateError as e:
        return {"valid": False, "strictProblems": e.problems}, False
    except (AssemblerError, ResolveError, BindError, HierarchyError) as e:
        return {"valid": False, "error": str(e)}, False

    warnings = [ln[len("[warn] "):] for ln in logs if ln.startswith("[warn] ")]
    note = next((ln[len("[pacOwnerId] "):] for ln in logs if ln.startswith("[pacOwnerId] ")), None)
    return {
        "valid": True,
        "strict": strict,
        "initiativesResolved": len(ir["initiatives"]),
        "warnings": warnings,
        "note": note,
    }, False


TOOL = {
    "name": NAME,
    "description": DESCRIPTION,
    "inputSchema": INPUT_SCHEMA,
    "handler": handler,
}
