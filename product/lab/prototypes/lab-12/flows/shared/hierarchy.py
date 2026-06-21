"""Single parser for the authored domain hierarchy.

`config/azure-domain-hierachy.md` is the ONE human-authored source of truth.
Every producer script imports these helpers so the parse logic never diverges
(no second copy, no second parser = no drift).
"""
from pathlib import Path


def load_domain_map(hierarchy_path) -> dict[str, str]:
    """Return {category: domain}.

    Top-level domains are column-0 bullets ('- Domain'); their child categories
    are indented bullets ('  - Category').
    """
    mapping: dict[str, str] = {}
    current_domain: str | None = None
    for raw in Path(hierarchy_path).read_text(encoding="utf-8").splitlines():
        if raw.startswith("- "):
            current_domain = raw[2:].strip()
        elif raw.startswith("  - ") and current_domain:
            category = raw[4:].strip()
            if category:
                mapping[category] = current_domain
    return mapping


def load_hierarchy(hierarchy_path) -> dict[str, list[str]]:
    """Return {domain: [categories...]} preserving document order."""
    h: dict[str, list[str]] = {}
    current_domain: str | None = None
    for raw in Path(hierarchy_path).read_text(encoding="utf-8").splitlines():
        if raw.startswith("- "):
            current_domain = raw[2:].strip()
            h.setdefault(current_domain, [])
        elif raw.startswith("  - ") and current_domain:
            category = raw[4:].strip()
            if category:
                h[current_domain].append(category)
    return h
