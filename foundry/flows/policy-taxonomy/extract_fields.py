"""extract_fields — pull policy rows for a folder and apply the deterministic filters.

Replaces the JSON file enumeration + schema extraction + deprecation filter
that the Claude Code labs do in-context. The catalog parquet already contains
the four fields lab-05-plan.md cares about (displayName, description, effect,
allowedValues) plus deprecation/preview flags computed at ingest time.
"""

from __future__ import annotations

from typing import Any

from promptflow.core import tool

from _storage import read_parquet


REQUIRED_COLUMNS = {
    "policy_id",
    "folder",
    "display_name",
    "description",
    "effect",
    "allowed_values",
    "is_deprecated",
    "is_preview",
    "file_hash",
}


@tool
def extract_fields(catalog_uri: str, folder: str) -> dict:
    df = read_parquet(catalog_uri)

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(
            f"Catalog parquet missing required columns: {sorted(missing)}. "
            "The ingestion job needs to be re-run."
        )

    scoped = df[df["folder"] == folder].copy()
    if scoped.empty:
        raise RuntimeError(
            f"No policies found for folder '{folder}'. "
            "Either the folder is empty or the catalog is stale."
        )

    # Filters mirror lab-05-plan.md "Constraints":
    #   - exclude [Deprecated]
    #   - exclude preview policies (we surface them in a separate pipeline)
    #   - require a non-empty display name
    before = len(scoped)
    scoped = scoped[~scoped["is_deprecated"]]
    scoped = scoped[~scoped["is_preview"]]
    scoped = scoped[scoped["display_name"].str.strip().astype(bool)]
    dropped = before - len(scoped)

    # Materialize into a list of dicts so downstream nodes don't depend on
    # pandas. The classifier prompt formats from these dicts.
    policies: list[dict[str, Any]] = scoped.assign(
        # Normalize allowed_values to always be a list[str] for the prompt.
        allowed_values=scoped["allowed_values"].apply(
            lambda v: list(v) if v is not None else []
        )
    ).to_dict(orient="records")

    return {
        "policies": policies,
        "stats": {
            "folder": folder,
            "total_in_folder": before,
            "dropped_filters": dropped,
            "kept": len(policies),
        },
    }
