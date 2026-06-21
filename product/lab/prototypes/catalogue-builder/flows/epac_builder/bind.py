"""Parameter binding + effect posture for the epac-builder.

For each resolved group the catalogue provides an *assignment scaffold* whose
``parameters`` carry ``<REPLACE: key>`` mocks for every required (bubbled-up)
parameter. ``bind_parameters`` fills those from the manifest's
``bindings.defaults`` (global) merged with ``bindings.overrides["<domain>/<category>"]``
(per-group), failing fast on any unbound mock and type-checking the value against
the policyset's parameter schema.

``apply_posture`` decides the effect stance per group: ``hardened`` keeps the baked
effects, ``Audit`` softens every member effect to ``Audit``; surgical
``effectOverrides`` (per ``policyDefinitionReferenceId``) are applied last.
"""

PLACEHOLDER_PREFIX = "<REPLACE:"


class BindError(Exception):
    """A required parameter is unbound or a value fails its type check (fail-fast)."""


def is_placeholder(value):
    return isinstance(value, str) and value.lstrip().startswith(PLACEHOLDER_PREFIX)


def required_param_keys(assignment):
    """Keys in an assignment scaffold whose value is still a ``<REPLACE: …>`` mock."""
    return [k for k, v in (assignment.get("parameters") or {}).items() if is_placeholder(v)]


def _merged_bindings(group, bindings):
    defaults = dict(bindings.get("defaults") or {})
    dom = _slugof(group, 0)
    cat = _slugof(group, 2)
    override = (bindings.get("overrides") or {}).get(f"{dom}/{cat}", {})
    defaults.update(override)
    return defaults


def _slugof(group, i):
    return group["_slug"][i]


def bind_parameters(artifacts, bindings):
    """Return the bound ``parameters`` dict for a group, fail-fast on gaps."""
    group = artifacts["group"]
    assignment = artifacts["assignment"]
    pset_params = (artifacts["policyset"].get("properties", {}) or {}).get("parameters", {})
    values = _merged_bindings(group, bindings)

    bound = {}
    for key, val in (assignment.get("parameters") or {}).items():
        if is_placeholder(val):
            if key not in values:
                raise BindError(
                    f"group '{group['name']}': required parameter '{key}' has no binding. "
                    f"Add it to bindings.defaults (or bindings.overrides['{_slugof(group,0)}/"
                    f"{_slugof(group,2)}']) in the manifest."
                )
            resolved = values[key]
        else:
            resolved = val
        _typecheck(group["name"], key, resolved, pset_params.get(key, {}))
        bound[key] = resolved
    return bound


_JSON_TYPE = {
    "String": str, "Integer": int, "Float": (int, float), "Boolean": bool,
    "Array": list, "Object": dict, "DateTime": str,
}


def _typecheck(group_name, key, value, schema):
    declared = schema.get("type")
    expected = _JSON_TYPE.get(declared)
    if expected and not isinstance(value, expected):
        raise BindError(
            f"group '{group_name}': parameter '{key}' expects {declared}, got "
            f"{type(value).__name__} ({value!r})."
        )
    allowed = schema.get("allowedValues")
    if allowed is not None and value not in allowed:
        raise BindError(
            f"group '{group_name}': parameter '{key}' value {value!r} is not in "
            f"allowedValues {allowed}."
        )


def resolve_posture(group, selection_item, environments):
    """One posture per group: selection override, else the environments' enforcement.

    Returns ``(posture, warning_or_None)``. When environments disagree and the
    selection sets no override, the manifest's first environment wins (deterministic)
    and a warning is surfaced.
    """
    if selection_item and selection_item.get("enforcement"):
        return selection_item["enforcement"], None
    distinct = {e["enforcement"] for e in environments}
    if len(distinct) == 1:
        return next(iter(distinct)), None
    chosen = environments[0]["enforcement"]
    warn = (f"group '{group['name']}': environments disagree on enforcement "
            f"({sorted(distinct)}); using first environment's '{chosen}'.")
    return chosen, warn


def apply_posture(policyset, posture, effect_overrides):
    """Mutate a *copy* of the policyset's member effects for the chosen posture.

    ``posture == 'Audit'`` softens every member that exposes an ``effect`` parameter
    to ``Audit``; ``hardened`` leaves baked effects untouched. ``effect_overrides`` is
    the manifest's per-member list ``[{policyDefinitionReferenceId, effect}, …]`` already
    filtered to this group.
    """
    members = policyset.get("properties", {}).get("policyDefinitions", [])
    override_by_ref = {o["policyDefinitionReferenceId"]: o["effect"] for o in effect_overrides}
    for m in members:
        params = m.setdefault("parameters", {})
        if posture == "Audit" and "effect" in params:
            params["effect"] = {"value": "Audit"}
        ref = m.get("policyDefinitionReferenceId")
        if ref in override_by_ref and "effect" in params:
            params["effect"] = {"value": override_by_ref[ref]}
    return policyset
