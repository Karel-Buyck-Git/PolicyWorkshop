"""Deploy-readiness gate for the epac-builder (``--strict``).

Structure validation (``manifest.schema.json``) proves the manifest is *well-formed*,
but it cannot prove it is *filled in*: many fields are free strings, so an unedited
``<REPLACE: …>`` placeholder — a selector, a location, a Log Analytics id, a bound
parameter value, a metadata field — sails through and renders **verbatim** into the
package, where Azure rejects it only at deploy time. Likewise a selection with no
``managementGroup``/``scope`` resolves to :data:`~epac_builder.mgscopes.PLACEHOLDER_SCOPE`,
which is a ``[warn]`` today, not an error.

``--strict`` turns the assembler into a pre-deploy gate: it fails the build when any
such placeholder survives. Without it, partial scaffolds still build during authoring
(a ``<REPLACE:>`` value binds as-is; a placeholder scope only warns).
"""
from epac_builder.bind import PLACEHOLDER_PREFIX
from epac_builder.mgscopes import PLACEHOLDER_SCOPE


class StrictGateError(Exception):
    """The manifest is not deploy-ready: residual placeholders would ship. Fail-fast."""

    def __init__(self, problems):
        self.problems = problems
        bullets = "\n".join(f"  - {p}" for p in problems)
        super().__init__(
            f"--strict: manifest is not deploy-ready ({len(problems)} placeholder(s) "
            f"survive into output):\n{bullets}\n"
            "Fill each value (and set selection.managementGroup or selection.scope) and "
            "re-run, or drop --strict while still authoring."
        )


def _is_placeholder(value):
    return isinstance(value, str) and value.lstrip().startswith(PLACEHOLDER_PREFIX)


def _walk(node, path, out):
    """Collect every ``<REPLACE: …>`` string (and placeholder dict key) under ``node``."""
    if _is_placeholder(node):
        out.append(f"{path} = {node!r}")
    elif isinstance(node, dict):
        for key, val in node.items():
            if _is_placeholder(key):
                out.append(f"{path} has unfilled key {key!r}")
            _walk(val, f"{path}.{key}", out)
    elif isinstance(node, list):
        for i, val in enumerate(node):
            _walk(val, f"{path}[{i}]", out)


def residual_placeholders(manifest, ir):
    """List every deploy-blocking placeholder: unfilled ``<REPLACE:>`` in the manifest
    plus any assignment scope that fell back to the placeholder management group."""
    problems = []
    _walk(manifest, "$", problems)
    for a in ir.get("assignments", []):
        for selector, scopes in (a.get("scopes") or {}).items():
            if PLACEHOLDER_SCOPE in scopes:
                problems.append(
                    f"selection '{a['group']}' resolved to the placeholder scope for "
                    f"selector '{selector}' — set selection.managementGroup or "
                    f"selection.scope, or remove the selection"
                )
    return problems
