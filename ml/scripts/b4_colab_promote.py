from __future__ import annotations

import json
import os
import pathlib
import shutil
import subprocess
import sys

import numpy as np
import torch
from google.colab import drive

PROJECT_REPO = "https://github.com/sjo1848/weld-inspection-ai.git"
PROJECT_BRANCH = "build/mvp-v0.1"
YOLOX_REPO = "https://github.com/Megvii-BaseDetection/YOLOX.git"
YOLOX_COMMIT = "6ddff4824372906469a7fae2dc3206c7aa4bbaee"

EXPECTED_MANIFEST_SHA256 = (
    "a78d393a623708b59594a2df5bc6073e7c830fe36db8ab0332e811da054c64fb"
)
EXPECTED_CHECKPOINT_SHA256 = (
    "7e5cd8915262a0f912de33a04262e7fab7b984badf70cf2f92f1a38fbac7fb8b"
)

PROJECT = pathlib.Path("/content/weld-inspection-ai")
YOLOX = pathlib.Path("/content/YOLOX-weld-vendor")
DRIVE_B3 = pathlib.Path("/content/drive/MyDrive/WELD-VISION-001/B3")
DRIVE_B4 = pathlib.Path("/content/drive/MyDrive/WELD-VISION-001/B4")

BEST_CKPT = DRIVE_B3 / "YOLOX_outputs/weld_nano_v0_1_train/best_ckpt.pth"
CANDIDATE_MANIFEST = DRIVE_B4 / "model-manifest.candidate.json"
FROZEN_TEST_RESULT = DRIVE_B4 / "b4-frozen-test.json"
CONSUMED_MARKER = DRIVE_B4 / "frozen-test-consumed.json"

ONNX_PATH = DRIVE_B4 / "weld-yolox-nano-v0.1.onnx"
PYTHON_PARITY_PATH = DRIVE_B4 / "b4-python-onnx-parity.json"
BROWSER_REFERENCE_PATH = DRIVE_B4 / "b4-browser-reference.json"
BROWSER_EVIDENCE_PATH = DRIVE_B4 / "b4-browser-wasm-evidence.json"
FINAL_MANIFEST_PATH = DRIVE_B4 / "model-manifest.v0.1.json"

PATTERNS = ("zero", "fill114", "ramp251")
ATOL = 1e-4
RTOL = 1e-3


def run(cmd: list[str | pathlib.Path], *, cwd=None, env=None) -> None:
    print("+", " ".join(str(part) for part in cmd))
    subprocess.run(
        [str(part) for part in cmd],
        cwd=cwd,
        env=env,
        check=True,
    )


def sha256_file(path: pathlib.Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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


def prepare_yolox() -> None:
    if YOLOX.exists():
        shutil.rmtree(YOLOX)
    run(["git", "clone", "-q", YOLOX_REPO, YOLOX])
    run(["git", "checkout", YOLOX_COMMIT], cwd=YOLOX)
    run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "-q",
            "loguru",
            "onnx",
            "onnxruntime",
        ]
    )


def make_input(pattern: str) -> np.ndarray:
    shape = (1, 3, 416, 416)
    if pattern == "zero":
        return np.zeros(shape, dtype=np.float32)
    if pattern == "fill114":
        return np.full(shape, 114.0, dtype=np.float32)
    if pattern == "ramp251":
        values = np.arange(np.prod(shape), dtype=np.float32) % 251
        return values.reshape(shape)
    raise ValueError(f"Unknown parity pattern: {pattern}")


def summarize(values: np.ndarray) -> dict[str, float]:
    flat = values.reshape(-1)
    return {
        "min": float(flat.min()),
        "max": float(flat.max()),
        "mean": float(flat.mean()),
    }


def validate_frozen_evidence() -> tuple[dict, dict]:
    for path in (
        BEST_CKPT,
        CANDIDATE_MANIFEST,
        FROZEN_TEST_RESULT,
        CONSUMED_MARKER,
    ):
        if not path.exists():
            raise SystemExit(f"Missing required B4 evidence: {path}")

    manifest_sha = sha256_file(CANDIDATE_MANIFEST)
    checkpoint_sha = sha256_file(BEST_CKPT)
    if manifest_sha != EXPECTED_MANIFEST_SHA256:
        raise SystemExit(f"Unexpected candidate manifest SHA-256: {manifest_sha}")
    if checkpoint_sha != EXPECTED_CHECKPOINT_SHA256:
        raise SystemExit(f"Unexpected checkpoint SHA-256: {checkpoint_sha}")

    manifest = json.loads(CANDIDATE_MANIFEST.read_text())
    frozen_test = json.loads(FROZEN_TEST_RESULT.read_text())
    consumed = json.loads(CONSUMED_MARKER.read_text())

    if frozen_test.get("stage") != "B4_2_FROZEN_TEST_COMPLETE":
        raise SystemExit("Frozen-test evidence is not complete")
    if consumed.get("status") != "CONSUMED":
        raise SystemExit("Frozen-test consumed marker is invalid")
    if frozen_test.get("manifest_sha256") != manifest_sha:
        raise SystemExit("Frozen-test manifest identity mismatch")
    if frozen_test.get("checkpoint_sha256") != checkpoint_sha:
        raise SystemExit("Frozen-test checkpoint identity mismatch")
    if consumed.get("manifest_sha256") != manifest_sha:
        raise SystemExit("Consumed marker manifest identity mismatch")
    if consumed.get("checkpoint_sha256") != checkpoint_sha:
        raise SystemExit("Consumed marker checkpoint identity mismatch")

    return manifest, frozen_test


