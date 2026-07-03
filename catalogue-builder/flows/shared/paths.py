"""Single source of truth for Catalogue Builder pipeline paths.

The catalogue-builder (producer) writes the shared CATALOGUE. Customer packages
live separately under customer/. Import these constants instead of hardcoding
folder names, so a future rename is a one-line change here.
"""
import os
from pathlib import Path

# shared/paths.py  ->  shared  ->  flows  ->  project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# The external official Azure Policy repo (parameter/schema source of truth).
# Unlike the constants below, this is NOT derived from PROJECT_ROOT -- it is a
# separate clone whose location varies per machine, so it is never baked in.
OFFICIAL_POLICY_REPO_ENV = "AZURE_POLICY_REPO"


def official_policy_source() -> str | None:
    """Resolve the official policy repo from the AZURE_POLICY_REPO env var.

    Returns None when unset; callers pass --source to override or fail/degrade
    when neither is provided.
    """
    return os.environ.get(OFFICIAL_POLICY_REPO_ENV)

# Shared catalogue produced by the catalogue-builder (producer)
CATALOGUE_DIR   = PROJECT_ROOT / "catalogue"
DEFINITIONS_DIR = CATALOGUE_DIR / "definitions"   # policies.md taxonomy
INITIATIVES_DIR = CATALOGUE_DIR / "initiatives"   # EPAC group artifacts
INDEX_FILE      = CATALOGUE_DIR / "index.json"     # generated: groups + domain map
CATALOGUE_FILE  = CATALOGUE_DIR / "catalogue.json" # generated: version stamp

# Authored inputs
CONFIG_DIR     = PROJECT_ROOT / "config"
HIERARCHY_FILE = CONFIG_DIR / "azure-domain-hierachy.md"   # the ONE authored hierarchy
TIER_RULES_FILE = CONFIG_DIR / "tier-rules.yaml"           # the ONE authored tier ruleset
CATEGORY_ABBREV_FILE = CONFIG_DIR / "azure-category-abbreviation.md"  # authored category short codes
DEFINITION_GENS_FILE = CONFIG_DIR / "definition-gens.md"  # authored allowlist of overlay generators
DOCS_DIR       = PROJECT_ROOT / "docs"

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
