import json
from pathlib import Path

from weldvision.data.coco_audit import audit_coco


def test_audit_coco_counts_classes_and_background_images(tmp_path: Path) -> None:
    annotation_file = tmp_path / "_annotations.coco.json"
    annotation_file.write_text(
        json.dumps(
            {
                "images": [
                    {"id": 1, "file_name": "a.jpg", "width": 640, "height": 640},
                    {"id": 2, "file_name": "b.jpg", "width": 640, "height": 640},
                ],
                "categories": [
                    {"id": 10, "name": "spatter"},
                    {"id": 20, "name": "undercut"},
                ],
                "annotations": [
                    {"id": 1, "image_id": 1, "category_id": 10, "bbox": [1, 2, 10, 20]},
                    {"id": 2, "image_id": 1, "category_id": 20, "bbox": [4, 5, 6, 7]},
                ],
            }
        ),
        encoding="utf-8",
    )

    report = audit_coco(annotation_file)

    assert report["images"] == 2
    assert report["annotations"] == 2
    assert report["background_images"] == 1
    assert report["invalid_image_refs"] == 0
    assert report["invalid_category_refs"] == 0
    assert {row["name"] for row in report["categories"]} == {"spatter", "undercut"}
