from __future__ import annotations

import json
import os
import pathlib
import shutil
import subprocess
import sys
from collections import defaultdict

import numpy as np
import torch
from google.colab import drive
from pycocotools.cocoeval import COCOeval

PROJECT_REPO = "https://github.com/sjo1848/weld-inspection-ai.git"
PROJECT_BRANCH = "build/mvp-v0.1"
YOLOX_REPO = "https://github.com/Megvii-BaseDetection/YOLOX.git"
YOLOX_COMMIT = "6ddff4824372906469a7fae2dc3206c7aa4bbaee"
B3_BEST_SHA256 = "7e5cd8915262a0f912de33a04262e7fab7b984badf70cf2f92f1a38fbac7fb8b"

PROJECT = pathlib.Path("/content/weld-inspection-ai")
YOLOX = pathlib.Path("/content/YOLOX-weld-vendor")
DRIVE_B3 = pathlib.Path("/content/drive/MyDrive/WELD-VISION-001/B3")
DRIVE_B4 = pathlib.Path("/content/drive/MyDrive/WELD-VISION-001/B4")
ARCHIVE = DRIVE_B3 / "input/weld-v0.1-materialized.tar.gz"
BEST_CKPT = DRIVE_B3 / "YOLOX_outputs/weld_nano_v0_1_train/best_ckpt.pth"
THRESHOLDS = (0.01, 0.03, 0.05, 0.10, 0.15, 0.20, 0.30)
NMS_THRESHOLD = 0.65
PROMOTED_CLASSES = ("spatter", "slag inclusion")
DIAGNOSTIC_ONLY_CLASSES = ("undercut",)


def run(cmd, *, cwd=None, env=None) -> None:
    print("+", " ".join(str(part) for part in cmd))
    subprocess.run([str(part) for part in cmd], cwd=cwd, env=env, check=True)


def clone_project() -> str:
    if PROJECT.exists() and (PROJECT / ".git").exists():
        run(["git", "-C", PROJECT, "fetch", "origin", PROJECT_BRANCH])
        run(["git", "-C", PROJECT, "switch", PROJECT_BRANCH])
        run(["git", "-C", PROJECT, "pull", "--ff-only"])
    else:
        if PROJECT.exists():
            shutil.rmtree(PROJECT)
        run(
            [
                "git",
                "clone",
                "--branch",
                PROJECT_BRANCH,
                "--single-branch",
                PROJECT_REPO,
                PROJECT,
            ]
        )
    return subprocess.check_output(
        ["git", "-C", str(PROJECT), "rev-parse", "HEAD"],
        text=True,
    ).strip()


def prepare_dataset() -> pathlib.Path:
    assert ARCHIVE.exists(), f"Missing persistent B3 dataset archive: {ARCHIVE}"
    materialized_root = PROJECT / "data/materialized"
    yolox_root = PROJECT / "data/yolox/weld-v0.1"
    materialized_root.mkdir(parents=True, exist_ok=True)
    run(["tar", "-xzf", ARCHIVE, "-C", materialized_root])

    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT / "ml/src")
    run(
        [
            sys.executable,
            "ml/scripts/prepare_yolox_dataset.py",
            "data/materialized/weld-v0.1",
            "--out",
            "data/yolox/weld-v0.1",
            "--link-mode",
            "copy",
        ],
        cwd=PROJECT,
        env=env,
    )
    counts = {
        split: sum(
            1
            for path in (yolox_root / f"{split}2017").iterdir()
            if path.is_file()
        )
        for split in ("train", "val", "test")
    }
    assert counts == {"train": 358, "val": 45, "test": 45}, counts
    return yolox_root


def prepare_yolox() -> None:
    if YOLOX.exists():
        shutil.rmtree(YOLOX)
    run(["git", "clone", "-q", YOLOX_REPO, YOLOX])
    run(["git", "checkout", YOLOX_COMMIT], cwd=YOLOX)
    deps = [
        "loguru",
        "tqdm",
        "thop",
        "ninja",
        "tabulate",
        "psutil",
        "tensorboard",
        "pycocotools",
        "opencv-python",
    ]
    run([sys.executable, "-m", "pip", "install", "-q", *deps])
    sha = subprocess.check_output(
        ["git", "-C", str(YOLOX), "rev-parse", "HEAD"],
        text=True,
    ).strip()
    assert sha == YOLOX_COMMIT


def xyxy_iou(a: list[float], b_xywh: list[float]) -> float:
    ax1, ay1, ax2, ay2 = a
    bx, by, bw, bh = b_xywh
    bx1, by1, bx2, by2 = bx, by, bx + bw, by + bh
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    iw, ih = max(0.0, ix2 - ix1), max(0.0, iy2 - iy1)
    intersection = iw * ih
    if intersection <= 0:
        return 0.0
    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bw) * max(0.0, bh)
    union = area_a + area_b - intersection
    return intersection / union if union > 0 else 0.0


