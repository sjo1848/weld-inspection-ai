from __future__ import annotations

import argparse
import json
from pathlib import Path

from weldvision.data.project_split import materialize_project_split


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Materialize the frozen WELD-VISION-001 source-photo-aware COCO split"
    )
    parser.add_argument(
        "dataset_root",
        type=Path,
        help="Extracted 'Annotated Image Dataset for Shielded Metal Arc Wel' directory",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("data/manifests/b1-source-split-manifest.json"),
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("data/materialized/weld-v0.1"),
    )
    parser.add_argument(
        "--link-mode",
        choices=("copy", "hardlink", "symlink"),
        default="copy",
        help="How selected images are materialized; copy is the portable default",
    )
    args = parser.parse_args()

    summary = materialize_project_split(
        args.dataset_root,
        args.manifest,
        args.out,
        link_mode=args.link_mode,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
