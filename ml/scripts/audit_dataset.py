from __future__ import annotations

import argparse
import json
from pathlib import Path

from weldvision.data.coco_audit import audit_coco


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit COCO annotations for WELD-VISION-001")
    parser.add_argument("root", type=Path, help="Extracted dataset root")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("data/manifests/dataset-audit.json"),
    )
    args = parser.parse_args()

    annotation_files = sorted(
        path
        for path in args.root.rglob("*.json")
        if "annotation" in path.name.lower() or "coco" in path.name.lower()
    )
    if not annotation_files:
        raise SystemExit(f"No COCO-like annotation JSON files found under {args.root}")

    reports = [audit_coco(path) for path in annotation_files]
    output = {
        "dataset_root": str(args.root),
        "annotation_files": reports,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
