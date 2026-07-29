"""Single source of truth for Catalogue Builder pipeline paths.

The catalogue-builder (producer) writes the shared CATALOGUE. Customer packages
live separately under customer/. Import these constants instead of hardcoding
folder names, so a future rename is a one-line change here.

``EPAC_WORKBENCH_ROOT`` relocates the whole workbench. Normally the root is derived
from this file's own location, which is right for every real invocation. Setting the
variable points the producer at a scratch workbench instead, which is what lets the
tests exercise the parts of the pipeline that read fixed paths — ``apply_overlays``
(phase 4), ``quality_control`` (phase 5) and the release driver — without touching the
real ``catalogue/``. It is a **test/rehearsal hook, not a deployment knob**: a release
run with it set would stamp and publish the wrong tree.
"""
import json
import os
from pathlib import Path

WORKBENCH_ROOT_ENV = "EPAC_WORKBENCH_ROOT"

# shared/paths.py  ->  shared  ->  engine  ->  project root
_default_root = Path(__file__).resolve().parents[2]
_override = os.environ.get(WORKBENCH_ROOT_ENV)
PROJECT_ROOT = Path(_override).resolve() if _override else _default_root

# The external official Azure Policy repo (parameter/schema source of truth).
# Unlike the constants below, this is NOT derived from PROJECT_ROOT -- it is a
# separate clone whose location varies per machine, so it is never baked in.
OFFICIAL_POLICY_REPO_ENV = "AZURE_POLICY_REPO"

# Shared catalogue produced by the catalogue-builder (producer)
CATALOGUE_DIR   = PROJECT_ROOT / "catalogue"
DEFINITIONS_DIR = CATALOGUE_DIR / "definitions"   # policies.md taxonomy
INITIATIVES_DIR = CATALOGUE_DIR / "initiatives"   # EPAC group artifacts
INDEX_FILE      = CATALOGUE_DIR / "index.json"     # generated: groups + domain map
CATALOGUE_FILE  = CATALOGUE_DIR / "catalogue.json" # generated: version stamp
CHANGELOG_FILE  = CATALOGUE_DIR / "CHANGELOG.md"   # generated: per-release record (the released-label ledger)

# Authored inputs
CONFIG_DIR     = PROJECT_ROOT / "config"
HIERARCHY_FILE = CONFIG_DIR / "azure-domain-hierachy.md"   # the ONE authored hierarchy
TIER_RULES_FILE = CONFIG_DIR / "tier-rules.yaml"           # the ONE authored tier ruleset
CATEGORY_ABBREV_FILE = CONFIG_DIR / "azure-category-abbreviation.md"  # authored category short codes
DEFINITION_GENS_FILE = CONFIG_DIR / "definition-gens.md"  # authored allowlist of overlay generators
DOCS_DIR       = PROJECT_ROOT / "docs"

# Official policy source (parameter/schema source of truth). The pin file records
# the exact upstream commit; engine/tools/fetch_policy_source.py materialises it into
# the gitignored cache below. The producer resolves its --source default from either.
POLICY_SOURCE_PIN   = CONFIG_DIR / "policy-source.json"   # tracked: which upstream commit
POLICY_SOURCE_CACHE = PROJECT_ROOT / ".policy-source"     # gitignored: the fetched checkout

# Quality-control outputs (Phase 4): regenerated docs + machine-readable report
NAMING_SAMPLES_FILE = CATALOGUE_DIR / "naming-samples.md"
EPAC_NAMING_DOC     = DOCS_DIR / "epac-naming-convention.md"
QC_REPORT_FILE      = CATALOGUE_DIR / "quality-control.json"

# Customer packages (consumer side): the epac-builder reads the shared catalogue
# and writes a customer's own scaffold here. Manifests + their schemas live under
# customer/manifests/; the deployable package defaults to customer/package/.
CUSTOMER_DIR          = PROJECT_ROOT / "customer"
MANIFESTS_DIR         = CUSTOMER_DIR / "manifests"
INPUT_SCHEMA_FILE          = MANIFESTS_DIR / "input.schema.json"
MANIFEST_INPUT_SCHEMA_FILE = MANIFESTS_DIR / "manifest.input.schema.json"
MANIFEST_SCHEMA_FILE       = MANIFESTS_DIR / "manifest.schema.json"


def _pinned_source_dir() -> Path | None:
    """The policyDefinitions folder inside the fetched cache, per the pin file.

    Returns None when the pin file is absent (nothing to resolve). Existence of the
    folder itself is the caller's concern.
    """
    if not POLICY_SOURCE_PIN.exists():
        return None
    pin = json.loads(POLICY_SOURCE_PIN.read_text(encoding="utf-8"))
    return POLICY_SOURCE_CACHE / pin["subdir"]


def official_policy_source() -> str | None:
    """Resolve the official policy source for the producer's --source default.

    Precedence: AZURE_POLICY_REPO env var (explicit override) -> the pinned cache
    materialised by engine/tools/fetch_policy_source.py (the canonical default every
    colleague shares) -> None. Returning None lets callers fail/degrade with a clear
    message. An explicit --source flag overrides all of this at the argparse layer.
    """
    env = os.environ.get(OFFICIAL_POLICY_REPO_ENV)
    if env:
        return env
    cached = _pinned_source_dir()
    if cached and cached.exists():
        return str(cached)
    return None
