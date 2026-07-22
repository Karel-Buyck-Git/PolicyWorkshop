"""Focused JSON Schema validator (stdlib only).

The producer pulls in no third-party libraries, so the consumer hand-rolls the
slice of JSON Schema 2020-12 that the three manifest schemas actually use rather
than depending on ``jsonschema``. Supported keywords: ``type`` (incl. type
arrays), ``properties``, ``required``, ``additionalProperties`` (bool or schema),
``enum``, ``const``, ``pattern``, ``minLength``/``maxLength``, ``minItems``,
``uniqueItems``, ``items``, ``format: date``, ``allOf`` and ``if``/``then``.

``validate`` collects *every* violation and raises one ``ValidationError`` listing
them all with JSON-pointer-ish paths, so the manifest author sees all problems at
once instead of one-per-run.
"""
import re
from datetime import date

_TYPE_CHECKS = {
    "object": lambda v: isinstance(v, dict),
    "array": lambda v: isinstance(v, list),
    "string": lambda v: isinstance(v, str),
    "boolean": lambda v: isinstance(v, bool),
    # JSON has one number type; bool is a subclass of int in Python -> exclude it.
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
}


class ValidationError(Exception):
    """Raised when an instance fails its schema. ``errors`` lists each problem."""

    def __init__(self, label, errors):
        self.errors = errors
        bullets = "\n".join(f"  - {e}" for e in errors)
        super().__init__(f"{label} failed validation ({len(errors)} problem(s)):\n{bullets}")


def validate(instance, schema, label="instance"):
    errors = []
    _walk(instance, schema, "$", errors)
    if errors:
        raise ValidationError(label, errors)


def _type_matches(value, types):
    types = types if isinstance(types, list) else [types]
    return any(_TYPE_CHECKS.get(t, lambda _v: True)(value) for t in types)


def _walk(value, schema, path, errors):
    if not isinstance(schema, dict):
        return

    if "type" in schema and not _type_matches(value, schema["type"]):
        errors.append(f"{path}: expected type {schema['type']!r}, got {_kind(value)}")
        return  # further checks assume the type held

    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: must equal {schema['const']!r}")

    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: {value!r} is not one of {schema['enum']}")

    if isinstance(value, str):
        _check_string(value, schema, path, errors)
    if isinstance(value, list):
        _check_array(value, schema, path, errors)
    if isinstance(value, dict):
        _check_object(value, schema, path, errors)

    for sub in schema.get("allOf", []):
        _walk(value, sub, path, errors)

    if "if" in schema and not _has_errors(value, schema["if"]):
        if "then" in schema:
            _walk(value, schema["then"], path, errors)
        # 'else' unused by the current schemas; add here if needed.


def _check_string(value, schema, path, errors):
    if "minLength" in schema and len(value) < schema["minLength"]:
        errors.append(f"{path}: shorter than minLength {schema['minLength']}")
    if "maxLength" in schema and len(value) > schema["maxLength"]:
        errors.append(f"{path}: longer than maxLength {schema['maxLength']}")
    if "pattern" in schema and not re.search(schema["pattern"], value):
        errors.append(f"{path}: {value!r} does not match pattern {schema['pattern']!r}")
    if schema.get("format") == "date":
        try:
            date.fromisoformat(value)
        except ValueError:
            errors.append(f"{path}: {value!r} is not a valid date (YYYY-MM-DD)")


def _check_array(value, schema, path, errors):
    if "minItems" in schema and len(value) < schema["minItems"]:
        errors.append(f"{path}: fewer than minItems {schema['minItems']}")
    if schema.get("uniqueItems") and _has_dupes(value):
        errors.append(f"{path}: items must be unique")
    item_schema = schema.get("items")
    if isinstance(item_schema, dict):
        for i, item in enumerate(value):
            _walk(item, item_schema, f"{path}[{i}]", errors)


def _check_object(value, schema, path, errors):
    props = schema.get("properties", {})
    for key in schema.get("required", []):
        if key not in value:
            errors.append(f"{path}: missing required property {key!r}")
    addl = schema.get("additionalProperties", True)
    for key, val in value.items():
        child = f"{path}.{key}"
        if key in props:
            _walk(val, props[key], child, errors)
        elif addl is False:
            errors.append(f"{child}: unexpected property (additionalProperties is false)")
        elif isinstance(addl, dict):
            _walk(val, addl, child, errors)


def _has_errors(value, schema):
    """True if ``value`` violates ``schema`` (used to evaluate ``if``)."""
    local = []
    _walk(value, schema, "$", local)
    return bool(local)


def _has_dupes(items):
    seen = []
    for it in items:
        if it in seen:
            return True
        seen.append(it)
    return False


def _kind(value):
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, dict):
        return "object"
    if isinstance(value, list):
        return "array"
    if isinstance(value, str):
        return "string"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if value is None:
        return "null"
    return type(value).__name__
