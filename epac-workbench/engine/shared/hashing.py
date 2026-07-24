"""Reproducible content hashing for catalogue provenance (#27, 27e).

The catalogue's ``inputs.*`` / ``tools.*`` fingerprints and its ``contentHash`` must
be **identical on every platform** — otherwise a hash flaps between a Windows (CRLF)
and a Linux/CI (LF) checkout with no real change, which silently corrupts the
provenance record (a hash moved for a reason nothing explains). These helpers hash
the **newline-normalized** bytes so the result depends only on file *content*, not on
the checkout's line-ending policy.

All catalogue inputs and outputs are text (``.py`` / ``.yaml`` / ``.json`` / ``.md``),
so normalizing unconditionally is safe. Single source of truth — both producer phases
(``create_initiatives.py``, ``apply_overlays.py``) import from here so the two hashes
can never drift.
"""
import hashlib
from pathlib import Path


def _normalize(data: bytes) -> bytes:
    """CRLF / lone-CR -> LF, so the hash is independent of checkout line endings."""
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def sha256_file(path) -> str:
    """``sha256:<hex>`` of one file's normalized bytes, or ``""`` if it is absent."""
    p = Path(path)
    if not p.exists():
        return ""
    return "sha256:" + hashlib.sha256(_normalize(p.read_bytes())).hexdigest()


def content_hash(root, exclude) -> str:
    """``sha256:<hex>`` over every file under ``root`` (path + normalized bytes),
    skipping any whose name is in ``exclude`` (the stamp files that would be circular)."""
    h = hashlib.sha256()
    for p in sorted(Path(root).rglob("*")):
        if not p.is_file() or p.name in exclude:
            continue
        rel = str(p.relative_to(root)).replace("\\", "/")
        h.update(rel.encode("utf-8")); h.update(b"\x00")
        h.update(_normalize(p.read_bytes())); h.update(b"\x00")
    return "sha256:" + h.hexdigest()
