#!/usr/bin/env python3
"""Controlled A/B — prove the phase-3 refactor is ADDITIVE-ONLY.

It builds a "pre-refactor" variant of create_initiatives.py by stripping ONLY the
deliberately-added bits (policyset metadata fields catalogueVersion/hasRemediation/
roleDefinitionIds, the .roles.json sidecar, and the index.json/catalogue.json finalize),
then runs BOTH the current ("post") and the stripped ("pre") generator against the SAME
catalogue/definitions, and diffs the catalogue/initiatives output.

Expected result (PASS):
  - .md / .assignment.json / .exemptions.json are byte-identical pre vs post.
  - .policyset.json are identical AFTER removing the added metadata keys.
  - the only post-exclusive files are .roles.json (and index.json/catalogue.json at the root).

Run:
  python flows/tools/ab_verify.py
  python flows/tools/ab_verify.py --source "C:\\GIT\\Official Azure Policy\\azure-policy\\built-in-policies\\policyDefinitions"

With no --source both sides use an empty parameter index (identical), which cleanly isolates
the grouping/assembly code paths. With the real --source, post additionally bakes roles.
"""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Output contains box-drawing/arrow glyphs (→, ∅); force UTF-8 so it doesn't
# crash on the default Windows cp1252 console.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass

HERE = Path(__file__).resolve().parent              # flows/tools
FLOWS = HERE.parent                                  # flows/
POST = FLOWS / "catalogue_builder" / "create_initiatives.py"
SHARED = FLOWS / "shared"
DEFS = FLOWS.parent / "catalogue" / "definitions"


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip())


def build_pre(post_text: str) -> str:
    """Remove only the post-refactor additions to reconstruct a pre-refactor generator.

    Everything else stays byte-identical. The additions stripped (kept in sync with
    create_initiatives.py) are:
      1) the extra policyset metadata keys (catalogueVersion / hasRemediation / roleDefinitionIds);
      2) the `.roles.json` sidecar write block (`if has_roles:` …);
      3) the `index_records` initializer + its `.append({…})` block;
      4) the `write_catalogue_manifests(...)` call;
      5) the 'Catalogue stamped' print.
    Block bodies are skipped by indentation, so the stripper tolerates small edits.
    """
    lines = post_text.split("\n")
    out, i, n = [], 0, len(lines)
    while i < n:
        s = lines[i].strip()
        # 1) keep the clean metadata= line, drop the extra metadata.* lines until the blank
        if s == 'metadata = {"category": category, "domain": domain, "tier": tier}':
            out.append(lines[i]); i += 1
            while i < n and lines[i].strip() != "":
                i += 1
            continue
        # 2) drop the `.roles.json` sidecar write block (header + its indented body)
        if s == "if has_roles:":
            base = _indent(lines[i]); i += 1
            while i < n and (lines[i].strip() == "" or _indent(lines[i]) > base):
                i += 1
            continue
        # 3a) drop the index_records initializer
        if s == "index_records: list[dict] = []":
            i += 1
            continue
        # 3b) drop the index_records.append({...}) block (until the closing `})`)
        if s.startswith("index_records.append("):
            while i < n and lines[i].strip() != "})":
                i += 1
            i += 1  # skip the closing })
            continue
        # 4) drop the write_catalogue_manifests(...) call
        if s.startswith("write_catalogue_manifests("):
            while i < n and lines[i].strip() != ")":
                i += 1
            i += 1
            continue
        # 5) drop the 'Catalogue stamped' print (+ its continuation line)
        if s.startswith('print(f"[Phase 3] Catalogue stamped:'):
            i += 1
            if i < n and lines[i].strip().startswith('f"(index.json'):
                i += 1
            continue
        out.append(lines[i]); i += 1
    return "\n".join(out)


def run(script: Path, out_root: Path, source: str):
    cmd = [sys.executable, str(script), "--output", str(DEFS),
           "--initiatives", str(out_root / "initiatives"), "--source", source]
    return subprocess.run(cmd, capture_output=True, text=True)


