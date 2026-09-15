# B3 Free-GPU Handoff — WELD-VISION-001

Status: ACTIVE HANDOFF
Date: 2026-09-15
Scope: offline YOLOX-Nano transfer-learning execution only

## Why this exists

The project owner's local machine completed deterministic data preparation but does not expose an NVIDIA/CUDA training path (`nvidia-smi` is unavailable). CPU training is intentionally not used. This is a compute-location constraint, not a product-architecture change and not a Human Gate.

## Frozen evidence entering the handoff

- Branch: `build/mvp-v0.1`
- Validated training-prep head before this handoff: `8f023a00288b8efa6b41ad8fcdb1bc86038347d1`
- CI #26: SUCCESS
- Python used locally: 3.11.16
- Materialized dataset: `data/materialized/weld-v0.1`
- Strict YOLOX layout: `data/yolox/weld-v0.1`
- Train: 358 images
- Validation: 45 images
- Frozen test: 45 images
- Classes: `slag inclusion`, `spatter`, `undercut`
- Compact training handoff: `weld-v0.1-materialized.tar.gz` (~28 MB)
- Local hardware outcome: `HARDWARE_BLOCKER`
- Torch/CUDA/GPU/VRAM/checkpoints/metrics: UNKNOWN until external GPU execution

## Execution policy

1. Preferred zero-cost execution seam: Google Colab Free with GPU enabled.
2. Kaggle GPU notebook is an acceptable fallback if Colab does not provide a GPU session.
3. Upload only the compact `weld-v0.1-materialized.tar.gz`; do not upload the 1.1 GB canonical archive.
4. Training/tuning may use only train + validation.
5. The 45-image project test partition remains frozen until B4 promotion evaluation.
6. Primary model remains YOLOX-Nano; SSDLite fallback is not activated by this hardware blocker.
7. Transfer learning only; do not train from scratch.
8. Upstream YOLOX must be pinned to commit `6ddff4824372906469a7fae2dc3206c7aa4bbaee`.
9. Start with a 1-epoch smoke run. Only continue to the bounded 80-epoch candidate if the smoke is green.
10. Do not claim model-quality PASS until validation metrics and checkpoint identity are recorded.

## Colab Free procedure

### 1. Start GPU runtime

Open a new Colab notebook and select a GPU runtime. First cell:

```bash
!nvidia-smi
```

If no NVIDIA GPU is exposed, stop and use the Kaggle fallback. Do not attempt a long CPU training run.

### 2. Clone the project branch

```bash
%cd /content
!git clone --branch build/mvp-v0.1 --single-branch https://github.com/sjo1848/weld-inspection-ai.git
%cd /content/weld-inspection-ai
!git rev-parse HEAD
```

Record the exact project commit used for training.

### 3. Upload compact materialized data

Use Colab's file upload UI to upload `weld-v0.1-materialized.tar.gz` to `/content`.

Then:

```bash
%cd /content/weld-inspection-ai
!mkdir -p data/materialized
!tar -xzf /content/weld-v0.1-materialized.tar.gz -C data/materialized
!python -m pip install -e '.[dev]'
!python ml/scripts/prepare_yolox_dataset.py data/materialized/weld-v0.1 --out data/yolox/weld-v0.1 --link-mode copy
!cat data/yolox/weld-v0.1/yolox-dataset-summary.json
```

Required physical counts:

```bash
!find data/yolox/weld-v0.1/train2017 -type f | wc -l
!find data/yolox/weld-v0.1/val2017 -type f | wc -l
!find data/yolox/weld-v0.1/test2017 -type f | wc -l
```

Expected exactly: 358 / 45 / 45.

### 4. Pin upstream YOLOX

```bash
%cd /content
!git clone https://github.com/Megvii-BaseDetection/YOLOX.git YOLOX-weld-vendor
%cd /content/YOLOX-weld-vendor
!git checkout 6ddff4824372906469a7fae2dc3206c7aa4bbaee
!git rev-parse HEAD
```

Use the notebook's existing CUDA-enabled PyTorch. Install only the training dependencies needed by upstream source execution:

```bash
!python -m pip install -U pip
!python -m pip install loguru tqdm thop ninja tabulate psutil tensorboard pycocotools opencv-python
```

The source tree can be executed directly from its root; a package build is not required for the smoke path.

Verify GPU/PyTorch:

