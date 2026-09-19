from __future__ import annotations

import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tarfile

from google.colab import drive

PROJECT_REPO = "https://github.com/sjo1848/weld-inspection-ai.git"
PROJECT_BRANCH = "build/mvp-v0.1"

PROJECT = pathlib.Path("/content/weld-inspection-ai")
WORK = pathlib.Path("/content/weld-b5-reference")
DRIVE_B3_ARCHIVE = pathlib.Path(
    "/content/drive/MyDrive/WELD-VISION-001/B3/input/weld-v0.1-materialized.tar.gz"
)
DRIVE_B4_MODEL = pathlib.Path(
    "/content/drive/MyDrive/WELD-VISION-001/B4/weld-yolox-nano-v0.1.onnx"
)
DRIVE_B5 = pathlib.Path("/content/drive/MyDrive/WELD-VISION-001/B5")

EXPECTED_MODEL_SHA256 = (
    "b5e980bf03113583a9a21600c3ee49a89daf2c76358fdcecf9c75db2bf7ee714"
)
SUPPORTED_CLASSES = {"spatter", "slag inclusion"}


def run(cmd: list[str | pathlib.Path], *, cwd=None, env=None) -> None:
    print("+", " ".join(str(part) for part in cmd))
    subprocess.run(
        [str(part) for part in cmd],
        cwd=cwd,
        env=env,
        check=True,
    )


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def clone_project() -> str:
    if PROJECT.exists() and (PROJECT / ".git").exists():
        run(["git", "-C", PROJECT, "fetch", "origin", PROJECT_BRANCH])
        run(["git", "-C", PROJECT, "switch", PROJECT_BRANCH])
        run(["git", "-C", PROJECT, "reset", "--hard", f"origin/{PROJECT_BRANCH}"])
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


def extract_materialized_archive() -> pathlib.Path:
    if not DRIVE_B3_ARCHIVE.is_file():
        raise SystemExit(f"Missing B3 materialized archive: {DRIVE_B3_ARCHIVE}")

    extracted = WORK / "materialized"
    if extracted.exists():
        shutil.rmtree(extracted)
    extracted.mkdir(parents=True, exist_ok=True)

    print("+ extracting", DRIVE_B3_ARCHIVE)
    with tarfile.open(DRIVE_B3_ARCHIVE, "r:gz") as archive:
        archive.extractall(extracted)

    annotation_candidates = list(extracted.rglob("val/_annotations.coco.json"))
    if len(annotation_candidates) != 1:
        raise SystemExit(
            "Expected exactly one materialized val annotation file; "
            f"found {len(annotation_candidates)}"
        )
    return annotation_candidates[0]


def choose_reference_image(annotation_path: pathlib.Path) -> pathlib.Path:
    payload = json.loads(annotation_path.read_text())
    category_name_by_id = {
        int(category["id"]): str(category["name"])
        for category in payload["categories"]
    }
    supported_ids = {
        category_id
        for category_id, name in category_name_by_id.items()
        if name in SUPPORTED_CLASSES
    }

    supported_image_ids = {
        int(annotation["image_id"])
        for annotation in payload["annotations"]
        if int(annotation["category_id"]) in supported_ids
    }

    image_by_id = {
        int(image["id"]): image
        for image in payload["images"]
    }

    for image_id in sorted(supported_image_ids):
        image = image_by_id.get(image_id)
        if not image:
            continue
        candidate = annotation_path.parent / "images" / str(image["file_name"])
        if candidate.is_file():
            return candidate

    raise SystemExit("No validation image with a supported-class annotation was found")


def prepare_promoted_model() -> pathlib.Path:
    if not DRIVE_B4_MODEL.is_file():
        raise SystemExit(f"Missing promoted B4 ONNX: {DRIVE_B4_MODEL}")

    actual_sha = sha256_file(DRIVE_B4_MODEL)
    if actual_sha != EXPECTED_MODEL_SHA256:
        raise SystemExit(
            f"Promoted ONNX SHA mismatch: {actual_sha} != {EXPECTED_MODEL_SHA256}"
        )

    destination = PROJECT / "apps/web/public/models/weld-yolox-nano-v0.1.onnx"
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(DRIVE_B4_MODEL, destination)
    return destination


def run_reference_path(reference_image: pathlib.Path) -> dict:
    DRIVE_B5.mkdir(parents=True, exist_ok=True)
    evidence_path = DRIVE_B5 / "b5-reference-path.json"
    screenshot_path = DRIVE_B5 / "b5-reference-path.png"

    if evidence_path.exists():
        evidence_path.unlink()

    run(["node", "--version"])
    run(["corepack", "enable"])
    run(["corepack", "prepare", "pnpm@10.15.1", "--activate"])
    run(["pnpm", "install", "--no-frozen-lockfile"], cwd=PROJECT)
    run(
        [
            "pnpm",
            "--filter",
            "@weld-inspection-ai/web",
            "exec",
            "playwright",
            "install",
            "--with-deps",
            "chromium",
        ],
        cwd=PROJECT,
    )
    run(["pnpm", "web:build"], cwd=PROJECT)

    env = os.environ.copy()
    env["B5_REFERENCE_IMAGE"] = str(reference_image)
    env["B5_EVIDENCE_JSON"] = str(evidence_path)
    env["B5_SCREENSHOT"] = str(screenshot_path)

    run(
        [
            "pnpm",
            "--filter",
            "@weld-inspection-ai/web",
            "test:b5-reference",
        ],
        cwd=PROJECT,
        env=env,
    )

    if not evidence_path.is_file():
        raise SystemExit("B5 reference-path evidence was not produced")

    evidence = json.loads(evidence_path.read_text())
    if evidence.get("status") != "PASS":
        raise SystemExit("B5 reference path did not PASS")

    if evidence.get("privacy", {}).get("nonReadRequestCount") != 0:
        raise SystemExit("B5 privacy evidence found non-read network requests")
    if evidence.get("privacy", {}).get("requestBodiesCount") != 0:
        raise SystemExit("B5 privacy evidence found request bodies")

    return evidence


def main() -> None:
    drive.mount("/content/drive")
    WORK.mkdir(parents=True, exist_ok=True)

    project_commit = clone_project()
    annotation_path = extract_materialized_archive()
    reference_image = choose_reference_image(annotation_path)
    promoted_model = prepare_promoted_model()

    print("B5 project commit:", project_commit)
    print("B5 reference image:", reference_image)
    print("B5 promoted model:", promoted_model)
    print("B5 promoted model SHA-256:", sha256_file(promoted_model))

    evidence = run_reference_path(reference_image)

    summary = {
        "stage": "B5_REFERENCE_PATH_COMPLETE",
        "project_commit": project_commit,
        "model_sha256": EXPECTED_MODEL_SHA256,
        "reference_partition": "validation",
        "reference_image": reference_image.name,
        "frozen_test_used": False,
        "evidence": evidence,
    }
    summary_path = DRIVE_B5 / "b5-reference-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2))

    print(json.dumps(summary, indent=2))
    print("B5 evidence:", DRIVE_B5 / "b5-reference-path.json")
    print("B5 screenshot:", DRIVE_B5 / "b5-reference-path.png")
    print("B5 summary:", summary_path)
    print("B5 REFERENCE PATH PASS")


if __name__ == "__main__":
    main()
