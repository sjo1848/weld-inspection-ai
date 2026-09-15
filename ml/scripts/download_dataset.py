from __future__ import annotations

import argparse
import json
from pathlib import Path

from weldvision.data.mendeley import download_file, list_root_files, safe_filename


def main() -> int:
    parser = argparse.ArgumentParser(description="Download the public WELD-VISION-001 source dataset")
    parser.add_argument("--out", type=Path, default=Path("data/raw/mendeley"))
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("data/manifests/mendeley-download.json"),
    )
    parser.add_argument("--list-only", action="store_true")
    args = parser.parse_args()

    files = list_root_files()
    listed = [
        {
            "file_id": item.file_id,
            "name": item.name,
            "size_bytes": item.size_bytes,
        }
        for item in files
    ]

    if args.list_only:
        print(json.dumps({"files": listed}, indent=2))
        return 0

    records = []
    for remote in files:
        destination = args.out / safe_filename(remote.name)
        records.append(download_file(remote, destination))

    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(
        json.dumps({"source_files": records}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"Downloaded {len(records)} source file(s); manifest: {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
