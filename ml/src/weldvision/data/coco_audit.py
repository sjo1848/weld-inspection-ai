from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def audit_coco(annotation_file: Path) -> dict[str, Any]:
    payload = json.loads(annotation_file.read_text(encoding="utf-8"))
    images = payload.get("images") or []
    annotations = payload.get("annotations") or []
    categories = payload.get("categories") or []

    if (
        not isinstance(images, list)
        or not isinstance(annotations, list)
        or not isinstance(categories, list)
    ):
        raise ValueError(f"Invalid COCO structure in {annotation_file}")

    category_names = {
        int(category["id"]): str(category["name"])
        for category in categories
        if isinstance(category, dict) and "id" in category and "name" in category
    }
    image_ids = {
        int(image["id"])
        for image in images
        if isinstance(image, dict) and "id" in image
    }

    annotation_counts: Counter[int] = Counter()
    annotated_images: defaultdict[int, set[int]] = defaultdict(set)
    invalid_image_refs = 0
    invalid_category_refs = 0
    degenerate_boxes = 0

    for annotation in annotations:
        if not isinstance(annotation, dict):
            continue
        image_id = int(annotation.get("image_id", -1))
        category_id = int(annotation.get("category_id", -1))
        annotation_counts[category_id] += 1
        annotated_images[category_id].add(image_id)
        if image_id not in image_ids:
            invalid_image_refs += 1
        if category_id not in category_names:
            invalid_category_refs += 1
        box = annotation.get("bbox")
        if isinstance(box, list) and len(box) >= 4:
            try:
                width = float(box[2])
                height = float(box[3])
            except (TypeError, ValueError):
                degenerate_boxes += 1
            else:
                if width <= 0 or height <= 0:
                    degenerate_boxes += 1

    image_name_counts = Counter(
        str(image.get("file_name", ""))
        for image in images
        if isinstance(image, dict)
    )
    duplicate_file_names = sorted(
        name for name, count in image_name_counts.items() if name and count > 1
    )

    image_ids_with_any_annotation = {
        int(annotation.get("image_id", -1))
        for annotation in annotations
        if isinstance(annotation, dict)
    }
    background_image_ids = image_ids - image_ids_with_any_annotation

    widths = [
        int(image["width"])
        for image in images
        if isinstance(image, dict) and image.get("width") is not None
    ]
    heights = [
        int(image["height"])
        for image in images
        if isinstance(image, dict) and image.get("height") is not None
    ]

    per_class = []
    for category_id, name in sorted(category_names.items(), key=lambda item: item[1]):
        per_class.append(
            {
                "category_id": category_id,
                "name": name,
                "annotations": annotation_counts[category_id],
                "images_with_class": len(annotated_images[category_id]),
            }
        )

    return {
        "annotation_file": str(annotation_file),
        "images": len(images),
        "annotations": len(annotations),
        "categories": per_class,
        "background_images": len(background_image_ids),
        "duplicate_file_names": duplicate_file_names,
        "invalid_image_refs": invalid_image_refs,
        "invalid_category_refs": invalid_category_refs,
        "degenerate_boxes": degenerate_boxes,
        "image_widths": _range_summary(widths),
        "image_heights": _range_summary(heights),
        "file_name_samples": [
            str(image.get("file_name", ""))
            for image in images[:10]
            if isinstance(image, dict)
        ],
    }


def _range_summary(values: list[int]) -> dict[str, int] | None:
    if not values:
        return None
    return {"min": min(values), "max": max(values)}
