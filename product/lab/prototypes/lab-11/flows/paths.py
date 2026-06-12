"""Single source of truth for lab-11 pipeline paths.

The taxonomy flow (phases 1-3) writes the shared CATALOGUE. Customer packages
live separately under customer/. Import these constants instead of hardcoding
folder names, so a future rename is a one-line change here.
"""
from pathlib import Path

LAB_ROOT = Path(__file__).resolve().parent.parent

# Shared catalogue produced by the taxonomy flow
CATALOGUE_DIR   = LAB_ROOT / "catalogue"
DEFINITIONS_DIR = CATALOGUE_DIR / "definitions"   # policies.md taxonomy
INITIATIVES_DIR = CATALOGUE_DIR / "initiatives"   # EPAC group artifacts
INDEX_FILE      = CATALOGUE_DIR / "index.json"     # generated: groups + domain map
CATALOGUE_FILE  = CATALOGUE_DIR / "catalogue.json" # generated: version stamp

# Authored inputs
CONFIG_DIR     = LAB_ROOT / "config"
HIERARCHY_FILE = CONFIG_DIR / "azure-domain-hierachy.md"   # the ONE authored hierarchy
TIER_RULES_FILE = CONFIG_DIR / "tier-rules.yaml"           # the ONE authored tier ruleset
DOCS_DIR       = LAB_ROOT / "docs"
