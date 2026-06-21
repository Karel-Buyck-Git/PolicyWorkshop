"""Catalogue access + selection resolution for the epac-builder.

Reads only the published catalogue (``index.json`` + the ``initiatives/`` tree),
never ``config/`` or ``docs/`` — the consumer has no dependency on the producer's
authored inputs. ``index.json`` carries the group list whose ``dir`` field encodes
the slug triple ``initiatives/<domain>/<tier>/<category>`` the manifest selects on.

Resolution rules (confirmed):
- tiers are cumulative — ``professional`` pulls essential+professional, ``enterprise``
  pulls all three.
- ``category:"*"`` expands to every category present in the domain for the rolled-up
  tiers.
- the ``undefined`` domain is **never consumable**: a selection naming it is a hard
  error; ``*`` expansion never reaches it (it lives under its own domain slug).
- a selection that resolves to **zero** groups is a hard error with a message naming
  the offending selection.
"""
import json
from pathlib import Path

TIER_ORDER = ["essential", "professional", "enterprise"]
UNDEFINED_DOMAIN = "undefined"


class ResolveError(Exception):
    """A selection could not be resolved against the catalogue (fail-fast)."""


def tier_rollup(tier):
    """Cumulative tiers up to and including ``tier`` (essential ⊆ … ⊆ enterprise)."""
    return TIER_ORDER[: TIER_ORDER.index(tier) + 1]


class Catalogue:
    def __init__(self, catalogue_dir):
        self.dir = Path(catalogue_dir)
        index_file = self.dir / "index.json"
        if not index_file.exists():
            raise ResolveError(f"catalogue index not found: {index_file}")
        self.index = json.loads(index_file.read_text(encoding="utf-8"))
        self.version = self.index.get("catalogueVersion", "")
        self.by_triple = {}            # (domain, tier, category) slug -> group record
        for g in self.index.get("groups", []):
            parts = g["dir"].split("/")          # initiatives/<domain>/<tier>/<category>
            if len(parts) != 4:
                continue
            _, dom, tier, cat = parts
            g = dict(g, _slug=(dom, tier, cat))
            self.by_triple[(dom, tier, cat)] = g
        self.domains = sorted({d for (d, _t, _c) in self.by_triple})

    def categories_in(self, domain, tiers):
        """All category slugs present in ``domain`` for any tier in ``tiers``."""
        return sorted({c for (d, t, c) in self.by_triple if d == domain and t in tiers})

    def resolve(self, selection):
        """Return the deduped, ordered list of group records the selection picks.

        ``selection`` is the manifest's list of ``{domain, category, tier}`` slug dicts.
        """
        picked = []
        seen = set()
        for sel in selection:
            dom, cat, tier = sel["domain"], sel["category"], sel["tier"]
            label = f"{dom}/{tier}/{cat}"

            if dom == UNDEFINED_DOMAIN:
                raise ResolveError(
                    f"selection '{label}': the 'undefined' domain is excluded from the "
                    f"epac-builder. Those policies have no domain assigned in the catalogue "
                    f"and must be given a real domain (producer follow-up) before they can be "
                    f"consumed. Remove this selection."
                )
            if dom not in self.domains:
                raise ResolveError(
                    f"selection '{label}': unknown domain '{dom}'. "
                    f"Available domains: {', '.join(self.domains)}."
                )

            tiers = tier_rollup(tier)
            if cat == "*":
                cats = self.categories_in(dom, tiers)
                matched = [self.by_triple[(dom, t, c)]
                           for c in cats for t in tiers if (dom, t, c) in self.by_triple]
                if not matched:
                    raise ResolveError(
                        f"selection '{label}': domain '{dom}' has no categories at tier "
                        f"'{tier}' or below. Nothing to assemble — remove or change this "
                        f"selection."
                    )
            else:
                matched = [self.by_triple[(dom, t, cat)]
                           for t in tiers if (dom, t, cat) in self.by_triple]
                if not matched:
                    avail = self.categories_in(dom, tiers)
                    hint = (f"categories available in '{dom}' at this tier: {', '.join(avail)}"
                            if avail else f"domain '{dom}' has no groups at tier '{tier}' or below")
                    raise ResolveError(
                        f"selection '{label}': no group exists for category '{cat}' in domain "
                        f"'{dom}' at tier '{tier}' (or below). {hint}."
                    )

            for g in matched:
                if g["name"] not in seen:
                    seen.add(g["name"])
                    picked.append(g)
        return picked

    def group_dir(self, group):
        return self.dir / group["dir"]

    def load_artifacts(self, group):
        """Load a group's policyset/assignment (+ optional roles) JSON from disk."""
        base = self.group_dir(group)
        name = group["name"]

        def _read(suffix, required):
            p = base / f"{name}.{suffix}"
            if not p.exists():
                if required:
                    raise ResolveError(f"group '{name}': missing artifact {p}")
                return None
            return json.loads(p.read_text(encoding="utf-8"))

        return {
            "group": group,
            "policyset": _read("policyset.json", True),
            "assignment": _read("assignment.json", True),
            "roles": _read("roles.json", False),
        }
