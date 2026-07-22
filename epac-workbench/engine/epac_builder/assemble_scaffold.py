"""epac-builder entry point: manifest + catalogue@version -> IaC scaffold.

    python engine/epac_builder/assemble_scaffold.py --manifest customer/manifests/<c>.manifest.jsonc
        [--input <input.json>]   # expand an input.json into a manifest first
        [--only json,terraform,bicep]
        [--check]                # validate + report, write no scaffold files
        [--strict]               # fail if any <REPLACE:>/placeholder-scope survives (pre-deploy gate)
        [--out <dir>]            # override output.root

A pure, deterministic transform: same manifest + same catalogue ⇒ byte-identical
output. Reads the catalogue only; never modifies it. All validation is fail-fast,
before any scaffold file is written.
"""
import argparse
import json
import os
import re
import sys
import uuid
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # engine/ root

from epac_builder import jsonc, validate                         # noqa: E402
from epac_builder.catalogue import Catalogue, ResolveError       # noqa: E402
from epac_builder.bind import BindError                          # noqa: E402
from epac_builder.expand import expand                           # noqa: E402
from epac_builder.ir import build_ir                             # noqa: E402
from epac_builder.mgscopes import HierarchyError, load_mg_index  # noqa: E402
from epac_builder import package as package_mod                  # noqa: E402
from epac_builder import render_json, report                     # noqa: E402
from epac_builder.strict import StrictGateError, residual_placeholders  # noqa: E402

try:
    from epac_builder import render_terraform
except ImportError:
    render_terraform = None
try:
    from epac_builder import render_bicep
except ImportError:
    render_bicep = None

RENDERERS = {"json": render_json}
if render_terraform:
    RENDERERS["terraform"] = render_terraform
if render_bicep:
    RENDERERS["bicep"] = render_bicep

# Sub-folder name per flavour when more than one is selected (json -> "epac").
# A single flavour is rendered FLAT at the package root.
FLAVOUR_DIR = {"json": "epac", "terraform": "terraform", "bicep": "bicep"}

GUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
MANIFESTS_DIR = Path(__file__).resolve().parents[2] / "customer" / "manifests"


class AssemblerError(Exception):
    pass


def _load_schema(name):
    return json.loads((MANIFESTS_DIR / name).read_text(encoding="utf-8"))


def resolve_pac_owner_id(manifest, manifest_path, write_back=True):
    """Use a valid manifest pacOwnerId, else generate one. §3.

    With ``write_back=True`` (the default, CLI behaviour) a generated id is persisted
    back into the manifest file. Read-only callers (e.g. the MCP ``validate_manifest``
    tool) pass ``write_back=False``: the id is applied in memory only so validation can
    proceed, the file is never touched, and the note reports what *would* be assigned.
    """
    val = manifest.get("pacOwnerId")
    if isinstance(val, str) and GUID_RE.match(val):
        return None
    guid = str(uuid.uuid4())
    manifest["pacOwnerId"] = guid
    if not write_back:
        return (f"pacOwnerId missing/invalid — would assign {guid} "
                "(applied in memory for validation; manifest file left untouched)")
    text = Path(manifest_path).read_text(encoding="utf-8")
    if isinstance(val, str) and val in text:
        Path(manifest_path).write_text(text.replace(val, guid, 1), encoding="utf-8")
        return f"generated pacOwnerId {guid} and wrote it back to {manifest_path.name}"
    return f"generated pacOwnerId {guid} (add it to the manifest to keep runs reproducible)"


def load_manifest(manifest_path, write_back=True):
    manifest = jsonc.load(manifest_path)
    validate.validate(manifest, _load_schema("manifest.input.schema.json"),
                      f"{manifest_path.name} (structure)")
    note = resolve_pac_owner_id(manifest, manifest_path, write_back=write_back)  # before strict gate
    validate.validate(manifest, _load_schema("manifest.schema.json"),
                      f"{manifest_path.name} (build gate)")
    return manifest, note


