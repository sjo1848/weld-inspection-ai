# B3 Free-GPU Handoff — WELD-VISION-001

Status: ACTIVE / RESUMABLE COLAB PATH
Updated: 2026-09-17
Scope: offline YOLOX-Nano transfer-learning execution only

## Current position

Local deterministic data preparation is complete, but the project owner's machine has no NVIDIA/CUDA training path. Colab Free exposed a T4 GPU, but the original notebook treated the 80-epoch candidate as one all-or-nothing run. The user reports that the Colab execution was cancelled for excess runtime before evidence packaging completed.

This is not evidence of a model-quality failure. It is an execution-resilience failure in the original handoff: checkpoints lived only in the ephemeral Colab filesystem and the final evidence bundle was created only after all 80 epochs completed.

The handoff is now changed to a resumable design.

## Frozen project invariants

- Branch: `build/mvp-v0.1`
- Dataset split: train 358 / validation 45 / frozen test 45
- Classes: `slag inclusion`, `spatter`, `undercut`
- Source-photo overlap across project partitions: 0
- Compact input: `weld-v0.1-materialized.tar.gz` (~28 MB)
- Primary model: YOLOX-Nano
- Transfer learning only
- Train + validation only for tuning
- Frozen project test remains untouched during B3
- Upstream YOLOX commit: `6ddff4824372906469a7fae2dc3206c7aa4bbaee`
- No paid training infrastructure

## Resumable execution design

The canonical notebook remains:

`ml/notebooks/WELD_VISION_B3_COLAB.ipynb`

It now delegates execution to:

`ml/scripts/b3_colab_resumable.py`

The experiment supports a persistent output root through:

`WELD_YOLOX_OUTPUT_DIR`

The resumable runner mounts Google Drive and persists:

- the compact materialized-data archive after the first upload;
- official YOLOX-Nano pretrained weights;
- the smoke-pass marker;
- the main training console log;
- YOLOX `latest_ckpt.pth`;
- YOLOX `last_epoch_ckpt.pth`;
- YOLOX `best_ckpt.pth`;
- environment/evidence metadata.

YOLOX upstream saves `latest_ckpt.pth` after every completed epoch and exposes `--resume` plus `-c/--ckpt`. The runner selects the newest readable `latest_ckpt.pth` or `last_epoch_ckpt.pth` and resumes from the checkpoint's stored `start_epoch`.

If Colab terminates mid-epoch, at most that incomplete epoch is lost. Completed epochs already persisted in Drive remain reusable.

## User procedure

1. Open the canonical Colab notebook from the GitHub branch.
2. Select a GPU runtime.
3. Click **Run all**.
4. Authorize Google Drive when requested.
5. On the first resumable run only, upload `weld-v0.1-materialized.tar.gz`.
6. Leave the training running.
7. If Colab stops or disconnects, reopen the same notebook, select GPU and click **Run all** again.

After the first successful setup, the compact dataset and pretrained weights are reused from Google Drive. A previously passed smoke test is also skipped.

The main run remains a single bounded 80-epoch candidate. It is not converted into a hyperparameter sweep and the total target epoch count is not changed merely to accommodate session limits.

## Recovery details

Persistent root in Colab Google Drive:

`MyDrive/WELD-VISION-001/B3`

Main training output:

`MyDrive/WELD-VISION-001/B3/YOLOX_outputs/weld_nano_v0_1_train`

The runner checks both:

- `latest_ckpt.pth`
- `last_epoch_ckpt.pth`

Unreadable/corrupted candidates are ignored, allowing fallback to the other persisted checkpoint.

Upstream resume command semantics are preserved:

`tools/train.py --resume -c <persisted checkpoint>`

The experiment still uses `WELD_YOLOX_EPOCHS=80`; resumption continues toward the same total schedule rather than starting a new 80-epoch run.

## Evidence output

When epoch 80 completes, the runner creates:

`MyDrive/WELD-VISION-001/B3/weld-b3-evidence.tar.gz`

The package contains the available environment metadata, smoke marker, training logs and promoted checkpoint candidates. It must be reviewed before any B3 model-quality PASS is claimed.

Expected evidence includes:

- exact project commit;
- exact YOLOX commit;
- Python / PyTorch / CUDA versions;
- GPU and VRAM;
- batch;
- target and completed epochs;
- official pretrained checkpoint SHA-256;
- latest/best checkpoint paths and SHA-256 values;
- validation logs and COCO metrics;
- confirmation that the frozen project test was not used for tuning.

## Important limitation

Upstream YOLOX supports checkpoint resume and stores optimizer plus epoch state, but exact bit-for-bit continuation across interrupted seeded sessions is not guaranteed. The upstream trainer itself warns that restarting from checkpoints under deterministic seeding may have unexpected behavior. For this educational MVP, resumed training is accepted as the operational recovery path, while checkpoint lineage and validation evidence remain mandatory.

## B3 exit states

- `B3_SMOKE_PASS_AND_TRAINING_COMPLETE`
- `B3_RESUMABLE_TRAINING_INCOMPLETE`
- `GPU_RUNTIME_BLOCKER`
- `TRAINING_BLOCKER`

A completed 80-epoch process is not automatically a model-quality PASS. B3 closes only after metrics, checkpoint identity and validation behavior are reviewed. The frozen test remains reserved for the later promotion/evaluation stage.
