from __future__ import annotations

import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tarfile
import time

import torch
import torchvision
from google.colab import drive, files

PROJECT_REPO = "https://github.com/sjo1848/weld-inspection-ai.git"
PROJECT_BRANCH = "build/mvp-v0.1"
YOLOX_REPO = "https://github.com/Megvii-BaseDetection/YOLOX.git"
YOLOX_COMMIT = "6ddff4824372906469a7fae2dc3206c7aa4bbaee"
TOTAL_EPOCHS = 80
REQUIRED_ARCHIVE = "weld-v0.1-materialized.tar.gz"

PROJECT = pathlib.Path("/content/weld-inspection-ai")
YOLOX = pathlib.Path("/content/YOLOX-weld-vendor")
DRIVE_ROOT = pathlib.Path("/content/drive/MyDrive/WELD-VISION-001/B3")
INPUT_DIR = DRIVE_ROOT / "input"
OUTPUT_ROOT = DRIVE_ROOT / "YOLOX_outputs"
EVIDENCE_DIR = DRIVE_ROOT / "evidence"


def run(cmd, cwd=None, env=None, check=True):
    print("+", " ".join(str(part) for part in cmd))
    return subprocess.run(
        [str(part) for part in cmd],
        cwd=cwd,
        env=env,
        check=check,
    )


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_checkpoint_epoch(path):
    try:
        checkpoint = torch.load(path, map_location="cpu", weights_only=False)
    except TypeError:
        checkpoint = torch.load(path, map_location="cpu")
    return int(checkpoint.get("start_epoch", 0))


def usable_checkpoint(*candidates):
    usable = []
    for path in candidates:
        if not path.exists():
            continue
        try:
            epoch = load_checkpoint_epoch(path)
        except Exception as exc:
            print(f"Ignoring unreadable checkpoint {path}: {exc}")
            continue
        usable.append((epoch, path))
    return max(usable, default=(0, None), key=lambda item: item[0])


def clone_project():
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


def prepare_dataset():
    drive_archive = INPUT_DIR / REQUIRED_ARCHIVE
    if not drive_archive.exists():
        print("First run only: upload", REQUIRED_ARCHIVE)
        uploaded = files.upload()
        assert REQUIRED_ARCHIVE in uploaded, f"Upload exactly {REQUIRED_ARCHIVE}"
        drive_archive.write_bytes(uploaded[REQUIRED_ARCHIVE])
        print("Saved persistent copy to:", drive_archive)
    else:
        print("Using persistent archive from Google Drive:", drive_archive)

    materialized_root = PROJECT / "data/materialized"
    yolox_data_root = PROJECT / "data/yolox/weld-v0.1"
    materialized_root.mkdir(parents=True, exist_ok=True)
    run(["tar", "-xzf", drive_archive, "-C", materialized_root])
    run(
        [sys.executable, "-m", "pip", "install", "-q", "-e", ".[dev]"],
        cwd=PROJECT,
    )
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
    )

    counts = {}
    for split in ("train", "val", "test"):
        split_dir = yolox_data_root / f"{split}2017"
        counts[split] = sum(1 for path in split_dir.iterdir() if path.is_file())
    print("Physical counts:", counts)
    assert counts == {"train": 358, "val": 45, "test": 45}
    return yolox_data_root


def prepare_yolox():
    if YOLOX.exists():
        shutil.rmtree(YOLOX)
    run(["git", "clone", "-q", YOLOX_REPO, YOLOX])
    run(["git", "checkout", YOLOX_COMMIT], cwd=YOLOX)
    yolox_sha = subprocess.check_output(
        ["git", "-C", str(YOLOX), "rev-parse", "HEAD"],
        text=True,
    ).strip()
    assert yolox_sha == YOLOX_COMMIT

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

    weights_dir = DRIVE_ROOT / "weights"
    weights_dir.mkdir(parents=True, exist_ok=True)
    pretrained = weights_dir / "yolox_nano.pth"
    if not pretrained.exists():
        weights_url = (
            "https://github.com/Megvii-BaseDetection/YOLOX/releases/download/"
            "0.1.1rc0/yolox_nano.pth"
        )
        run(["wget", "-q", "-O", pretrained, weights_url])
    return yolox_sha, pretrained