def core(ps_path: Path) -> str:
    """policyset JSON with the added metadata keys removed, for core comparison."""
    d = json.loads(ps_path.read_text(encoding="utf-8"))
    md = d.get("properties", {}).get("metadata", {})
    for k in ("catalogueVersion", "hasRemediation", "roleDefinitionIds"):
        md.pop(k, None)
    return json.dumps(d, sort_keys=True)


def rel_files(root: Path):
    return {str(p.relative_to(root)).replace("\\", "/") for p in root.rglob("*") if p.is_file()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default=str(Path(tempfile.gettempdir()) / "no_repo_ab"))
    args = ap.parse_args()

    if not DEFS.exists():
        sys.exit(f"definitions not found: {DEFS}")

    tmp = Path(tempfile.mkdtemp(prefix="ab_"))
    pre_dir, post_dir = tmp / "pre", tmp / "post"
    # Recreate the minimal package layout so the scripts' `from shared.* import …`
    # bootstrap resolves: tmp/shared/<libs> + tmp/catalogue_builder/<scripts>.
    # Each generator inserts parents[1] (== tmp) on sys.path, where shared/ lives.
    (tmp / "shared").mkdir()
    for m in ("paths.py", "hierarchy.py", "mdtable.py", "__init__.py"):
        shutil.copy(SHARED / m, tmp / "shared" / m)
    cb = tmp / "catalogue_builder"
    cb.mkdir()
    pre_script = cb / "create_initiatives.py"           # same bootstrap → shared resolves
    pre_script.write_text(build_pre(POST.read_text(encoding="utf-8")), encoding="utf-8")
    post_script = cb / "post_create.py"
    shutil.copy(POST, post_script)

    print(f"definitions: {DEFS}")
    print(f"source:      {args.source}  (missing → empty param index, identical both sides)\n")
    r_pre = run(pre_script, pre_dir, args.source)
    r_post = run(post_script, post_dir, args.source)
    for name, r in (("pre", r_pre), ("post", r_post)):
        if r.returncode != 0:
            print(f"{name} FAILED:\n{r.stderr[-1500:]}"); sys.exit(1)

    pi, qi = pre_dir / "initiatives", post_dir / "initiatives"
    fp, fq = rel_files(pi), rel_files(qi)

    only_post = sorted(fq - fp)
    only_pre = sorted(fp - fq)
    common = sorted(fp & fq)

    core_mismatch, other_mismatch, meta_added = [], [], 0
    for rel in common:
        a, b = pi / rel, qi / rel
        if rel.endswith(".policyset.json"):
            if core(a) != core(b):
                core_mismatch.append(rel)
            ma = set(json.loads(a.read_text())["properties"].get("metadata", {}))
            mb = set(json.loads(b.read_text())["properties"].get("metadata", {}))
            if mb - ma:
                meta_added += 1
        else:
            if a.read_bytes() != b.read_bytes():
                other_mismatch.append(rel)

    print(f"groups: pre={sum(1 for f in fp if f.endswith('.policyset.json'))} "
          f"post={sum(1 for f in fq if f.endswith('.policyset.json'))}")
    print(f"common files: {len(common)} | only-in-post: {len(only_post)} | only-in-pre: {len(only_pre)}")
    print(f"policyset CORE mismatches (should be 0): {len(core_mismatch)}")
    print(f"md/assignment/exemption byte mismatches (should be 0): {len(other_mismatch)}")
    print(f"policysets with added metadata keys (additive): {meta_added}")
    if only_post:
        kinds = sorted({f.rsplit('.', 2)[-2] + '.' + f.rsplit('.', 1)[-1] if f.count('.') > 1 else f for f in only_post})
        print(f"only-in-post kinds: {sorted({Path(f).name.split('.',1)[1] for f in only_post})}")
    print(f"root manifests (post): "
          f"index.json={ (post_dir/'index.json').exists() } catalogue.json={ (post_dir/'catalogue.json').exists() }")

    ok = (not core_mismatch) and (not other_mismatch) and (not only_pre)
    print("\nRESULT:", "PASS — refactor is additive-only (categorization/enrichment unchanged)"
          if ok else "FAIL — investigate the mismatches above")
    print(f"(work dir: {tmp})")
    sys.exit(0 if ok else 2)


if __name__ == "__main__":
    main()
