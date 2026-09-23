from __future__ import annotations

import json
import os
import shutil
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

AUGMENTATION_PREFIXES = (
    "Original_",
    "Flip_H_",
    "Flip_V_",
    "Rotate_90_CW_",
    "Rotate_90_CCW_",
    "Rotate_180_",
    "Grayscale_",
    "Color_Jitter_",
    "Blur_",
)
TARGET_CATEGORIES = {"slag inclusion", "spatter", "undercut"}


@dataclass(frozen=True)
class CocoSource:
    name: str
    annotation_path: Path
    images_dir: Path
    base_only: bool


def source_photo_id(file_name: str) -> str:
    """Recover the original camera-photo identity from a Roboflow-derived filename."""
    name = Path(file_name).name
    if name.startswith("orig_"):
        name = name.removeprefix("orig_")
    else:
        for prefix in AUGMENTATION_PREFIXES:
            if name.startswith(prefix):
                name = name.removeprefix(prefix)
                break
    return name.split("_jpg.rf.", 1)[0]


def materialize_project_split(
    dataset_root: Path,
    manifest_path: Path,
    output_root: Path,
    *,
    link_mode: str = "copy",
) -> dict[str, Any]:
    """Materialize the frozen source-photo split into compact COCO train/val/test sets."""
    dataset_root = dataset_root.resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    split_sources = manifest["project_split"]["sources"]
    expected_stats = manifest["project_split"].get("stats", {})

    source_to_split: dict[str, str] = {}
    for split_name in ("train", "val", "test"):
        for source_id in split_sources[split_name]:
            previous = source_to_split.setdefault(source_id, split_name)
            if previous != split_name:
                raise ValueError(
                    f"Source photo {source_id!r} appears in both {previous!r} and {split_name!r}"
                )

    sources = _discover_sources(dataset_root)
    records: list[dict[str, Any]] = []
    category_defs: dict[str, dict[str, Any]] = {}

    for source in sources:
        payload = json.loads(source.annotation_path.read_text(encoding="utf-8"))
        images = payload.get("images") or []
        annotations = payload.get("annotations") or []
        categories = payload.get("categories") or []
        anns_by_image: dict[int, list[dict[str, Any]]] = {}
        for annotation in annotations:
            if not isinstance(annotation, dict):
                continue
            anns_by_image.setdefault(int(annotation["image_id"]), []).append(annotation)

        category_name_by_id = {
            int(category["id"]): str(category["name"])
            for category in categories
            if isinstance(category, dict)
            and "id" in category
            and "name" in category
            and str(category["name"]) in TARGET_CATEGORIES
        }
        for category in categories:
            if not isinstance(category, dict):
                continue
            name = str(category.get("name", ""))
            if name in TARGET_CATEGORIES:
                category_defs.setdefault(name, dict(category))

        for image in images:
            if not isinstance(image, dict):
                continue
            file_name = str(image.get("file_name", ""))
            if source.base_only and not file_name.startswith("orig_"):
                continue

            source_id = source_photo_id(file_name)
            split_name = source_to_split.get(source_id)
            if split_name is None:
                raise ValueError(
                    f"Source photo {source_id!r} from {source.name} is absent "
                    "from the frozen manifest"
                )

            image_id = int(image["id"])
            kept_annotations = []
            for annotation in anns_by_image.get(image_id, []):
                category_id = int(annotation["category_id"])
                category_name = category_name_by_id.get(category_id)
                if category_name is None:
                    continue
                kept_annotations.append((annotation, category_name))

            records.append(
                {
                    "origin": source.name,
                    "source_photo": source_id,
                    "split": split_name,
                    "image": image,
                    "annotations": kept_annotations,
                    "source_path": source.images_dir / file_name,
                }
            )

    _assert_base_pool(manifest, records)

    output_root.mkdir(parents=True, exist_ok=True)
    summary: dict[str, Any] = {
        "manifest": str(manifest_path),
        "dataset_root": str(dataset_root),
        "output_root": str(output_root),
        "link_mode": link_mode,
        "splits": {},
    }
    category_order = ("slag inclusion", "spatter", "undercut")
    output_categories = []
    output_category_ids: dict[str, int] = {}
    for new_id, name in enumerate(category_order, start=1):
        category = dict(category_defs.get(name, {"name": name}))
        category["id"] = new_id
        category["name"] = name
        output_categories.append(category)
        output_category_ids[name] = new_id

    for split_name in ("train", "val", "test"):
        split_records = [record for record in records if record["split"] == split_name]
        split_dir = output_root / split_name
        images_dir = split_dir / "images"
        images_dir.mkdir(parents=True, exist_ok=True)

        output_images: list[dict[str, Any]] = []
        output_annotations: list[dict[str, Any]] = []
        class_counts: Counter[str] = Counter()
        source_ids: set[str] = set()

        for new_image_id, record in enumerate(
            sorted(split_records, key=lambda item: str(item["image"]["file_name"])),
            start=1,
        ):
            image = dict(record["image"])
            file_name = str(image["file_name"])
            image["id"] = new_image_id
            output_images.append(image)
            source_ids.add(str(record["source_photo"]))

            source_path = Path(record["source_path"])
            if not source_path.is_file():
                raise FileNotFoundError(f"Dataset image is missing: {source_path}")
            _materialize_file(source_path, images_dir / file_name, link_mode)

            for annotation, category_name in record["annotations"]:
                output_annotation = dict(annotation)
                output_annotation["id"] = len(output_annotations) + 1
                output_annotation["image_id"] = new_image_id
                output_annotation["category_id"] = output_category_ids[category_name]
                output_annotations.append(output_annotation)
                class_counts[category_name] += 1

        coco = {
            "images": output_images,
            "annotations": output_annotations,
            "categories": output_categories,
        }
        (split_dir / "_annotations.coco.json").write_text(
            json.dumps(coco, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        split_summary = {
            "source_photos": len(source_ids),
            "tiles": len(output_images),
            "annotations": len(output_annotations),
            "class_counts": dict(sorted(class_counts.items())),
        }
        _assert_expected_split(split_name, split_summary, expected_stats.get(split_name))
        summary["splits"][split_name] = split_summary

    split_source_sets = {
        split_name: {
            str(record["source_photo"])
            for record in records
            if record["split"] == split_name
        }
        for split_name in ("train", "val", "test")
    }
    if (
        split_source_sets["train"] & split_source_sets["val"]
        or split_source_sets["train"] & split_source_sets["test"]
        or split_source_sets["val"] & split_source_sets["test"]
    ):
        raise AssertionError("Frozen project split contains source-photo overlap")

    summary["zero_source_overlap"] = True
    (output_root / "materialization-summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return summary


def _discover_sources(dataset_root: Path) -> tuple[CocoSource, ...]:
    train_root = dataset_root / "train" / "train_fold_1"
    val_root = dataset_root / "val" / "val_fold_1"
    test_root = dataset_root / "test"
    sources = (
        CocoSource(
            "train_fold_1",
            train_root / "_annotations.coco.json",
            train_root / "images",
            True,
        ),
        CocoSource(
            "val_fold_1",
            val_root / "_annotations.coco.json",
            val_root / "images",
            True,
        ),
        CocoSource("published_test", test_root / "_annotations.coco.json", test_root, False),
    )
    for source in sources:
        if not source.annotation_path.is_file():
            raise FileNotFoundError(f"COCO annotation file is missing: {source.annotation_path}")
        if not source.images_dir.is_dir():
            raise FileNotFoundError(f"Dataset image directory is missing: {source.images_dir}")
    return sources


def _assert_base_pool(manifest: dict[str, Any], records: list[dict[str, Any]]) -> None:
    expected = manifest.get("base_pool", {})
    expected_tiles = expected.get("tiles")
    expected_annotations = expected.get("annotations")
    actual_annotations = sum(len(record["annotations"]) for record in records)
    if expected_tiles is not None and len(records) != int(expected_tiles):
        raise AssertionError(f"Base tile count mismatch: {len(records)} != {expected_tiles}")
    if expected_annotations is not None and actual_annotations != int(expected_annotations):
        raise AssertionError(
            f"Base annotation count mismatch: {actual_annotations} != {expected_annotations}"
        )


def _assert_expected_split(
    split_name: str,
    actual: dict[str, Any],
    expected: dict[str, Any] | None,
) -> None:
    if not expected:
        return
    for key in ("source_photos", "tiles", "annotations"):
        if key in expected and actual[key] != int(expected[key]):
            raise AssertionError(
                f"{split_name} {key} mismatch: {actual[key]} != {expected[key]}"
            )
    expected_classes = expected.get("class_counts")
    if expected_classes and actual["class_counts"] != expected_classes:
        raise AssertionError(
            f"{split_name} class-count mismatch: "
            f"{actual['class_counts']} != {expected_classes}"
        )


def _materialize_file(source: Path, destination: Path, link_mode: str) -> None:
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
