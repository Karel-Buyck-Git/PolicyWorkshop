"""Tiny HCL literal emitter for the Terraform renderer.

``hcl_value`` turns Python data into an HCL object/list/scalar literal suitable as
the argument to ``jsonencode(...)`` (objects use ``"key" = value``). ``hcl_str``
quotes/escapes a string; ``tf_ident`` makes a Terraform-safe local resource name.
Output is deterministic — dict keys keep insertion order (the IR builds them in a
stable order).
"""

_INDENT = "  "


def tf_ident(name):
    """A valid Terraform resource local name (letters, digits, ``_``, ``-``)."""
    return "".join(c if (c.isalnum() or c in "_-") else "_" for c in name)


def hcl_str(value):
    s = str(value).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{s}"'


def hcl_value(obj, level=0):
    if isinstance(obj, bool):
        return "true" if obj else "false"
    if isinstance(obj, (int, float)):
        return str(obj)
    if isinstance(obj, str):
        return hcl_str(obj)
    if obj is None:
        return "null"
    if isinstance(obj, list):
        return _hcl_list(obj, level)
    if isinstance(obj, dict):
        return _hcl_obj(obj, level)
    return hcl_str(str(obj))


def _hcl_list(items, level):
    if not items:
        return "[]"
    if all(isinstance(i, (str, int, float, bool)) for i in items):
        return "[" + ", ".join(hcl_value(i) for i in items) + "]"
    pad = _INDENT * (level + 1)
    inner = ",\n".join(pad + hcl_value(i, level + 1) for i in items)
    return "[\n" + inner + "\n" + _INDENT * level + "]"


def _hcl_obj(d, level):
    if not d:
        return "{}"
    pad = _INDENT * (level + 1)
    lines = [f'{pad}{hcl_str(k)} = {hcl_value(v, level + 1)}' for k, v in d.items()]
    return "{\n" + "\n".join(lines) + "\n" + _INDENT * level + "}"