def smoke_test(base_env, exp_path, pretrained, batch, gpu_info, project_sha, yolox_sha):
    smoke_marker = EVIDENCE_DIR / "smoke-pass.json"
    if smoke_marker.exists():
        print("Smoke already passed in an earlier session:", smoke_marker)
        return smoke_marker

    smoke_output = pathlib.Path("/content/weld-b3-smoke-output")
    if smoke_output.exists():
        shutil.rmtree(smoke_output)

    smoke_env = base_env.copy()
    smoke_env["WELD_YOLOX_OUTPUT_DIR"] = str(smoke_output)
    smoke_env["WELD_YOLOX_EPOCHS"] = "1"
    smoke_cmd = [
        sys.executable,
        "tools/train.py",
        "-f",
        exp_path,
        "-expn",
        "weld_nano_v0_1_smoke",
        "-d",
        "1",
        "-b",
        str(batch),
        "--fp16",
        "-c",
        pretrained,
    ]
    started = time.time()
    smoke = run(smoke_cmd, cwd=YOLOX, env=smoke_env, check=False)
    seconds = time.time() - started
    assert smoke.returncode == 0, "B3 smoke failed. Do not start the main training."

    smoke_marker.write_text(
        json.dumps(
            {
                "status": "PASS",
                "seconds": seconds,
                "batch": batch,
                "gpu": gpu_info,
                "project_commit": project_sha,
                "yolox_commit": yolox_sha,
            },
            indent=2,
        )
    )
    print("Smoke PASS:", smoke_marker)
    return smoke_marker


def run_or_resume_training(base_env, exp_path, pretrained, batch):
    train_name = "weld_nano_v0_1_train"
    train_dir = OUTPUT_ROOT / train_name
    latest = train_dir / "latest_ckpt.pth"
    last_epoch = train_dir / "last_epoch_ckpt.pth"
    best = train_dir / "best_ckpt.pth"
    train_log = EVIDENCE_DIR / "b3-train-console.log"

    completed_epoch, resume_path = usable_checkpoint(latest, last_epoch)
    print("Persisted completed epoch:", completed_epoch, "/", TOTAL_EPOCHS)
    if completed_epoch >= TOTAL_EPOCHS:
        print("Training is already complete.")
        return completed_epoch, latest, best, train_log, train_dir

    train_env = base_env.copy()
    train_env["WELD_YOLOX_OUTPUT_DIR"] = str(OUTPUT_ROOT)
    train_env["WELD_YOLOX_EPOCHS"] = str(TOTAL_EPOCHS)

    if resume_path is not None:
        training_args = ["--resume", "-c", resume_path]
        print("Resuming from:", resume_path)
    else:
        training_args = ["-c", pretrained]
        print("Starting transfer learning from pretrained YOLOX-Nano")

    train_cmd = [
        sys.executable,
        "tools/train.py",
        "-f",
        exp_path,
        "-expn",
        train_name,
        "-d",
        "1",
        "-b",
        str(batch),
        "--fp16",
        *training_args,
    ]
    shell_cmd = " ".join(subprocess.list2cmdline([str(part)]) for part in train_cmd)
    log_arg = subprocess.list2cmdline([str(train_log)])
    shell_cmd += f" 2>&1 | tee -a {log_arg}"

    print("Checkpoint progress is persisted in Google Drive after every completed epoch.")
    print("If Colab stops, reopen this notebook and Run all again.")
    training = subprocess.run(
        ["bash", "-lc", f"set -o pipefail; {shell_cmd}"],
        cwd=YOLOX,
        env=train_env,
    )
    if training.returncode != 0:
        print("Training stopped before completion; persisted progress can be resumed.")

    completed_epoch, _ = usable_checkpoint(latest, last_epoch)
    return completed_epoch, latest, best, train_log, train_dir


