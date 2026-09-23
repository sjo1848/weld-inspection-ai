from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys

import torch
from google.colab import drive

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from b4_colab_calibrate import (  # noqa: E402
    BEST_CKPT,
    DRIVE_B4,
    NMS_THRESHOLD,
    PROJECT,
    PROMOTED_CLASSES,
    YOLOX,
    YOLOX_COMMIT,
    clone_project,
    evaluate_threshold,
    prepare_dataset,
    prepare_yolox,
)

ACK = "I_ACKNOWLEDGE_FROZEN_TEST_ONCE"
MANIFEST_PATH = DRIVE_B4 / "model-manifest.candidate.json"
CONSUMED_MARKER = DRIVE_B4 / "frozen-test-consumed.json"
RESULT_PATH = DRIVE_B4 / "b4-frozen-test.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        "WELD-VISION-001 B4.2 frozen-test runner"
    )
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--ack", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.ack != ACK:
        raise SystemExit(
            f"Frozen test not authorized. Required --ack {ACK}"
        )

    drive.mount("/content/drive")
    if CONSUMED_MARKER.exists():
        raise SystemExit(
            "Frozen test evidence already exists. "
            "Do not rerun or tune against the test set."
        )
    if not MANIFEST_PATH.exists():
        raise SystemExit("B4.1 frozen candidate manifest is missing")

    project_sha = clone_project()
    yolox_data_root = prepare_dataset("test")
    prepare_yolox()

    sys.path.insert(0, str(PROJECT / "ml/src"))
    sys.path.insert(0, str(YOLOX))
    from yolox.exp import get_exp

    from weldvision.evaluation.promotion import (
        sha256_file,
        validate_frozen_manifest,
    )

    manifest_sha = sha256_file(MANIFEST_PATH)
    if manifest_sha != args.manifest_sha256:
        raise SystemExit(
            f"Manifest SHA mismatch: got {manifest_sha}, "
            f"expected {args.manifest_sha256}"
        )

    manifest = json.loads(MANIFEST_PATH.read_text())
    if project_sha != manifest["project_commit"]:
        raise SystemExit(
            "Repository head changed after manifest freeze. "
            "Review before frozen-test execution."
        )

    checkpoint_sha = sha256_file(BEST_CKPT)
    validate_frozen_manifest(
        manifest,
        expected_checkpoint_sha256=checkpoint_sha,
    )

    os.environ["WELD_YOLOX_DATA_DIR"] = str(yolox_data_root)
    os.environ["WELD_YOLOX_OUTPUT_DIR"] = str(
        DRIVE_B4 / "YOLOX_outputs-test"
    )
    os.environ["WELD_YOLOX_EPOCHS"] = "80"
    os.environ["WELD_YOLOX_WORKERS"] = "2"

    exp = get_exp(str(PROJECT / "ml/yolox/weld_nano_exp.py"), None)
    if exp.test_ann != "instances_test.json":
        raise SystemExit("Unexpected YOLOX test annotation contract")
    exp.test_conf = float(manifest["confidence_threshold"])
    exp.nmsthre = float(manifest["nms_threshold"])
    if exp.nmsthre != NMS_THRESHOLD:
        raise SystemExit("NMS threshold differs from B4 contract")

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
        testdev=True,
        legacy=False,
    )
    evaluator.per_class_AP = True
    evaluator.per_class_AR = True

    print("B4.2 FROZEN TEST: one successful execution only.")
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
    if len(coco_gt.getImgIds()) != 45:
        raise SystemExit(
            "Frozen project test must contain exactly 45 images"
        )

    metrics = evaluate_threshold(
        coco_gt,
        output_data,
        float(manifest["confidence_threshold"]),
    )
    result = {
        "stage": "B4_2_FROZEN_TEST_COMPLETE",
        "manifest_sha256": manifest_sha,
        "checkpoint_sha256": checkpoint_sha,
        "project_commit": project_sha,
        "yolox_commit": YOLOX_COMMIT,
        "test_images": 45,
        "confidence_threshold": manifest["confidence_threshold"],
        "nms_threshold": manifest["nms_threshold"],
        "supported_classes": list(PROMOTED_CLASSES),
        "metrics": metrics,
        "rule": (
            "No threshold, class or checkpoint tuning is allowed "
            "after this evidence."
        ),
    }
    RESULT_PATH.write_text(json.dumps(result, indent=2))

    marker = {
        "status": "CONSUMED",
        "manifest_sha256": manifest_sha,
        "checkpoint_sha256": checkpoint_sha,
        "result_file": str(RESULT_PATH),
    }
    CONSUMED_MARKER.write_text(json.dumps(marker, indent=2))

    print(json.dumps(result, indent=2))
    print("Frozen-test evidence:", RESULT_PATH)
    print("Consumed marker:", CONSUMED_MARKER)
    print("SAFE STOP: review B4.2 evidence before ONNX promotion.")


if __name__ == "__main__":
    main()
