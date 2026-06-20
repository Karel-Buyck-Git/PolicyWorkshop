"""Single source of truth for lab-11 catalogue naming.

Both the producer (catalogue-builder) and the consumer (epac-builder) import these
builders so a customer deploys exactly the names QC validated. Names are
**brand-neutral** (no `company`) and sized to the Azure hard limits in
`docs/epac-arm-hard-limits.md`. One canonical group name is used for the policy set,
the assignment and the files:

    name (set / assignment) <domain>-<tier>-<abbr>         (<=24)
    exemption name          <name>-ex                      (<=64)
    displayName             <Domain> <Tier> — <Category>   (<=128, readable)
    nodeName                /<domain>/<tier>/<category>/

Tier codes: essential->esn, professional->pro, enterprise->ent. Category
abbreviations are authored in `config/azure-category-abbreviation.md` (CAF-aligned
where the category is a resource type, a readable shortname otherwise). The
human-readable detail lives in `displayName`, per the hard-limits guidance.
"""
from functools import lru_cache

from shared.mdtable import slugify
from shared.paths import CATEGORY_ABBREV_FILE

# Azure hard limits — see docs/epac-arm-hard-limits.md
ASSIGNMENT_NAME_MAX = 24
DEFINITION_NAME_MAX = 64          # policy / policy set / exemption name
DISPLAY_NAME_MAX = 128
DESCRIPTION_MAX = 512

TIER_CODE = {"essential": "esn", "professional": "pro", "enterprise": "ent"}
TIER_DISPLAY = {"essential": "Essential", "professional": "Professional", "enterprise": "Enterprise"}


def tier_code(tier: str) -> str:
    key = (tier or "").strip().lower()
    if key not in TIER_CODE:
        raise ValueError(f"unknown tier {tier!r} (expected essential/professional/enterprise)")
    return TIER_CODE[key]


def tier_display(tier: str) -> str:
    return TIER_DISPLAY[(tier or "").strip().lower()]


@lru_cache(maxsize=1)
def category_abbreviations() -> dict:
    """Parse the authored `Domain | Category | Abbreviation | Basis` markdown table."""
    mapping: dict[str, str] = {}
    header = None
    for line in CATEGORY_ABBREV_FILE.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if header is None:
            header = [c.lower() for c in cells]
            continue
        if set("".join(cells)) <= set("-: "):        # separator row
            continue
        row = dict(zip(header, cells))
        cat, abbr = row.get("category"), row.get("abbreviation")
        if cat and abbr:
            mapping[cat] = abbr
    return mapping


def category_abbr(category: str) -> str:
    key = slugify(category)
    mapping = category_abbreviations()
    if key not in mapping:
        raise KeyError(
            f"no abbreviation for category {category!r} ({key}) in "
            f"{CATEGORY_ABBREV_FILE.name}; add it there and re-run.")
    return mapping[key]


def name(domain: str, tier: str, category: str) -> str:
    """The canonical group name `<domain>-<tier>-<abbr>` (<=24), used for the policy
    set, the assignment and the file basenames."""
    return f"{slugify(domain)}-{tier_code(tier)}-{category_abbr(category)}"


def exemption_name(group_name: str) -> str:
    return f"{group_name}-ex"


def display_name(domain: str, tier: str, category: str) -> str:
    """Brand-neutral, human-readable: `<Domain> <Tier> — <Category>` (tier spelled out)."""
    return f"{domain} {tier_display(tier)} — {category}"


def node_name(domain: str, tier: str, category: str, suffix: str = "") -> str:
    """Brand-neutral EPAC nodeName path (no customer/brand segment)."""
    base = f"/{slugify(domain)}/{slugify(tier)}/{slugify(category)}/"
    return f"{base}{suffix}/" if suffix else base
