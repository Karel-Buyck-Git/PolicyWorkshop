#!/usr/bin/env python3
"""Catalogue drift detector.

Compares two catalogues at the policy-asset level (keyed on policy GUID) and reports
exactly which policies were added, removed, re-tiered, re-categorised, or had their
baked effect changed — then attributes the cause from each catalogue's catalogue.json
provenance (source git ref, tool hashes, content fingerprint) when available.

Works on either a catalogue root (contains catalogue.json / initiatives/) or an
initiatives directory directly — it discovers groups by reading each policyset's
metadata {domain, tier, category}, so it's independent of folder layout and prefix.

Usage:
    python engine/catalogue_diff.py OLD NEW [--out report.json] [--limit 20]

Example (a previous catalogue vs the current one):
    python engine/catalogue_diff.py \
        "C:/GIT/.../previous/initiatives" \
        "C:/GIT/.../epac-workbench/catalogue" --limit 15
"""
import argparse
import json
import sys
from pathlib import Path

# Output contains box-drawing/arrow glyphs (→, ∅); force UTF-8 so it doesn't
# crash on the default Windows cp1252 console.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass


def find_provenance(root: Path):
    for cand in (root / "catalogue.json", root.parent / "catalogue.json"):
        if cand.exists():
            try:
                return json.loads(cand.read_text(encoding="utf-8")), cand
            except Exception:
                pass
    return None, None


def scan(root: Path):
    """Return {guid: {'group': (domain,tier,category), 'effect': str|None, 'name': displayName}}."""
    idx = {}
    files = list(root.rglob("*.policyset.json"))
    for f in files:
        try:
            props = json.loads(f.read_text(encoding="utf-8")).get("properties", {})
        except Exception:
            continue
        md = props.get("metadata", {}) or {}
        group = (str(md.get("domain", "")).lower(),
                 str(md.get("tier", "")).lower(),
                 str(md.get("category", "")).lower())
        for m in props.get("policyDefinitions", []) or []:
            guid = m.get("policyDefinitionReferenceId")
            if not guid:
                continue
            eff = ((m.get("parameters") or {}).get("effect") or {}).get("value")
            # first occurrence wins; record group + effect
            idx.setdefault(guid, {"group": group, "effect": eff,
                                  "name": (m.get("metadata") or {}).get("policyName", "")})
    return idx, len(files)


def classify_move(ga, gb):
    da, ta, ca = ga
    db, tb, cb = gb
    if da == db and ca == cb and ta != tb:
        return "retiered", f"{ta or '∅'} → {tb or '∅'}"
    if da != db or ca != cb:
        a = f"{da}/{ca}" if da or ca else "∅"
        b = f"{db}/{cb}" if db or cb else "∅"
        return "recategorised", f"{a} → {b}"
    return None, None


def _attribute(pa, pb):
    """Classify *why* the catalogue changed, from the two provenance stamps (#27, 27d).

    Maps the input-hash deltas onto the drivers a customer engineer reasons about:
    ``builtInsRef`` moved -> upstream Microsoft policy change (the recurring fetch);
    ``hierarchyHash``/``tierRulesHash`` moved -> taxonomy/classification (our curation);
    tool or definition-gen hashes moved (with sources unchanged) -> engine change.
    """
    if not pa or not pb:
        return {"attributable": False,
                "verdict": "one side predates version-stamping — cause not attributable",
                "drivers": []}
    ai, bi = (pa.get("inputs", {}) or {}), (pb.get("inputs", {}) or {})
    upstream = ai.get("builtInsRef") != bi.get("builtInsRef")
    taxonomy = (ai.get("hierarchyHash") != bi.get("hierarchyHash")
                or ai.get("tierRulesHash") != bi.get("tierRulesHash"))
    engine = (pa.get("tools") != pb.get("tools")
              or ai.get("definitionGensHash") != bi.get("definitionGensHash")
              or pa.get("producedByEngine") != pb.get("producedByEngine"))
    drivers = []
    if upstream:
        drivers.append("upstream policies (Azure/azure-policy)")
    if taxonomy:
        drivers.append("taxonomy / classification (curation)")
    if engine:
        drivers.append("engine")
    if not drivers:
        drivers.append("none — identical provenance (any asset drift is non-determinism)")
    return {
        "attributable": True,
        "upstreamChanged": upstream, "taxonomyChanged": taxonomy, "engineChanged": engine,
        "drivers": drivers,
        "oldEngine": pa.get("producedByEngine"), "newEngine": pb.get("producedByEngine"),
        "oldBuiltInsRef": ai.get("builtInsRef"), "newBuiltInsRef": bi.get("builtInsRef"),
        "oldContentHash": pa.get("contentHash"), "newContentHash": pb.get("contentHash"),
    }