def export_onnx() -> None:
    output = str(ONNX_PATH)
    run(
        [
            sys.executable,
            "tools/export_onnx.py",
            "-f",
            PROJECT / "ml/yolox/weld_nano_exp.py",
            "-c",
            BEST_CKPT,
            "--output-name",
            output,
            "--input",
            "images",
            "--output",
            "output",
            "-o",
            "11",
            "--no-onnxsim",
        ],
        cwd=YOLOX,
    )


def run_python_parity(
    manifest: dict,
    tooling_commit: str,
) -> tuple[dict, dict]:
    import onnx
    import onnxruntime as ort
    from torch import nn

    sys.path.insert(0, str(YOLOX))
    from yolox.exp import get_exp
    from yolox.models.network_blocks import SiLU
    from yolox.utils import replace_module

    onnx_model = onnx.load(str(ONNX_PATH))
    onnx.checker.check_model(onnx_model)

    exp = get_exp(str(PROJECT / "ml/yolox/weld_nano_exp.py"), None)
    model = exp.get_model()
    checkpoint = torch.load(BEST_CKPT, map_location="cpu", weights_only=False)
    model.load_state_dict(checkpoint["model"])
    model = replace_module(model, nn.SiLU, SiLU)
    model.head.decode_in_inference = False
    model.eval()

    session = ort.InferenceSession(
        str(ONNX_PATH),
        providers=["CPUExecutionProvider"],
    )
    input_meta = session.get_inputs()[0]
    output_meta = session.get_outputs()[0]

    if input_meta.name != "images":
        raise SystemExit(f"Unexpected ONNX input name: {input_meta.name}")
    if output_meta.name != "output":
        raise SystemExit(f"Unexpected ONNX output name: {output_meta.name}")

    expected_output_shape = [1, 3549, 8]
    parity_rows = []
    browser_patterns = {}

    for pattern in PATTERNS:
        input_array = make_input(pattern)
        with torch.no_grad():
            torch_output = model(torch.from_numpy(input_array)).cpu().numpy()
        ort_output = session.run(
            [output_meta.name],
            {input_meta.name: input_array},
        )[0]

        if list(torch_output.shape) != expected_output_shape:
            raise SystemExit(
                f"Unexpected PyTorch output shape: {list(torch_output.shape)}"
            )
        if list(ort_output.shape) != expected_output_shape:
            raise SystemExit(
                f"Unexpected ONNX output shape: {list(ort_output.shape)}"
            )

        abs_diff = np.abs(torch_output - ort_output)
        max_abs = float(abs_diff.max())
        mean_abs = float(abs_diff.mean())
        allclose = bool(
            np.allclose(torch_output, ort_output, rtol=RTOL, atol=ATOL)
        )
        if not allclose:
            raise SystemExit(
                f"Python -> ONNX parity failed for {pattern}: "
                f"max_abs={max_abs}, mean_abs={mean_abs}"
            )

        flat = ort_output.reshape(-1)
        browser_patterns[pattern] = {
            "sample": [float(value) for value in flat[:32]],
            "summary": summarize(ort_output),
        }
        parity_rows.append(
            {
                "pattern": pattern,
                "shape": list(ort_output.shape),
                "max_abs_diff": max_abs,
                "mean_abs_diff": mean_abs,
                "allclose": allclose,
            }
        )

    onnx_sha = sha256_file(ONNX_PATH)
    parity = {
        "stage": "B4_3_PYTHON_ONNX_PARITY_PASS",
        "tooling_commit": tooling_commit,
        "source_manifest_sha256": EXPECTED_MANIFEST_SHA256,
        "checkpoint_sha256": EXPECTED_CHECKPOINT_SHA256,
        "onnx_sha256": onnx_sha,
        "onnx_bytes": ONNX_PATH.stat().st_size,
        "opset": 11,
        "decode_in_inference": False,
        "input": {
            "name": input_meta.name,
            "dtype": str(input_meta.type),
            "shape": input_meta.shape,
        },
        "output": {
            "name": output_meta.name,
            "dtype": str(output_meta.type),
            "shape": output_meta.shape,
        },
        "rtol": RTOL,
        "atol": ATOL,
        "patterns": parity_rows,
    }
    PYTHON_PARITY_PATH.write_text(json.dumps(parity, indent=2))

    browser_reference = {
        "model_sha256": onnx_sha,
        "input_name": input_meta.name,
        "output_name": output_meta.name,
        "output_shape": expected_output_shape,
        "patterns": browser_patterns,
    }
    BROWSER_REFERENCE_PATH.write_text(
        json.dumps(browser_reference, indent=2)
    )
    return parity, browser_reference


