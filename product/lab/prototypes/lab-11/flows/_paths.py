"""Single source of truth for lab-11 pipeline paths.

The taxonomy flow (phases 1-3) writes the shared CATALOGUE. Customer packages
live separately under customer/. Import these constants instead of hardcoding
folder names, so a future rename is a one-line change here.
"""
from pathlib import Path

LAB_ROOT = Path(__file__).resolve().parent.parent

# Shared catalogue produced by the taxonomy flow
CATALOGUE_DIR   = LAB_ROOT / "catalogue"
DEFINITIONS_DIR = CATALOGUE_DIR / "definitions"   # was: output/        (policies.md taxonomy)
INITIATIVES_DIR = CATALOGUE_DIR / "initiatives"   # was: initiatives/    (EPAC group artifacts)

# Inputs
DOCS_DIR       = LAB_ROOT / "docs"
HIERARCHY_FILE = DOCS_DIR / "azure-domain-hierachy.md"