def diff_catalogues(old, new):
    """Compare two catalogues at policy-GUID level + attribute the cause. Returns a report dict.

    The single reusable entry point — the console tool (``main``) and the changelog
    generator (``catalogue_changelog.py``) both build on this so the diff logic lives once.
    """
    A, B = Path(old).resolve(), Path(new).resolve()
    ia, na = scan(A); ib, nb = scan(B)
    sa, sb = set(ia), set(ib)

    added = sorted(sb - sa)
    removed = sorted(sa - sb)
    common = sa & sb

    retiered, recategorised, effect_changed, unchanged = [], [], [], 0
    for g in common:
        ga, gb = ia[g]["group"], ib[g]["group"]
        if ga != gb:
            kind, detail = classify_move(ga, gb)
            (retiered if kind == "retiered" else recategorised).append((g, detail, ib[g]["name"]))
        elif ia[g]["effect"] != ib[g]["effect"]:
            effect_changed.append((g, f"{ia[g]['effect']} → {ib[g]['effect']}", ib[g]["name"]))
        else:
            unchanged += 1

    pa, _ = find_provenance(A); pb, _ = find_provenance(B)
    return {
        "old": str(A), "new": str(B),
        "counts": {"added": len(added), "removed": len(removed),
                   "retiered": len(retiered), "recategorised": len(recategorised),
                   "effectChanged": len(effect_changed), "unchanged": unchanged,
                   "policiesOld": len(sa), "policiesNew": len(sb),
                   "policysetsOld": na, "policysetsNew": nb},
        "added": [{"guid": g, "group": ib[g]["group"], "name": ib[g]["name"]} for g in added],
        "removed": [{"guid": g, "group": ia[g]["group"], "name": ia[g]["name"]} for g in removed],
        "retiered": [{"guid": g, "move": d, "name": n} for g, d, n in retiered],
        "recategorised": [{"guid": g, "move": d, "name": n} for g, d, n in recategorised],
        "effectChanged": [{"guid": g, "move": d, "name": n} for g, d, n in effect_changed],
        "attribution": _attribute(pa, pb),
        "provenance": {"old": pa, "new": pb},
        "_idx": {"old": ia, "new": ib},   # in-memory indices (for the console renderer)
    }


