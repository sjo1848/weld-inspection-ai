from __future__ import annotations

import argparse
import json
from pathlib import Path

from weldvision.training.yolox_data import prepare_yolox_dataset

PROJECT_EXPECTED_TILES = {"train": 358, "val": 45, "test": 45}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prepare the frozen WELD-VISION-001 materialized split for upstream YOLOX"
    )
    parser.add_argument(
        "materialized_root",
        type=Path,
        help="Materialized split root containing train/val/test subdirectories",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("data/yolox/weld-v0.1"),
    )
    parser.add_argument(
        "--link-mode",
        choices=("copy", "hardlink", "symlink"),
        default="hardlink",
        help="How images are placed into YOLOX train2017/val2017/test2017 directories",
    )
    args = parser.parse_args()

    summary = prepare_yolox_dataset(
        args.materialized_root,
        args.out,
        link_mode=args.link_mode,
        expected_tiles=PROJECT_EXPECTED_TILES,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