def threshold_predictions(output_data: dict, threshold: float) -> list[dict]:
    predictions = []
    for image_id, payload in output_data.items():
        for bbox, score, category_id in zip(
            payload["bboxes"],
            payload["scores"],
            payload["categories"],
            strict=True,
        ):
            if float(score) < threshold:
                continue
            x1, y1, x2, y2 = (float(value) for value in bbox)
            predictions.append(
                {
                    "image_id": int(image_id),
                    "category_id": int(category_id),
                    "bbox": [x1, y1, x2 - x1, y2 - y1],
                    "score": float(score),
                }
            )
    return predictions


def operating_point_counts(
    coco_gt,
    output_data: dict,
    threshold: float,
    cat_id: int,
) -> tuple[int, int, int]:
    gt_by_image: dict[int, list[dict]] = defaultdict(list)
    for ann in coco_gt.loadAnns(coco_gt.getAnnIds(catIds=[cat_id])):
        gt_by_image[int(ann["image_id"])].append(ann)

    pred_by_image: dict[int, list[tuple[float, list[float]]]] = defaultdict(list)
    for image_id, payload in output_data.items():
        for bbox, score, category_id in zip(
            payload["bboxes"],
            payload["scores"],
            payload["categories"],
            strict=True,
        ):
            if int(category_id) == cat_id and float(score) >= threshold:
                pred_by_image[int(image_id)].append(
                    (float(score), [float(value) for value in bbox])
                )

    tp = fp = 0
    matched_gt = 0
    image_ids = set(gt_by_image) | set(pred_by_image)
    for image_id in image_ids:
        ground_truth = gt_by_image.get(image_id, [])
        used = set()
        for _, pred_box in sorted(pred_by_image.get(image_id, []), reverse=True):
            best_idx = None
            best_iou = 0.0
            for idx, ann in enumerate(ground_truth):
                if idx in used:
                    continue
                iou = xyxy_iou(pred_box, ann["bbox"])
                if iou > best_iou:
                    best_iou = iou
                    best_idx = idx
            if best_idx is not None and best_iou >= 0.50:
                tp += 1
                used.add(best_idx)
            else:
                fp += 1
        matched_gt += len(used)

    total_gt = sum(len(items) for items in gt_by_image.values())
    fn = total_gt - matched_gt
    return tp, fp, fn


def evaluate_threshold(coco_gt, output_data: dict, threshold: float) -> dict:
    predictions = threshold_predictions(output_data, threshold)
    cat_ids = sorted(coco_gt.cats)
    names = {cat_id: coco_gt.cats[cat_id]["name"] for cat_id in cat_ids}

    ap50_by_id = {cat_id: 0.0 for cat_id in cat_ids}
    overall_ap50 = 0.0
    if predictions:
        coco_dt = coco_gt.loadRes(predictions)
        coco_eval = COCOeval(coco_gt, coco_dt, "bbox")
        coco_eval.evaluate()
        coco_eval.accumulate()
        precision = coco_eval.eval["precision"][0, :, :, 0, -1]
        valid_all = precision[precision > -1]
        overall_ap50 = float(np.mean(valid_all)) if valid_all.size else 0.0
        for idx, cat_id in enumerate(coco_eval.params.catIds):
            values = precision[:, idx]
            values = values[values > -1]
            ap50_by_id[cat_id] = float(np.mean(values)) if values.size else 0.0

    per_class = {}
    for cat_id in cat_ids:
        tp, fp, fn = operating_point_counts(
            coco_gt,
            output_data,
            threshold,
            cat_id,
        )
        precision_value = tp / (tp + fp) if tp + fp else 0.0
        recall_value = tp / (tp + fn) if tp + fn else 0.0
        total = precision_value + recall_value
        f1 = 2 * precision_value * recall_value / total if total else 0.0
        per_class[names[cat_id]] = {
            "precision": precision_value,
            "recall": recall_value,
            "f1": f1,
            "ap50": ap50_by_id[cat_id],
            "ground_truth": tp + fn,
            "tp": tp,
            "fp": fp,
            "fn": fn,
        }

    return {
        "threshold": threshold,
        "overall_ap50": overall_ap50,
        "per_class": per_class,
    }


