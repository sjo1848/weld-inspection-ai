from __future__ import annotations

import json
from pathlib import Path

from weldvision.data.project_split import materialize_project_split, source_photo_id


def _write_coco(
    path: Path,
    images_dir: Path,
    image_names: list[str],
    *,
    annotation_category: int = 2,
) -> None:
    images_dir.mkdir(parents=True, exist_ok=True)
    images = []
    annotations = []
    for index, name in enumerate(image_names, start=1):
        (images_dir / name).write_bytes(b"image")
        images.append({"id": index, "file_name": name, "width": 640, "height": 640})
        annotations.append(
            {
                "id": index,
                "image_id": index,
                "category_id": annotation_category,
                "bbox": [10, 10, 20, 20],
                "area": 400,
                "iscrowd": 0,
            }
        )
    payload = {
        "images": images,
        "annotations": annotations,
        "categories": [
            {"id": 0, "name": "weld-defect-det"},
            {"id": 1, "name": "slag inclusion"},
            {"id": 2, "name": "spatter"},
            {"id": 3, "name": "undercut"},
        ],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_source_photo_id_strips_augmentation_and_roboflow_suffix() -> None:
    assert (
        source_photo_id("Blur_20230612_101104_jpg.rf.0123456789abcdef0123456789abcdef.jpg")
        == "20230612_101104"
    )
    assert (
        source_photo_id("orig_IMG_20240516_142554_jpg.rf.0123456789abcdef0123456789abcdef.jpg")
        == "IMG_20240516_142554"
    )


def test_materialize_project_split_keeps_only_orig_train_val(tmp_path: Path) -> None:
    dataset = tmp_path / "dataset"
    train_root = dataset / "train" / "train_fold_1"
    val_root = dataset / "val" / "val_fold_1"
    test_root = dataset / "test"

    hash_value = "0123456789abcdef0123456789abcdef"
    _write_coco(
        train_root / "_annotations.coco.json",
        train_root / "images",
        [
            f"orig_SRC_A_jpg.rf.{hash_value}.jpg",
            f"Blur_SRC_A_jpg.rf.{hash_value}.jpg",
        ],
    )
    _write_coco(
        val_root / "_annotations.coco.json",
        val_root / "images",
        [f"orig_SRC_B_jpg.rf.{hash_value}.jpg"],
    )
    _write_coco(
        test_root / "_annotations.coco.json",
        test_root,
        [f"SRC_C_jpg.rf.{hash_value}.jpg"],
    )

    manifest = {
        "base_pool": {"tiles": 3, "annotations": 3},
        "project_split": {
            "sources": {"train": ["SRC_A"], "val": ["SRC_B"], "test": ["SRC_C"]},
            "stats": {
                "train": {
                    "source_photos": 1,
                    "tiles": 1,
                    "annotations": 1,
                    "class_counts": {"spatter": 1},
                },
                "val": {
                    "source_photos": 1,
                    "tiles": 1,
                    "annotations": 1,
                    "class_counts": {"spatter": 1},
                },
                "test": {
                    "source_photos": 1,
                    "tiles": 1,
                    "annotations": 1,
                    "class_counts": {"spatter": 1},
                },
            },
        },
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    output = tmp_path / "output"
    summary = materialize_project_split(dataset, manifest_path, output)

    assert summary["zero_source_overlap"] is True
    assert summary["splits"]["train"]["tiles"] == 1
    assert not (output / "train" / "images" / f"Blur_SRC_A_jpg.rf.{hash_value}.jpg").exists()
    assert (output / "train" / "images" / f"orig_SRC_A_jpg.rf.{hash_value}.jpg").is_file()