def write_evidence(
    project_sha,
    yolox_sha,
    pretrained,
    smoke_marker,
    batch,
    completed_epoch,
    latest,
    best,
    train_log,
    train_dir,
):
    status = (
        "B3_SMOKE_PASS_AND_TRAINING_COMPLETE"
        if completed_epoch >= TOTAL_EPOCHS
        else "B3_RESUMABLE_TRAINING_INCOMPLETE"
    )
    evidence = {
        "status": status,
        "project_commit": project_sha,
        "yolox_commit": yolox_sha,
        "python": sys.version,
        "torch": torch.__version__,
        "cuda": torch.version.cuda,
        "gpu": torch.cuda.get_device_name(0),
        "vram_bytes": torch.cuda.get_device_properties(0).total_memory,
        "batch": batch,
        "target_epochs": TOTAL_EPOCHS,
        "completed_epoch": completed_epoch,
        "train_images": 358,
        "val_images": 45,
        "frozen_test_images": 45,
        "pretrained_sha256": sha256(pretrained),
        "latest_ckpt": str(latest) if latest.exists() else None,
        "best_ckpt": str(best) if best.exists() else None,
        "latest_ckpt_sha256": sha256(latest) if latest.exists() else None,
        "best_ckpt_sha256": sha256(best) if best.exists() else None,
        "note": "Frozen project test was not used for B3 tuning.",
    }
    evidence_json = EVIDENCE_DIR / "b3-environment.json"
    evidence_json.write_text(json.dumps(evidence, indent=2))
    print(json.dumps(evidence, indent=2))

    if completed_epoch < TOTAL_EPOCHS:
        print("SAFE STOP: progress is persisted in Google Drive.")
        print("Reopen with a GPU and Run all again to resume.")
        return None

    package = DRIVE_ROOT / "weld-b3-evidence.tar.gz"
    sources = [
        evidence_json,
        smoke_marker,
        train_log,
        train_dir / "train_log.txt",
        latest,
        best,
    ]
    with tarfile.open(package, "w:gz") as archive:
        for path in sources:
            if path.exists():
                archive.add(path, arcname=path.name)
    print("B3 evidence package:", package)
    print("Upload that file to ChatGPT for B3 audit and B4 promotion work.")
    return package


def main():
    print("Python:", sys.version)
    run(["nvidia-smi"])
    assert torch.cuda.is_available(), "CUDA GPU is not available in this runtime"

    props = torch.cuda.get_device_properties(0)
    gpu_info = {
        "torch": torch.__version__,
        "torchvision": torchvision.__version__,
        "cuda": torch.version.cuda,
        "gpu": torch.cuda.get_device_name(0),
        "vram_bytes": props.total_memory,
    }
    print(json.dumps(gpu_info, indent=2))

    drive.mount("/content/drive")
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

    project_sha = clone_project()
    print("Project HEAD:", project_sha)
    yolox_data_root = prepare_dataset()
    yolox_sha, pretrained = prepare_yolox()
    print("YOLOX HEAD:", yolox_sha)
    print("Pretrained SHA-256:", sha256(pretrained))

    vram_gib = torch.cuda.get_device_properties(0).total_memory / (1024**3)
    batch = 8 if vram_gib >= 14 else 4 if vram_gib >= 8 else 2
    print("VRAM GiB:", round(vram_gib, 2), "=> batch", batch)

    exp_path = PROJECT / "ml/yolox/weld_nano_exp.py"
    base_env = os.environ.copy()
    base_env["PYTHONPATH"] = str(YOLOX)
    base_env["WELD_YOLOX_DATA_DIR"] = str(yolox_data_root)
    base_env["WELD_YOLOX_WORKERS"] = "2"

    smoke_marker = smoke_test(
        base_env,
        exp_path,
        pretrained,
        batch,
        gpu_info,
        project_sha,
        yolox_sha,
    )
    completed_epoch, latest, best, train_log, train_dir = run_or_resume_training(
        base_env,
        exp_path,
        pretrained,
        batch,
    )
    write_evidence(
        project_sha,
        yolox_sha,
        pretrained,
        smoke_marker,
        batch,
        completed_epoch,
        latest,
        best,
        train_log,
        train_dir,
    )


if __name__ == "__main__":
    main()