```python
import torch
print('torch:', torch.__version__)
print('cuda available:', torch.cuda.is_available())
print('cuda version:', torch.version.cuda)
if torch.cuda.is_available():
    p = torch.cuda.get_device_properties(0)
    print('gpu:', torch.cuda.get_device_name(0))
    print('vram bytes:', p.total_memory)
assert torch.cuda.is_available(), 'GPU runtime is not usable'
```

### 5. Download official YOLOX-Nano pretrained checkpoint

```bash
%cd /content/YOLOX-weld-vendor
!mkdir -p weights
!wget -O weights/yolox_nano.pth https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_nano.pth
!sha256sum weights/yolox_nano.pth
```

Record the SHA-256 returned by the runtime.

### 6. Set the frozen project paths

```bash
%env WELD_YOLOX_DATA_DIR=/content/weld-inspection-ai/data/yolox/weld-v0.1
```

Experiment:

```text
/content/weld-inspection-ai/ml/yolox/weld_nano_exp.py
```

Pretrained checkpoint:

```text
/content/YOLOX-weld-vendor/weights/yolox_nano.pth
```

### 7. Select a conservative batch

Use VRAM as a bounded heuristic:

- >= 14 GiB: batch 8
- >= 8 GiB: batch 4
- otherwise: batch 2

Do not maximize memory usage. If the smoke OOMs, reduce the batch once and retry once.

### 8. One-epoch smoke

```bash
%cd /content/YOLOX-weld-vendor
%env WELD_YOLOX_EPOCHS=1
%env WELD_YOLOX_WORKERS=2
!python tools/train.py -f /content/weld-inspection-ai/ml/yolox/weld_nano_exp.py -d 1 -b <BATCH> --fp16 -c /content/YOLOX-weld-vendor/weights/yolox_nano.pth
```

If FP16 itself is the blocker, repeat once without `--fp16` and record the reason.

Smoke PASS requires:

- train data loads;
- validation data loads;
- three custom classes are recognized;
- pretrained checkpoint is consumed as transfer-learning input;
- mismatched 80-class head tensors are skipped rather than treated as fatal;
- forward/backward completes;
- validation completes;
- checkpoint is written;
- no tuning/evaluation uses `test2017`.

### 9. Bounded 80-epoch candidate

Only after smoke PASS:

```bash
%cd /content/YOLOX-weld-vendor
%env WELD_YOLOX_EPOCHS=80
!python tools/train.py -f /content/weld-inspection-ai/ml/yolox/weld_nano_exp.py -d 1 -b <SAME_BATCH> --fp16 -c /content/YOLOX-weld-vendor/weights/yolox_nano.pth
```

Do not launch alternate models or hyperparameter sweeps.

## Evidence to preserve before the runtime disappears

Record or download:

- exact `weld-inspection-ai` commit;
- exact YOLOX upstream commit;
- Python version;
- PyTorch version;
- CUDA version;
- GPU model and VRAM;
- batch, epochs, FP16 yes/no;
- official pretrained checkpoint SHA-256;
- exact training command;
- elapsed training time;
- `best_ckpt.pth` and `latest_ckpt.pth` paths;
- SHA-256 of `best_ckpt.pth`;
- best epoch;
- validation AP50 and AP50:95 reported by YOLOX/COCOeval;
- per-class AP/AR output reported by YOLOX;
- warnings/errors;
- proof that frozen test was not used for tuning.

Before ending the free GPU session, download the best checkpoint plus the training logs/evidence bundle. Do not commit weights to Git.

## Kaggle fallback

If Colab Free exposes no GPU, use a Kaggle notebook with GPU acceleration. The same invariants apply: clone `build/mvp-v0.1`, pin YOLOX to `6ddff4824372906469a7fae2dc3206c7aa4bbaee`, upload only the 28 MB compact tar, rebuild the strict YOLOX layout, smoke for 1 epoch, then run one 80-epoch candidate. Keep project test frozen.

## Exit states

- `B3_SMOKE_PASS_AND_TRAINING_COMPLETE`
- `B3_SMOKE_PASS_TRAINING_NOT_RUN`
- `GPU_RUNTIME_BLOCKER`
- `TRAINING_BLOCKER`

A completed process is not automatically a model-quality PASS. B3 model evidence closes only after metrics, checkpoint identity and validation behavior are reviewed.