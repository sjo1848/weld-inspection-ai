from __future__ import annotations

import hashlib
import json
import os
import shutil
from pathlib import Path
from typing import Any

TARGET_CLASSES = ("slag inclusion", "spatter", "undercut")
YOLOX_SPLIT_DIRS = {
    "train": "train2017",
    "val": "val2017",
    "test": "test2017",
}
YOLOX_ANNOTATION_NAMES = {
    "train": "instances_train.json",
    "val": "instances_val.json",
    "test": "instances_test.json",
}


def prepare_yolox_dataset(
    materialized_root: Path,
    output_root: Path,
    *,
    link_mode: str = "hardlink",
    expected_tiles: dict[str, int] | None = None,
    splits: tuple[str, ...] | None = None,
) -> dict[str, Any]:
    """Build the directory layout expected by the upstream YOLOX COCO loader."""

    materialized_root = materialized_root.resolve()
    output_root = output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    annotations_dir = output_root / "annotations"
    annotations_dir.mkdir(parents=True, exist_ok=True)

    requested_splits = splits or tuple(YOLOX_SPLIT_DIRS)
    unknown = set(requested_splits) - set(YOLOX_SPLIT_DIRS)
    if unknown:
        raise ValueError(f"Unknown YOLOX split(s): {sorted(unknown)!r}")

    summary: dict[str, Any] = {
        "materialized_root": str(materialized_root),
        "output_root": str(output_root),
        "link_mode": link_mode,
        "classes": list(TARGET_CLASSES),
        "requested_splits": list(requested_splits),
        "splits": {},
    }

    for split_name in requested_splits:
        destination_dir_name = YOLOX_SPLIT_DIRS[split_name]
        split_dir = materialized_root / split_name
        images_dir = split_dir / "images"
        annotation_path = split_dir / "_annotations.coco.json"
        if not images_dir.is_dir():
            raise FileNotFoundError(f"Missing image directory: {images_dir}")
        if not annotation_path.is_file():
            raise FileNotFoundError(f"Missing COCO annotation file: {annotation_path}")

        payload = json.loads(annotation_path.read_text(encoding="utf-8"))
        images = payload.get("images") or []
        annotations = payload.get("annotations") or []
        categories = payload.get("categories") or []
        if not isinstance(images, list) or not isinstance(annotations, list):
            raise ValueError(f"Invalid COCO structure in {annotation_path}")

        category_names = tuple(
            str(category.get("name", ""))
            for category in categories
            if isinstance(category, dict)
        )
        if set(category_names) != set(TARGET_CLASSES):
            raise ValueError(
                f"Unexpected category set in {annotation_path}: "
                f"{sorted(category_names)!r}"
            )

        if expected_tiles is not None:
            expected = int(expected_tiles[split_name])
            if len(images) != expected:
                raise AssertionError(
                    f"{split_name} tile count mismatch: {len(images)} != {expected}"
                )

        destination_images = output_root / destination_dir_name
        destination_images.mkdir(parents=True, exist_ok=True)
        referenced_names: set[str] = set()
        for image in images:
            if not isinstance(image, dict) or not image.get("file_name"):
                raise ValueError(f"Invalid image record in {annotation_path}")
            file_name = str(image["file_name"])
            if file_name in referenced_names:
                raise ValueError(
                    f"Duplicate file_name in {annotation_path}: {file_name}"
                )
            referenced_names.add(file_name)
            source = images_dir / file_name
            if not source.is_file():
                raise FileNotFoundError(
                    f"Referenced dataset image is missing: {source}"
                )
            _materialize_file(
                source,
                destination_images / file_name,
                link_mode,
            )

        annotation_destination = (
            annotations_dir / YOLOX_ANNOTATION_NAMES[split_name]
        )
        shutil.copy2(annotation_path, annotation_destination)
        summary["splits"][split_name] = {
            "images": len(images),
            "annotations": len(annotations),
            "annotation_sha256": _sha256(annotation_destination),
            "image_dir": destination_dir_name,
            "annotation_file": annotation_destination.name,
        }

    summary_path = output_root / "yolox-dataset-summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return summary


def _materialize_file(
    source: Path,
    destination: Path,
    link_mode: str,
) -> None:
    if destination.exists() or destination.is_symlink():
        destination.unlink()
    if link_mode == "copy":
        shutil.copy2(source, destination)
    elif link_mode == "hardlink":
        os.link(source, destination)
    elif link_mode == "symlink":
        destination.symlink_to(source.resolve())
    else:
        raise ValueError(f"Unsupported link mode: {link_mode!r}")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()