def assemble(manifest_path, only=None, check=False, strict=False, out=None, log=print, write_back=True):
    manifest_path = Path(manifest_path).resolve()
    manifest, note = load_manifest(manifest_path, write_back=write_back)
    if note:
        log(f"[pacOwnerId] {note}")

    cat_dir = (manifest_path.parent / manifest["source"]["initiatives"]).resolve().parent
    catalogue = Catalogue(cat_dir)

    pinned = manifest["source"].get("catalogueVersion")
    if pinned and pinned != catalogue.version:
        raise AssemblerError(
            f"catalogue version mismatch: manifest pins '{pinned}' but catalogue is "
            f"'{catalogue.version}'. Re-pin source.catalogueVersion or point at the right catalogue.")

    # Resolve management-group NAMES (selection.managementGroup) -> scope ids, from the
    # customer's hierarchy file if the manifest points at one.
    mg_index = {}
    mg_src = manifest["source"].get("managementGroups")
    if mg_src:
        mg_path = (manifest_path.parent / mg_src).resolve()
        mg_index = load_mg_index(mg_path)
        log(f"[hierarchy] {len(mg_index)} scope(s) from {mg_path.name}")

    groups = catalogue.resolve(manifest["selection"])
    ir = build_ir(manifest, catalogue, groups, mg_index)
    for w in ir["warnings"]:
        log(f"[warn] {w}")

    # Pre-deploy gate: refuse to emit a package that still carries unfilled placeholders.
    # Runs before both the --check return and any write, so both honour --strict.
    if strict:
        problems = residual_placeholders(manifest, ir)
        if problems:
            raise StrictGateError(problems)

    flavours = list(only) if only else manifest["output"]["flavours"]
    unknown = [f for f in flavours if f not in RENDERERS]
    if unknown:
        raise AssemblerError(f"unknown/unavailable flavour(s): {unknown}. Available: {sorted(RENDERERS)}")

    out_root = Path(out).resolve() if out else (manifest_path.parent / manifest["output"]["root"]).resolve()

    log(f"[catalogue] {catalogue.version} · {len(groups)} group(s) · flavours: {', '.join(flavours)}")
    if check:
        log(f"[check] validation passed; {len(ir['initiatives'])} initiative(s) resolved. No files written.")
        return ir

    # Each flavour becomes a self-contained deployable package: rendered content +
    # pipeline + docs + provenance. One flavour -> flat at the package root; several
    # -> a sub-folder per flavour (json -> "epac").
    flat = len(flavours) == 1
    for flavour in flavours:
        pkg = out_root if flat else out_root / FLAVOUR_DIR[flavour]
        RENDERERS[flavour].render(ir, pkg)
        report.write_reports(ir, pkg, [flavour])
        package_mod.finalize(ir, pkg, flavour, manifest_path, log=log)
        log(f"[package:{flavour}] -> {pkg}")
    return ir


def main(argv=None):
    p = argparse.ArgumentParser(description="epac-builder: manifest + catalogue -> IaC scaffold")
    p.add_argument("--manifest", help="customer manifest (.jsonc/.json)")
    p.add_argument("--input", help="expand this input.json into a manifest, then stop")
    p.add_argument("--only", help="comma list of flavours to render (json,terraform,bicep)")
    p.add_argument("--check", action="store_true", help="validate + report, write no scaffold files")
    p.add_argument("--strict", action="store_true",
                   help="pre-deploy gate: fail if any <REPLACE:> or placeholder scope survives")
    p.add_argument("--out", help="override output.root (the package root)")
    args = p.parse_args(argv)

    try:
        if args.input:
            return _do_expand(args)
        if not args.manifest:
            p.error("either --manifest or --input is required")
        only = [s.strip() for s in args.only.split(",")] if args.only else None
        assemble(args.manifest, only=only, check=args.check, strict=args.strict, out=args.out)
    except (AssemblerError, ResolveError, BindError, HierarchyError,
            StrictGateError, validate.ValidationError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    return 0


def _do_expand(args):
    input_path = Path(args.input).resolve()
    cat_dir = Path(__file__).resolve().parents[2] / "catalogue"
    catalogue = Catalogue(cat_dir)
    manifest = expand(json.loads(input_path.read_text(encoding="utf-8")), catalogue)
    out_path = Path(args.out) if args.out else input_path.parent / f"{manifest['customer']}.manifest.jsonc"
    out_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[expand] wrote manifest -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
