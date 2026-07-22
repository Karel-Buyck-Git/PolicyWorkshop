"""Helpers for reading/writing blobs via the user-assigned managed identity.

Used by every node that touches storage. Keeping this in one module means we
authenticate once per flow run and hit a single code path for both Parquet
catalog reads and markdown output writes.
"""

from __future__ import annotations

import io
import os
from functools import lru_cache
from typing import Optional
from urllib.parse import urlparse

import pandas as pd
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.storage.blob import BlobClient, BlobServiceClient


@lru_cache(maxsize=1)
def _credential():
    """Prefer a UAMI when running in Foundry; fall back to DefaultAzureCredential locally.

    Setting AZURE_CLIENT_ID makes ManagedIdentityCredential use the user-assigned
    identity bound to the compute. Without it, DefaultAzureCredential walks the
    chain (env, CLI, etc.) which is fine for `pf flow test` on a developer box.
    """
    client_id = os.environ.get("AZURE_CLIENT_ID")
    if client_id:
        return ManagedIdentityCredential(client_id=client_id)
    return DefaultAzureCredential(exclude_interactive_browser_credential=False)


def _parse_uri(uri: str) -> tuple[str, str, str]:
    """Accept either azureml:// datastore URIs or https:// blob URIs.

    Returns (account_url, container, blob_path).
    """
    if uri.startswith("azureml://"):
        # azureml://datastores/<datastore>/paths/<blob_path>
        # The flow runtime resolves this; for local testing we expect the
        # caller to substitute STORAGE_ACCOUNT_URL via env.
        account_url = os.environ.get("STORAGE_ACCOUNT_URL")
        if not account_url:
            raise RuntimeError(
                "azureml:// URIs require STORAGE_ACCOUNT_URL to be set when "
                "running outside the Foundry runtime."
            )
        # Strip the prefix and assume default container "workspaceblobstore"
        # is mounted as "catalog"/"outputs"/"flows" depending on path prefix.
        parts = uri.removeprefix("azureml://").split("/paths/", 1)
        if len(parts) != 2:
            raise ValueError(f"Malformed azureml URI: {uri}")
        blob_path = parts[1].lstrip("/")
        container = blob_path.split("/", 1)[0]
        rest = blob_path.split("/", 1)[1] if "/" in blob_path else ""
        return account_url, container, rest

    parsed = urlparse(uri)
    account_url = f"{parsed.scheme}://{parsed.netloc}"
    container, _, blob_path = parsed.path.lstrip("/").partition("/")
    return account_url, container, blob_path


def read_parquet(uri: str) -> pd.DataFrame:
    account_url, container, blob_path = _parse_uri(uri)
    client = BlobClient(
        account_url=account_url,
        container_name=container,
        blob_name=blob_path,
        credential=_credential(),
    )
    stream = io.BytesIO()
    client.download_blob().readinto(stream)
    stream.seek(0)
    return pd.read_parquet(stream)


def write_text(uri: str, content: str, content_type: str = "text/markdown") -> str:
    account_url, container, blob_path = _parse_uri(uri)
    client = BlobClient(
        account_url=account_url,
        container_name=container,
        blob_name=blob_path,
        credential=_credential(),
    )
    client.upload_blob(
        content.encode("utf-8"),
        overwrite=True,
        content_settings=None,  # set if you want explicit content-type via ContentSettings
    )
    return f"{account_url}/{container}/{blob_path}"


def container_url(account_url: str, container: str, blob_path: str) -> str:
    return f"{account_url}/{container}/{blob_path}"
