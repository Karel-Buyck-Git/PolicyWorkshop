"""Deterministic file writers shared by the renderers.

JSON is written with ``indent=2``, ``ensure_ascii=False`` and a trailing newline so
re-runs produce clean diffs (matches the producer's house style). Insertion order is
preserved — callers build dicts in a deterministic order rather than sorting keys, so
EPAC files stay human-readable.
"""
import json
from pathlib import Path


def write_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text, encoding="utf-8")
