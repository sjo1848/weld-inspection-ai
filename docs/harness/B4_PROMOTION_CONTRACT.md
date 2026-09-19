# B4 Model Promotion Contract — WELD-VISION-001

Status: ACTIVE / BUILD AUTHORIZED
Authority: HG-WV-002 Option A + WV-TC-BUILD-001
Scope: promote the trained B3 YOLOX-Nano candidate without leaking frozen-test evidence into tuning.

## Evidence entering B4

- B0 repository/bootstrap: TECHNICAL PASS.
- B1 source-aware dataset split: TECHNICAL PASS.
- B2 YOLOX-Nano browser/WASM family portability: TECHNICAL PASS.
- B3 transfer learning: 80/80 epochs complete on Tesla T4.
- Promoted checkpoint candidate: `best_ckpt.pth`.
- Candidate SHA-256: `7e5cd8915262a0f912de33a04262e7fab7b984badf70cf2f92f1a38fbac7fb8b`.
- Frozen project test: 45 images / 71 boxes / 7 source photos; not used during B3 tuning.
- Validation evidence shows `undercut` materially weaker than the other two target classes.

## Product-class decision entering B4

Candidate supported classes for v0.1:
- `spatter`
- `slag inclusion`

Diagnostic-only / not promoted:
- `undercut`

This follows WV-EVAL-001: a materially non-functional class must not be silently retained.

## B4.1 — Validation-only calibration

Purpose:
- select the operating confidence threshold using validation only;
- keep NMS fixed at the validated experiment baseline of 0.65;
- freeze model/checkpoint identity, preprocessing, class support and thresholds.

Rules:
- inference source is `instances_val.json` only;
- frozen test must not be opened, evaluated or used for tuning;
- one global confidence threshold is selected deterministically by macro F1 over the promoted classes;
- tie-breakers are higher macro precision, then higher threshold;
- calibration evidence must include per-class precision, recall and AP@0.50 for every threshold candidate;
- output is `model-manifest.candidate.json` with `frozen_test_used=false`.

B4.1 PASS requires:
- checkpoint identity matches B3 evidence;
- validation dataset is exactly 45 images;
- promoted classes have non-zero validated true-positive behavior;
- a deterministic operating threshold is frozen;
- manifest hash is recorded.

## B4.2 — Frozen test execution

Purpose:
- measure held-out performance once after all operating choices are frozen.

Preconditions:
- B4.1 PASS;
- exact manifest SHA-256 supplied to the runner;
- exact checkpoint SHA-256 matches the manifest;
- manifest states `stage=B4_CANDIDATE_FROZEN`;
- manifest states `frozen_test_used=false`.

Rules:
- use exactly the 45-image project test split;
- do not modify confidence/NMS/classes after seeing test results;
- report precision, recall, AP@0.50 and ground-truth count per class;
- inspect representative false positives and false negatives;
- `undercut` may be measured diagnostically but remains unsupported unless a later explicit evidence-backed decision changes scope.

## B4.3 — Artifact promotion and parity

After B4.2:
- export the exact promoted checkpoint to ONNX;
- record ONNX SHA-256, tensor names/shapes and opset;
- compare PyTorch and ONNX outputs on fixed non-test parity inputs;
- execute the promoted ONNX graph through ONNX Runtime Web/WASM;
- generate the final model manifest consumed by the web adapter.

B4 TECHNICAL PASS requires:
- B4.1 calibration evidence;
- B4.2 frozen-test evidence;
- promoted checkpoint identity;
- ONNX artifact identity;
- PyTorch/ONNX parity evidence;
- browser/WASM execution evidence.

## Explicitly forbidden during B4

- retraining because frozen-test results are disappointing;
- threshold tuning against test images;
- reintroducing `undercut` without new validation evidence;
- claiming certification, pass/fail weld acceptance, NDT replacement or industrial-grade validation;
- merging PR #1 before B4 evidence and required review gates close.

## Human Gate

No new Human Gate is opened by this contract. B4 remains inside the already authorized BUILD slice. A new Human Gate is required only if evidence forces a material scope/architecture/claim change outside the active contract.
