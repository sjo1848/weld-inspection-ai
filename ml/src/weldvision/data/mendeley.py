from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests

MENDELEY_DATASET_ID = "f7j76vz53p"
MENDELEY_DATASET_VERSION = 1
PUBLIC_FILES_URL = "https://data.mendeley.com/public-api/datasets/{dataset_id}/files"


@dataclass(frozen=True)
class RemoteFile:
    file_id: str
    name: str
    size_bytes: int | None
    download_url: str


def list_root_files(
    dataset_id: str = MENDELEY_DATASET_ID,
    version: int = MENDELEY_DATASET_VERSION,
    timeout_s: float = 30.0,
) -> list[RemoteFile]:
    """List files from the public Mendeley record without hardcoding rotating URLs."""
    response = requests.get(
        PUBLIC_FILES_URL.format(dataset_id=dataset_id),
        params={"folder_id": "root", "version": version},
        timeout=timeout_s,
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, list):
        raise ValueError("Unexpected Mendeley files payload: expected a list")

    files: list[RemoteFile] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        details = item.get("content_details") or {}
        download_url = details.get("download_url")
        if not download_url:
            continue
        _validate_https_url(str(download_url))
        files.append(
            RemoteFile(
                file_id=str(item.get("id") or ""),
                name=str(item.get("filename") or item.get("name") or item.get("id") or "file"),
                size_bytes=_optional_int(item.get("size")),
                download_url=str(download_url),
            )
        )
    return files


def safe_filename(name: str) -> str:
    """Return a basename suitable for writing under the configured dataset directory."""
    normalized = name.replace("\\", "/")
    basename = Path(normalized).name
    if not basename or basename in {".", ".."}:
        raise ValueError(f"Unsafe remote filename: {name!r}")
    if basename != normalized:
        raise ValueError(f"Remote filename must not contain a path: {name!r}")
    return basename


def download_file(
    remote: RemoteFile,
    destination: Path,
    timeout_s: float = 120.0,
    chunk_size: int = 1024 * 1024,
) -> dict[str, Any]:
    """Stream one dataset file and return durable integrity metadata."""
    _validate_https_url(remote.download_url)
    destination.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    written = 0

    with requests.get(remote.download_url, stream=True, timeout=timeout_s) as response:
        response.raise_for_status()
        with destination.open("wb") as output:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if not chunk:
                    continue
                output.write(chunk)
                digest.update(chunk)
                written += len(chunk)

    if remote.size_bytes is not None and written != remote.size_bytes:
        raise IOError(
            f"Downloaded byte count mismatch for {remote.name}: expected "
            f"{remote.size_bytes}, got {written}"
        )

    return {
        "file_id": remote.file_id,
        "name": remote.name,
        "size_bytes": written,
        "sha256": digest.hexdigest(),
    }


def _validate_https_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError(f"Dataset download URL must be HTTPS: {url!r}")


def _optional_int(value: object) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
