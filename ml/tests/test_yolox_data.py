from __future__ import annotations

import json
from pathlib import Path

from weldvision.training.yolox_data import prepare_yolox_dataset


def _write_split(root: Path, split: str, count: int) -> None:
    split_dir = root / split
    images_dir = split_dir / "images"
    images_dir.mkdir(parents=True)
    images = []
    annotations = []
    for index in range(1, count + 1):
        name = f"{split}-{index}.jpg"
        (images_dir / name).write_bytes(b"fixture")
        images.append(
            {
                "id": index,
                "file_name": name,
                "width": 640,
                "height": 640,
            }
        )
        annotations.append(
            {
                "id": index,
                "image_id": index,
                "category_id": 1,
                "bbox": [1, 2, 3, 4],
                "area": 12,
                "iscrowd": 0,
            }
        )
    payload = {
        "images": images,
        "annotations": annotations,
        "categories": [
            {"id": 1, "name": "slag inclusion"},
            {"id": 2, "name": "spatter"},
            {"id": 3, "name": "undercut"},
        ],
    }
    (split_dir / "_annotations.coco.json").write_text(
        json.dumps(payload),
        encoding="utf-8",
    )


def test_prepare_yolox_dataset_builds_expected_layout(
    tmp_path: Path,
) -> None:
    source = tmp_path / "materialized"
    _write_split(source, "train", 2)
    _write_split(source, "val", 1)
    _write_split(source, "test", 1)
    output = tmp_path / "yolox"

    summary = prepare_yolox_dataset(
        source,
        output,
        link_mode="copy",
        expected_tiles={"train": 2, "val": 1, "test": 1},
    )

    assert summary["splits"]["train"]["images"] == 2
    assert (output / "train2017" / "train-1.jpg").is_file()
    assert (output / "val2017" / "val-1.jpg").is_file()
    assert (output / "test2017" / "test-1.jpg").is_file()
    assert (output / "annotations" / "instances_train.json").is_file()
    assert (output / "annotations" / "instances_val.json").is_file()
    assert (output / "annotations" / "instances_test.json").is_file()
    assert (output / "yolox-dataset-summary.json").is_file()


def test_prepare_yolox_dataset_can_materialize_validation_only(
    tmp_path: Path,
) -> None:
    source = tmp_path / "materialized"
    _write_split(source, "val", 1)
    output = tmp_path / "yolox"

    summary = prepare_yolox_dataset(
        source,
        output,
        link_mode="copy",
        expected_tiles={"train": 2, "val": 1, "test": 1},
        splits=("val",),
    )

    assert summary["requested_splits"] == ["val"]
    assert set(summary["splits"]) == {"val"}
    assert (output / "val2017" / "val-1.jpg").is_file()
    assert (output / "annotations" / "instances_val.json").is_file()
    assert not (output / "annotations" / "instances_test.json").exists()
    assert not (output / "test2017").exists()
