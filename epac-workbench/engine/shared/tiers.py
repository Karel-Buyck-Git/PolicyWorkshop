"""Single source + engine for policy-tier classification.

`config/tier-rules.yaml` is the ONE human-authored definition of the tier rules.
Both producer steps import `classify()` from here (extract_policies.py for the
first pass, enrich_policies.py for the final pass), so there is one definition of
the rules and no second copy can drift — the same principle hierarchy.py applies
to the domain hierarchy.

The YAML is parsed by a small built-in subset parser (`_parse_yaml`) rather than
PyYAML, to keep the engine/ pipeline dependency-free (stdlib only). It supports
exactly what tier-rules.yaml uses: comments, nested mappings, block lists, and
scalar strings — nothing else.

Keyword conventions (see tier-rules.yaml for the authored docs):
  * whole-word, case-insensitive match
  * spaces and hyphens are interchangeable and optional ("zone-redundant"
    matches "zone redundant" / "zoneredundant")
  * trailing "*" = stem/prefix ("encrypt*" -> encryption, encrypted)
  * "..." = an arbitrary gap ("audit ... should be enabled")
"""
import re
from pathlib import Path

# Fixed evaluation order. The authored YAML may list tiers in any order; the
# engine always tries the most specific tier first.
TIER_PRIORITY = ["Enterprise", "Professional", "Essential"]


# ---------------------------------------------------------------------------
# Minimal YAML-subset parser
#
# Indentation-based recursive descent. Handles: full-line and inline "#"
# comments, blank lines, "key:" (nested block), "key: scalar", "- scalar"
# block lists, and optionally quoted scalars. Anything else raises, so an
# unsupported YAML feature fails loudly instead of being silently mis-parsed.
# ---------------------------------------------------------------------------

def _strip_comment(line: str) -> str:
    """Remove a trailing/inline '#' comment that is not inside quotes."""
    in_quote = ""
    for i, ch in enumerate(line):
        if in_quote:
            if ch == in_quote:
                in_quote = ""
        elif ch in "'\"":
            in_quote = ch
        elif ch == "#" and (i == 0 or line[i - 1] in " \t"):
            return line[:i]
    return line


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        return value[1:-1]
    return value


def _parse_yaml(text: str):
    """Parse the supported YAML subset into nested dict/list/str structures."""
    rows: list[tuple[int, str]] = []
    for raw in text.splitlines():
        body = _strip_comment(raw)
        if not body.strip():
            continue
        indent = len(body) - len(body.lstrip(" "))
        rows.append((indent, body.strip()))

    pos = 0  # shared cursor into rows

    def parse_block(min_indent: int):
        nonlocal pos
        indent = rows[pos][0]
        if rows[pos][1].startswith("- "):
            items = []
            while pos < len(rows) and rows[pos][0] == indent and rows[pos][1].startswith("- "):
                items.append(_unquote(rows[pos][1][2:]))
                pos += 1
            return items

        mapping: dict[str, object] = {}
        while pos < len(rows) and rows[pos][0] == indent:
            line = rows[pos][1]
            if ":" not in line:
                raise ValueError(f"tier-rules.yaml: expected 'key:' but got {line!r}")
            key, _, inline = line.partition(":")
            key = key.strip()
            inline = inline.strip()
            pos += 1
            if inline:
                mapping[key] = _unquote(inline)
            elif pos < len(rows) and rows[pos][0] > indent:
                mapping[key] = parse_block(indent + 1)
            else:
                mapping[key] = {}
        return mapping

    return parse_block(0)


# ---------------------------------------------------------------------------
# Keyword -> regex compilation
# ---------------------------------------------------------------------------

def _compile_keyword(keyword: str) -> re.Pattern:
    """Turn one authored keyword into a compiled, case-insensitive matcher.

    A keyword is one or more segments separated by '...'. Each segment is matched
    as a whole word/phrase (leading word boundary). Within a segment:
      * a space matches a run of whitespace only — so "private endpoint" does NOT
        fire on the hyphenated "private-endpoint" found in URL slugs;
      * a hyphen matches a space OR a hyphen — so "zone-redundant" matches both
        "zone redundant" and "zone-redundant".
    '...' between segments becomes an arbitrary gap of text. A trailing '*' drops
    the closing word boundary so the final token matches as a stem ("encrypt*").
    """
    kw = keyword.rstrip()
    stem = kw.endswith("*")
    if stem:
        kw = kw[:-1].rstrip()

    seg_patterns = []
    for seg in kw.split("..."):
        seg = seg.strip()
        if not seg:
            continue
        body = []
        for part in re.split(r"(\s+|-+)", seg):
            if not part:
                continue
            elif part.isspace():
                body.append(r"\s+")           # space => whitespace only
            elif set(part) == {"-"}:
                body.append(r"[\s\-]+")        # hyphen => space or hyphen
            else:
                body.append(re.escape(part))
        seg_patterns.append(r"\b" + "".join(body))

    pattern = r".*".join(seg_patterns)
    if not stem:
        pattern += r"\b"  # closing boundary unless this is a stem keyword
    return re.compile(pattern, re.IGNORECASE)


# ---------------------------------------------------------------------------
# Loaded rules + classification
# ---------------------------------------------------------------------------

class TierRules:
    def __init__(self, data: dict):
        tiers = data.get("tiers", {})
        # map lowercase yaml keys -> canonical tier names
        self._matchers = {
            tier: [_compile_keyword(k) for k in tiers.get(tier.lower(), [])]
            for tier in TIER_PRIORITY
        }
        # Overrides are per-tier. `name_only[tier]` forces `tier` when the policy
        # NAME matches; `category_only[tier]` forces `tier` for whole categories.
        overrides = data.get("overrides", {})
        name_only = overrides.get("name_only", {})
        category_only = overrides.get("category_only", {})
        self._name_only = {
            tier: [_compile_keyword(k) for k in name_only.get(tier.lower(), [])]
            for tier in TIER_PRIORITY
        }
        self._category_only = {
            tier: set(category_only.get(tier.lower(), []))
            for tier in TIER_PRIORITY
        }

    def classify(self, name: str, description: str, category: str | None = None) -> str:
        # Overrides win before the keyword scan. When more than one override
        # matches, the highest-priority tier wins (the same Enterprise >
        # Professional > Essential order used for the keyword scan), regardless
        # of whether it is a name or a category override.
        for tier in TIER_PRIORITY:
            if category is not None and category in self._category_only[tier]:
                return tier
            if any(m.search(name) for m in self._name_only[tier]):
                return tier

        text = f"{name} {description}"
        for tier in TIER_PRIORITY:
            if any(m.search(text) for m in self._matchers[tier]):
                return tier
        return "Essential"  # safe default


def load_tier_rules(path) -> TierRules:
    """Parse the authored tier-rules YAML into a ready-to-use TierRules."""
    data = _parse_yaml(Path(path).read_text(encoding="utf-8"))
    return TierRules(data)


# Convenience module-level singleton bound to the canonical authored file, so
# callers can simply `from shared.tiers import classify`.
from shared.paths import TIER_RULES_FILE  # noqa: E402

_RULES = load_tier_rules(TIER_RULES_FILE)


def classify(name: str, description: str, category: str | None = None) -> str:
    return _RULES.classify(name, description, category)
