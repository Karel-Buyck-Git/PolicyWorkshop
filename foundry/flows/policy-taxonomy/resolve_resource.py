"""resolve_resource — fuzzy-match a resource_name to a folder in the catalog.

Replaces the "Resource resolution" section of lab-05-plan.md. The deterministic
rules from that prompt are the same: case-insensitive match, allow singular/
plural and spacing variants, fail loudly on no-match or multi-match.
"""

from __future__ import annotations

from typing import Optional

import pandas as pd
from promptflow.core import tool
from rapidfuzz import fuzz, process

from _storage import read_parquet


# Hand-curated overrides from lab-05-plan.md. The fuzzy match handles the long
# tail; this dict short-circuits the well-known cases so the matcher cannot
# drift on common inputs.
KNOWN_MAPPINGS = {
    "app services": "App Service",
    "app service": "App Service",
    "function apps": "App Service",
    "function app": "App Service",
    "logic apps": "Logic Apps",
    "logic app": "Logic Apps",
    "key vault": "Key Vault",
    "storage accounts": "Storage",
    "storage account": "Storage",
    "api management": "API Management",
}


def _normalize(s: str) -> str:
    return " ".join(s.lower().strip().split())


@tool
def resolve_resource(resource_name: str, folders_uri: str) -> dict:
    folders_df = read_parquet(folders_uri)
    if "folder" not in folders_df.columns:
        raise ValueError(
            f"folders parquet at {folders_uri} must contain a 'folder' column; "
            f"got {list(folders_df.columns)}"
        )

    candidates = folders_df["folder"].astype(str).tolist()
    norm = _normalize(resource_name)

    # 1. Known mapping shortcut.
    if norm in KNOWN_MAPPINGS:
        target = KNOWN_MAPPINGS[norm]
        if target in candidates:
            return {
                "folder": target,
                "matched_via": "known_mapping",
                "score": 100,
                "candidates": [target],
            }
        # Fall through to fuzzy if the override no longer exists.

    # 2. Exact (normalized) match.
    exact = [f for f in candidates if _normalize(f) == norm]
    if len(exact) == 1:
        return {
            "folder": exact[0],
            "matched_via": "exact",
            "score": 100,
            "candidates": exact,
        }

    # 3. Fuzzy match. Only accept >= 85; 75-84 returns multi-match for the
    # user to disambiguate. Below 75 we fail.
    matches = process.extract(norm, candidates, scorer=fuzz.WRatio, limit=5)
    above = [(name, score) for name, score, _ in matches if score >= 85]

    if len(above) == 1:
        name, score = above[0]
        return {
            "folder": name,
            "matched_via": "fuzzy",
            "score": int(score),
            "candidates": [name],
        }

    if len(above) > 1:
        raise RuntimeError(
            f"Ambiguous resource '{resource_name}'. Candidates: "
            f"{[f'{n} ({s})' for n, s in above]}. "
            "Add an entry to KNOWN_MAPPINGS or pass the exact folder name."
        )

    raise RuntimeError(
        f"No folder match for resource '{resource_name}'. "
        f"Top candidates: {[(n, int(s)) for n, s, _ in matches]}."
    )
