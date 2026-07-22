"""Stdlib JSONC reader for the epac-builder.

The producer is deliberately zero-dependency (even YAML uses a hand-rolled subset
parser in ``shared/tiers.py``); the consumer follows suit rather than pulling in
``json5``. ``loads`` strips ``//`` line comments, ``/* */`` block comments and
trailing commas, then defers to ``json.loads``. Comment/comma stripping is
string-aware so ``//`` or ``,`` inside a JSON string value is preserved.
"""
import json
from pathlib import Path


def strip_jsonc(text: str) -> str:
    """Return ``text`` with comments and trailing commas removed (string-aware)."""
    out = []
    i, n = 0, len(text)
    in_str = False
    while i < n:
        ch = text[i]
        if in_str:
            out.append(ch)
            if ch == "\\" and i + 1 < n:        # keep escaped char verbatim
                out.append(text[i + 1])
                i += 2
                continue
            if ch == '"':
                in_str = False
            i += 1
            continue
        # not in a string
        if ch == '"':
            in_str = True
            out.append(ch)
            i += 1
            continue
        if ch == "/" and i + 1 < n and text[i + 1] == "/":   # // line comment
            i += 2
            while i < n and text[i] not in "\r\n":
                i += 1
            continue
        if ch == "/" and i + 1 < n and text[i + 1] == "*":   # /* block comment */
            i += 2
            while i + 1 < n and not (text[i] == "*" and text[i + 1] == "/"):
                i += 1
            i += 2
            continue
        out.append(ch)
        i += 1
    return _strip_trailing_commas("".join(out))


def _strip_trailing_commas(text: str) -> str:
    """Remove commas that immediately precede a closing ``}`` or ``]`` (string-aware)."""
    out = []
    i, n = 0, len(text)
    in_str = False
    while i < n:
        ch = text[i]
        if in_str:
            out.append(ch)
            if ch == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if ch == '"':
                in_str = False
            i += 1
            continue
        if ch == '"':
            in_str = True
            out.append(ch)
            i += 1
            continue
        if ch == ",":
            j = i + 1
            while j < n and text[j] in " \t\r\n":
                j += 1
            if j < n and text[j] in "}]":      # trailing comma -> drop it
                i += 1
                continue
        out.append(ch)
        i += 1
    return "".join(out)


def loads(text: str):
    return json.loads(strip_jsonc(text))


def load(path) -> dict:
    return loads(Path(path).read_text(encoding="utf-8"))
