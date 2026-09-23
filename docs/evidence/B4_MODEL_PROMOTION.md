# B4 — Task-model Promotion Evidence

Status: **B4.1 PASS / B4.2 HELD-OUT QUANTITATIVE PASS / B4.3 IN PREPARATION**

## Identity frozen before test

- B3 checkpoint: `best_ckpt.pth`
- checkpoint SHA-256: `7e5cd8915262a0f912de33a04262e7fab7b984badf70cf2f92f1a38fbac7fb8b`
- B4.1 candidate manifest SHA-256: `a78d393a623708b59594a2df5bc6073e7c830fe36db8ab0332e811da054c64fb`
- frozen project commit recorded by the manifest: `56e4259e67911b8e7905e65fc3fe4965ab60c3d6`
- confidence threshold: `0.20`
- NMS threshold: `0.65`
- input: `1×3×416×416`
- supported classes entering held-out test: `spatter`, `slag inclusion`
- diagnostic-only class: `undercut`

No threshold, checkpoint or class-set tuning was performed after B4.1.

## B4.1 — validation-only calibration

Validation set:
- 45 images
- 71 boxes
- source-photo overlap with train/test: 0

Selected operating point at confidence 0.20:

| Class | Precision | Recall | F1 | AP50 | TP | FP | FN | GT |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| slag inclusion | 0.8182 | 0.6429 | 0.7200 | 0.6085 | 9 | 2 | 5 | 14 |
| spatter | 0.9143 | 0.7805 | 0.8421 | 0.7521 | 32 | 3 | 9 | 41 |
| undercut (diagnostic) | 0.4545 | 0.3125 | 0.3704 | 0.1713 | 5 | 6 | 11 | 16 |

B4.1 wrote:
- `b4-validation-calibration.json`
- `model-manifest.candidate.json`

The runner physically materialized validation only; the frozen test was not materialized during calibration.

## B4.2 — one-shot frozen held-out test

Frozen test:
- 45 images
- 71 boxes
- 7 source photos
- source-photo overlap with train/validation: 0
- consumed marker persisted after the successful run

Held-out result at the already-frozen operating point:

| Class | Precision | Recall | F1 | AP50 | TP | FP | FN | GT |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| slag inclusion | 0.5294 | 0.6429 | 0.5806 | 0.5227 | 9 | 8 | 5 | 14 |
| spatter | 0.7576 | 0.6098 | 0.6757 | 0.5476 | 25 | 8 | 16 | 41 |
| undercut (diagnostic) | 0.4211 | 0.5000 | 0.4571 | 0.3148 | 8 | 11 | 8 | 16 |

Overall AP50 across all three model output classes: `0.4617`.

Promoted-class macro AP50:
- validation: approximately `0.6803`
- frozen test: approximately `0.5351`

This drop is material and must remain visible in the final limitations. It is not grounds for post-test tuning.

## Gate interpretation

WV-EVAL-001 deliberately does not define a fake industrial numeric threshold. The predeclared gate requires:
- materially better than random/unusable behavior;
- true-positive behavior for every promoted class;
- no silently retained non-functional class;
- honest measured metrics;
- no leakage-based quality claim.

The held-out evidence satisfies those quantitative conditions for `spatter` and `slag inclusion`.

Therefore:
- `spatter`: **PROMOTION CANDIDATE RETAINED**
- `slag inclusion`: **PROMOTION CANDIDATE RETAINED**
- `undercut`: **NOT PROMOTED / DIAGNOSTIC ONLY**

This remains an educational prototype result, not an industrial acceptance result.

## B4.2 execution incident

The first B4.2 execution attempt exposed a YOLOX loader binding issue:
- annotation file was switched to test;
- `get_evaluator(testdev=False)` still bound image directory `val2017`;
- execution failed at DataLoader `0/6` before image inference;
- no predictions, metrics, result JSON or consumed marker were produced.

The successful one-shot run used the minimal execution correction `testdev=True`, which binds `test_ann` to `test2017`. Checkpoint, manifest, thresholds, classes and data remained unchanged.

The repository runner is corrected permanently after the held-out evidence was captured.

## Evidence gap retained for B7

The one-shot runner persisted aggregate TP/FP/FN counts but not image-level prediction records or visual FP/FN crops. The frozen test must not be rerun to repair that instrumentation gap.

Required final validation evidence will therefore obtain representative failure examples from the independent B7 phone/demo sanity set and document them explicitly.

## B4.3 boundary

B4.3 may proceed without reopening model tuning.

Required next evidence:
- FP32 ONNX export of the exact promoted checkpoint;
- artifact size and SHA-256;
- input/output tensor contract and opset;
- PyTorch → Python ONNX Runtime numerical parity on fixed non-test inputs;
- ONNX Runtime Web/WASM execution and numerical reference comparison;
- final machine-readable `model-manifest.v0.1.json`.

The approved runtime contract requires raw model tensors to be returned by the inference runtime. The browser model adapter owns YOLOX decode, scoring, class filtering and NMS. Therefore the B4.3 ONNX export uses `decode_in_inference=False`.