def main():
    ap = argparse.ArgumentParser(description="Catalogue drift detector (policy-asset level).")
    ap.add_argument("old"); ap.add_argument("new")
    ap.add_argument("--out", help="Write full JSON report here")
    ap.add_argument("--limit", type=int, default=20, help="Max examples printed per category")
    args = ap.parse_args()

    rep = diff_catalogues(args.old, args.new)
    A, B = rep["old"], rep["new"]
    c = rep["counts"]
    ia, ib = rep["_idx"]["old"], rep["_idx"]["new"]
    added = [r["guid"] for r in rep["added"]]
    removed = [r["guid"] for r in rep["removed"]]
    retiered = [(r["guid"], r["move"], r["name"]) for r in rep["retiered"]]
    recategorised = [(r["guid"], r["move"], r["name"]) for r in rep["recategorised"]]
    effect_changed = [(r["guid"], r["move"], r["name"]) for r in rep["effectChanged"]]
    groups_a = {v["group"] for v in ia.values()}
    groups_b = {v["group"] for v in ib.values()}
    pa, pb = rep["provenance"]["old"], rep["provenance"]["new"]
    na, nb = c["policysetsOld"], c["policysetsNew"]
    sa, sb = set(ia), set(ib)
    unchanged = c["unchanged"]

    def fmt_group(g):
        return "/".join(x for x in g if x) or "∅"

    print("="*72)
    print(f"CATALOGUE DRIFT   OLD={A}\n                  NEW={B}")
    print("="*72)
    print(f"policies:  old={len(sa)}  new={len(sb)}   (policysets: old={na} new={nb})")
    print(f"groups:    old={len(groups_a)} new={len(groups_b)} | only-old={len(groups_a-groups_b)} only-new={len(groups_b-groups_a)}")
    print(f"\nADDED (new GUIDs):        {len(added)}")
    print(f"REMOVED (gone GUIDs):     {len(removed)}")
    print(f"RETIERED (same cat):      {len(retiered)}")
    print(f"RECATEGORISED:            {len(recategorised)}")
    print(f"EFFECT CHANGED:           {len(effect_changed)}")
    print(f"UNCHANGED:                {unchanged}")

    def show(title, rows, render):
        if not rows:
            return
        print(f"\n--- {title} (showing {min(len(rows), args.limit)}/{len(rows)}) ---")
        for r in rows[:args.limit]:
            print("  " + render(r))

    show("ADDED", added, lambda g: f"{g}  [{fmt_group(ib[g]['group'])}]  {ib[g]['name'][:60]}")
    show("REMOVED", removed, lambda g: f"{g}  [{fmt_group(ia[g]['group'])}]  {ia[g]['name'][:60]}")
    show("RETIERED", retiered, lambda r: f"{r[0]}  {r[1]}  {r[2][:50]}")
    show("RECATEGORISED", recategorised, lambda r: f"{r[0]}  {r[1]}  {r[2][:50]}")
    show("EFFECT CHANGED", effect_changed, lambda r: f"{r[0]}  {r[1]}  {r[2][:50]}")

    print("\n" + "="*72)
    print("ATTRIBUTION (from catalogue.json provenance)")
    print("="*72)
    if not pa or not pb:
        miss = [n for n, p in (("OLD", pa), ("NEW", pb)) if not p]
        print(f"  No catalogue.json for: {', '.join(miss)}.")
        print("  → cause cannot be attributed automatically for that side")
        print("    (built before version-stamping). The asset diff above still stands;")
        print("    a same-source build would attribute this to pipeline/manual-curation drift.")
    else:
        def line(label, a, b):
            same = "same" if a == b else "DIFFERENT"
            print(f"  {label:14} {same:9} old={a}  new={b}")
        line("source ref", pa["inputs"].get("builtInsRef"), pb["inputs"].get("builtInsRef"))
        line("hierarchy",  pa["inputs"].get("hierarchyHash"), pb["inputs"].get("hierarchyHash"))
        line("tier rules", pa["inputs"].get("tierRulesHash"), pb["inputs"].get("tierRulesHash"))
        for t in ("extract", "enrich", "createInitiatives"):
            line(f"tool:{t}", pa.get("tools", {}).get(t), pb.get("tools", {}).get(t))
        line("contentHash", pa.get("contentHash"), pb.get("contentHash"))
        srcsame = pa["inputs"].get("builtInsRef") == pb["inputs"].get("builtInsRef")
        toolsame = pa.get("tools") == pb.get("tools")
        verdict = ("source & pipeline identical — any asset drift is non-determinism (investigate)"
                   if srcsame and toolsame else
                   "pipeline changed (tools differ) — drift expected" if srcsame else
                   "source changed (builtInsRef differs) — drift expected")
        print(f"\n  VERDICT: {verdict}")

    if args.out:
        report = {k: v for k, v in rep.items() if k != "_idx"}
        Path(args.out).write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"\nfull report → {args.out}")


if __name__ == "__main__":
    main()
