"""Deterministic file writers shared by the renderers.

JSON is written with ``indent=2``, ``ensure_ascii=False`` and a trailing newline so
re-runs produce clean diffs (matches the producer's house style). Insertion order is
preserved — callers build dicts in a deterministic order rather than sorting keys, so
EPAC files stay human-readable.

Every write passes ``newline="\\n"`` (#52). Without it ``Path.write_text`` applies the
platform's newline translation, so the same manifest + catalogue rendered on Windows and
on Linux produce different *bytes* — which breaks the byte-for-byte contract
``examples/contoso/verify.sh`` enforces against LF fixtures, and makes
``assemble_scaffold``'s "deterministic transform" promise true only per-host.
"""
import json
from pathlib import Path


def write_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8", newline="\n")


def write_text(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text, encoding="utf-8", newline="\n")
