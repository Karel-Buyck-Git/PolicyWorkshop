"""Read the released-version record out of ``catalogue/CHANGELOG.md`` (#48).

``catalogueVersion`` defaults to the UTC date, so two releases in the same UTC day
collide on one label. That is not cosmetic: the assembler's version gate is an exact
string compare (``assemble_scaffold.py``), so a manifest pinned to the morning
catalogue builds green against the evening one.

``CHANGELOG.md`` is the record of what was actually *released* — each entry carries
its version label and the ``contentHash`` that label stood for — which makes it the
one artifact that can answer "has this label already been published, and did it mean
something else?". The producer consults it before finalizing a stamp
(``apply_overlays.py``) and again before writing an entry
(``tools/catalogue_changelog.py``), so a label can never come to mean two things.

Parses the format ``tools/catalogue_changelog.py`` writes; entries it cannot read a
hash from are recorded as ``None`` (a label reuse is still reported, without the
old/new pair). Stdlib only.
"""
import re
from pathlib import Path

_HEADING = re.compile(r"^##\s+(\S+)")
_CONTENT_HASH = re.compile(r"contentHash\s+`([^`]+)`")


def released_versions(changelog_path) -> dict:
    """Map ``{version label: contentHash or None}`` for every entry in the changelog.

    Returns ``{}`` when the changelog does not exist yet (the first release).
    """
    p = Path(changelog_path)
    if not p.exists():
        return {}
    out, current = {}, None
    for line in p.read_text(encoding="utf-8").splitlines():
        m = _HEADING.match(line)
        if m:
            current = m.group(1)
            out.setdefault(current, None)
            continue
        if current and out.get(current) is None:
            h = _CONTENT_HASH.search(line)
            if h:
                out[current] = h.group(1)
    return out


def version_collision(version, content_hash, changelog_path) -> str | None:
    """Explain the collision if ``version`` was already released for *different* content.

    Returns ``None`` when the label is unused, or when it was released for exactly this
    ``content_hash`` — re-stamping identical content under its own label is a harmless
    idempotent re-run, and is how a regenerate-and-verify check works.
    """
    released = released_versions(changelog_path)
    if version not in released:
        return None
    previous = released[version]
    if previous == content_hash:
        return None
    was = f"contentHash `{previous}`" if previous else "a contentHash this file does not record"
    return (
        f"catalogue version label '{version}' was already released with {was}, but this "
        f"build produces `{content_hash}`. One label would mean two different catalogues, "
        f"and the assembler's version pin is an exact string compare — a manifest pinned "
        f"to the released '{version}' would build green against this one. Re-run phase 3 "
        f"with an explicit label (e.g. --version {next_free_label(version, released)})."
    )


def next_free_label(version, released) -> str:
    """First ``<version>.<n>`` suffix not already released — format-agnostic on purpose.

    The label is a date today but the producer accepts any string, so this counts up
    rather than assuming it can increment the last component (which for ``2026.07.25``
    would silently propose *tomorrow's* date).
    """
    n = 1
    while f"{version}.{n}" in released:
        n += 1
    return f"{version}.{n}"
