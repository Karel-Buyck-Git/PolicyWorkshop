"""Put ``engine/`` on ``sys.path`` so tests import the engine the way it runs.

The engine is not an installed package (``pyproject.toml`` has no ``[build-system]``
and ``dependencies = []`` on purpose), so its own entry point does the same thing —
see ``engine/epac_builder/assemble_scaffold.py``. Importing this module is the only
setup a test file needs; import it before any ``epac_builder`` / ``shared`` import.
"""
import os
import sys

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TESTS_DIR)                 # epac-workbench/
ENGINE = os.path.join(ROOT, "engine")
FIXTURES = os.path.join(TESTS_DIR, "fixtures")
MINI_CATALOGUE = os.path.join(FIXTURES, "mini-catalogue")

if ENGINE not in sys.path:
    sys.path.insert(0, ENGINE)