def main() -> None:
    drive.mount("/content/drive")
    DRIVE_B4.mkdir(parents=True, exist_ok=True)

    project_sha = clone_project()
    yolox_data_root = prepare_dataset()
    prepare_yolox()

    sys.path.insert(0, str(PROJECT / "ml/src"))
    sys.path.insert(0, str(YOLOX))
    from yolox.exp import get_exp

    from weldvision.evaluation.promotion import (
        ClassMetrics,
        ThresholdResult,
        choose_operating_threshold,
        sha256_file,
    )

    assert BEST_CKPT.exists(), f"Missing B3 best checkpoint: {BEST_CKPT}"
    checkpoint_sha = sha256_file(BEST_CKPT)
    assert checkpoint_sha == B3_BEST_SHA256, (
        f"Unexpected checkpoint SHA-256: {checkpoint_sha}; "
        f"expected {B3_BEST_SHA256}"
    )

    os.environ["WELD_YOLOX_DATA_DIR"] = str(yolox_data_root)
    os.environ["WELD_YOLOX_OUTPUT_DIR"] = str(DRIVE_B4 / "YOLOX_outputs")
    os.environ["WELD_YOLOX_EPOCHS"] = "80"
    os.environ["WELD_YOLOX_WORKERS"] = "2"

    exp = get_exp(str(PROJECT / "ml/yolox/weld_nano_exp.py"), None)
    assert exp.val_ann == "instances_val.json"
    exp.test_conf = min(THRESHOLDS)
    exp.nmsthre = NMS_THRESHOLD

    model = exp.get_model()
    checkpoint = torch.load(
        BEST_CKPT,
        map_location="cuda:0",
        weights_only=False,
    )
    model.load_state_dict(checkpoint["model"])
    model.cuda(0).eval()

    evaluator = exp.get_evaluator(
        batch_size=8,
        is_distributed=False,
        testdev=False,
        legacy=False,
    )
    evaluator.per_class_AP = True
    evaluator.per_class_AR = True

    print("B4.1 validation-only inference. Frozen test is not accessed.")
    _, output_data = evaluator.evaluate(
        model,
        distributed=False,
        half=True,
        trt_file=None,
        decoder=None,
        test_size=exp.test_size,
        return_outputs=True,
    )
    coco_gt = evaluator.dataloader.dataset.coco
    assert len(coco_gt.getImgIds()) == 45

    calibration_rows = [
        evaluate_threshold(coco_gt, output_data, value)
        for value in THRESHOLDS
    ]
    threshold_results = []
    for row in calibration_rows:
        class_metrics = {
            name: ClassMetrics(
                precision=metrics["precision"],
                recall=metrics["recall"],
                ap50=metrics["ap50"],
            )
            for name, metrics in row["per_class"].items()
        }
        threshold_results.append(
            ThresholdResult(row["threshold"], class_metrics)
        )

    chosen = choose_operating_threshold(
        threshold_results,
        PROMOTED_CLASSES,
    )
    chosen_row = next(
        row
        for row in calibration_rows
        if row["threshold"] == chosen.threshold
    )

    for class_name in PROMOTED_CLASSES:
        assert chosen_row["per_class"][class_name]["tp"] > 0, (
            f"Promoted class has zero validation true positives: {class_name}"
        )

    calibration = {
        "stage": "B4_1_VALIDATION_CALIBRATION_COMPLETE",
        "project_commit": project_sha,
        "yolox_commit": YOLOX_COMMIT,
        "checkpoint_sha256": checkpoint_sha,
        "validation_images": 45,
        "frozen_test_images": 45,
        "frozen_test_used": False,
        "nms_threshold": NMS_THRESHOLD,
        "promoted_classes": list(PROMOTED_CLASSES),
        "diagnostic_only_classes": list(DIAGNOSTIC_ONLY_CLASSES),
        "threshold_candidates": calibration_rows,
        "selected_threshold": chosen.threshold,
        "selection_rule": (
            "max macro F1 across promoted classes; tie-break macro precision; "
            "then higher confidence threshold"
        ),
    }
    calibration_path = DRIVE_B4 / "b4-validation-calibration.json"
    calibration_path.write_text(json.dumps(calibration, indent=2))

    cat_ids = sorted(coco_gt.cats)
    class_order = [
        coco_gt.cats[cat_id]["name"]
        for cat_id in cat_ids
    ]
    manifest = {
        "stage": "B4_CANDIDATE_FROZEN",
        "project_commit": project_sha,
        "yolox_commit": YOLOX_COMMIT,
        "model_family": "YOLOX-Nano",
        "checkpoint_sha256": checkpoint_sha,
        "input_size": [416, 416],
        "model_class_order": class_order,
        "supported_classes": list(PROMOTED_CLASSES),
        "diagnostic_only_classes": list(DIAGNOSTIC_ONLY_CLASSES),
        "confidence_threshold": chosen.threshold,
        "nms_threshold": NMS_THRESHOLD,
        "validation_images": 45,
        "frozen_test_images": 45,
        "frozen_test_used": False,
        "threshold_source": "validation-only B4.1 calibration",
        "preprocess": "YOLOX validation preprocessing / 416x416",
        "postprocess": "YOLOX decode + class-aware NMS",
        "limitations": [
            "Educational prototype only; not weld certification or NDT.",
            "Undercut is not a supported v0.1 class.",
            "Canonical dataset contains no true negative/background images.",
            "Independent phone-image sanity evidence is still required in B7.",
        ],
    }
    manifest_path = DRIVE_B4 / "model-manifest.candidate.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    manifest_sha = sha256_file(manifest_path)

    print(json.dumps(chosen_row, indent=2))
    print("B4.1 calibration:", calibration_path)
    print("Frozen candidate manifest:", manifest_path)
    print("Manifest SHA-256:", manifest_sha)
    print("SAFE STOP: do not run the frozen test until this manifest is reviewed.")


if __name__ == "__main__":
    main()