def run_browser_wasm() -> dict:
    public_models = PROJECT / "apps/web/public/models"
    public_models.mkdir(parents=True, exist_ok=True)
    model_name = ONNX_PATH.name
    shutil.copy2(ONNX_PATH, public_models / model_name)

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
            "chromium",
        ],
        cwd=PROJECT,
    )
    run(["pnpm", "web:build"], cwd=PROJECT)

    env = os.environ.copy()
    env["B4_MODEL_URL"] = f"/models/{model_name}"
    env["B4_REFERENCE_JSON"] = str(BROWSER_REFERENCE_PATH)
    env["B4_BROWSER_EVIDENCE_JSON"] = str(BROWSER_EVIDENCE_PATH)
    run(
        [
            "pnpm",
            "--filter",
            "@weld-inspection-ai/web",
            "test:promoted",
        ],
        cwd=PROJECT,
        env=env,
    )

    if not BROWSER_EVIDENCE_PATH.exists():
        raise SystemExit("Browser parity evidence file was not produced")
    browser = json.loads(BROWSER_EVIDENCE_PATH.read_text())
    if browser.get("status") != "PASS":
        raise SystemExit("Browser WASM parity did not PASS")
    return browser


def write_final_manifest(
    manifest: dict,
    frozen_test: dict,
    parity: dict,
    browser: dict,
    tooling_commit: str,
) -> dict:
    final_manifest = {
        "stage": "B4_PROMOTED_MODEL_V0_1",
        "modelId": "weld-yolox-nano",
        "modelVersion": "0.1.0",
        "artifactPath": f"/models/{ONNX_PATH.name}",
        "artifactSha256": parity["onnx_sha256"],
        "artifactBytes": parity["onnx_bytes"],
        "architectureFamily": "YOLOX-Nano",
        "inputWidth": 416,
        "inputHeight": 416,
        "inputTensorName": "images",
        "inputDtype": "float32",
        "inputLayout": "NCHW",
        "outputTensorNames": ["output"],
        "outputTensorShapes": {"output": [1, 3549, 8]},
        "rawOutputDecodedInModel": False,
        "classMap": {
            "0": "slag inclusion",
            "1": "spatter",
            "2": "undercut",
        },
        "supportedClasses": manifest["supported_classes"],
        "diagnosticOnlyClasses": manifest["diagnostic_only_classes"],
        "confidenceThreshold": manifest["confidence_threshold"],
        "nmsThreshold": manifest["nms_threshold"],
        "preprocessingVersion": "yolox-val-416-v1",
        "postprocessingVersion": "yolox-raw-adapter-v1",
        "trainingDatasetReference": (
            "Mendeley Data DOI 10.17632/f7j76vz53p.1; "
            "source-aware project split"
        ),
        "licenseNotices": [
            "Dataset: CC BY 4.0.",
            "YOLOX upstream code/model family subject to upstream license.",
        ],
        "checkpointSha256": EXPECTED_CHECKPOINT_SHA256,
        "candidateManifestSha256": EXPECTED_MANIFEST_SHA256,
        "frozenTest": {
            "status": "CONSUMED",
            "images": frozen_test["test_images"],
            "overallAp50AllThreeModelClasses": (
                frozen_test["metrics"]["overall_ap50"]
            ),
            "evidenceFile": "b4-frozen-test.json",
        },
        "pythonOnnxParity": {
            "status": parity["stage"],
            "evidenceFile": PYTHON_PARITY_PATH.name,
        },
        "browserWasmParity": {
            "status": browser["status"],
            "evidenceFile": BROWSER_EVIDENCE_PATH.name,
        },
        "toolingCommit": tooling_commit,
        "limitations": manifest["limitations"]
        + [
            (
                "Held-out test performance is materially lower than validation; "
                "reported metrics must be presented as measured."
            ),
            (
                "Representative FP/FN visual examples were not persisted by the "
                "one-shot test runner and remain an explicit B7 evidence task."
            ),
        ],
    }
    FINAL_MANIFEST_PATH.write_text(json.dumps(final_manifest, indent=2))
    return final_manifest


def main() -> None:
    drive.mount("/content/drive")
    DRIVE_B4.mkdir(parents=True, exist_ok=True)

    manifest, frozen_test = validate_frozen_evidence()
    tooling_commit = clone_project()
    prepare_yolox()

    export_onnx()
    if not ONNX_PATH.exists():
        raise SystemExit("ONNX export did not produce the artifact")

    parity, _ = run_python_parity(manifest, tooling_commit)
    browser = run_browser_wasm()
    final_manifest = write_final_manifest(
        manifest,
        frozen_test,
        parity,
        browser,
        tooling_commit,
    )

    print(json.dumps(final_manifest, indent=2))
    print("B4.3 ONNX:", ONNX_PATH)
    print("B4.3 Python parity:", PYTHON_PARITY_PATH)
    print("B4.3 browser/WASM evidence:", BROWSER_EVIDENCE_PATH)
    print("B4.3 final manifest:", FINAL_MANIFEST_PATH)
    print("B4.3 TECHNICAL PASS")


if __name__ == "__main__":
    main()
