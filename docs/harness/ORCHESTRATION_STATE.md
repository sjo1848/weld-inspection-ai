# Orchestration State — WELD-VISION-001

As of: 2026-09-19
Runtime: ChatGPT / GitHub connector
Canonical branch: `build/mvp-v0.1`
Active Task Contract: `WV-TC-BUILD-001 — Thursday MVP Vertical Slice — ACTIVE`
Draft integration surface: PR #1

## Current execution

| Increment | Status | Purpose | Evidence target |
| --- | --- | --- | --- |
| B0 Repository and harness bootstrap | **TECHNICAL PASS** | Resumable repo, Python/web environments and execution boundaries | commit `1483bbb2...`, CI `34924440930` SUCCESS |
| B1 Dataset audit and split | **TECHNICAL PASS** | Canonical identity, annotation audit and source-independent project split | archive SHA + 448/717 canonical audit + frozen 57/7/7 source split |
| B2 Browser portability spike | **TECHNICAL PASS** | Prove YOLOX-Nano reference graph through ORT Web/WASM | commit `988ccb54...`, CI `34927649777`, real Chrome/WASM inference PASS |
| B3 Transfer learning candidate | **COMPLETE** | Fine-tune one bounded YOLOX-Nano baseline | 80/80 epochs + checkpoint SHA + validation evidence |
| B4 Model promotion | **TECHNICAL PASS** | Export, parity-check and freeze task model contract | ONNX identity/hash + final manifest + Python/browser parity PASS |
| B5 Thin client | **ACTIVE** | Implement P0 mobile journey | tests + reference-path evidence + local image privacy behavior |
| B6 Cloudflare delivery | PLANNED / DELIVERY CONSTRAINT KNOWN | Publish static app/model/config | resolve ~26.8 MB ORT WASM vs 25 MiB Static Assets limit, then deployment + smoke test |
| B7 Validate MVP | PLANNED / NEGATIVE SANITY SET REQUIRED | Execute acceptance/evaluation layers | validation report + supported class set + independent phone sanity set |

## Current branch and candidate identity

- Candidate ref: branch `build/mvp-v0.1`, surfaced through draft PR #1.
- Last B0 validated candidate: `1483bbb2a32b23b805da26a061f39643fdcbe203`.
- B2 validated implementation candidate: `988ccb5458de6a94c1ab960a4bb839063c8c5fdd`.
- B3 checkpoint candidate: `best_ckpt.pth`, SHA-256 `7e5cd8915262a0f912de33a04262e7fab7b984badf70cf2f92f1a38fbac7fb8b`.
- B4.1 candidate manifest SHA-256: `a78d393a623708b59594a2df5bc6073e7c830fe36db8ab0332e811da054c64fb`.
- B4.2 frozen test is consumed and must not be rerun/tuned.
- Supported promotion set remains `spatter` + `slag inclusion`; `undercut` remains diagnostic-only.
- Final promoted ONNX: `weld-yolox-nano-v0.1.onnx`, SHA-256 `b5e980bf03113583a9a21600c3ee49a89daf2c76358fdcecf9c75db2bf7ee714`, 3,653,900 bytes.\n- Final model manifest: `model-manifest.v0.1.json`.\n- B4.3 Python parity PASS and ORT Web/WASM parity PASS.

## B1 validated result

Canonical archive:

- archive SHA-256: `6f600d8d3f8aa7bbada0f3092a7712680ca8b1c02153ecb761cf3a22d2215868`;
- 18,001 entries / 1,157,926,436 uncompressed bytes;
- 17,990 images / 11 COCO JSON files;
- 71 source photos;
- canonical base pool: 448 tiles / 717 boxes;
- classes: slag inclusion 138, spatter 417, undercut 162;
- background/negative canonical tiles: 0.

Published leakage:

- 70 source photos on train side;
- 47 source photos in published test;
- 46 shared = 97.9% of published test source photos.

Frozen project split:

- train: 57 source photos / 358 tiles / 575 boxes;
- validation: 7 source photos / 45 tiles / 71 boxes;
- test: 7 source photos / 45 tiles / 71 boxes;
- class counts in both validation and test: 14 slag inclusion / 41 spatter / 16 undercut;
- source-photo overlap across partitions: 0;
- pre-generated augmentation excluded from validation/test.

B1 is complete for task-model training. The absence/no-defect claim still requires independent negative/background sanity evidence in B7.

## B2 validated result

- official YOLOX-Nano ONNX: 3,659,407 bytes;
- SHA-256: `c789161ed43c8269fcd4e67c67eeeb4e80c622da2eb296a20bc6007bd18a0b7d`;
- forced browser provider: WASM;
- input: `images`, float32 `[1,3,416,416]`;
- output: `output`, float32 `[1,3549,85]`;
- smoke inference latency on CI Chrome: 309.3 ms;
- Playwright result: 1/1 PASS.

B2 proves architecture-family/runtime portability only. It does not establish weld-model quality or mobile latency.

## B3/B4 validated result

B3:
- 80/80 transfer-learning epochs completed on Tesla T4;
- checkpoint SHA-256: `7e5cd8915262a0f912de33a04262e7fab7b984badf70cf2f92f1a38fbac7fb8b`.

B4.1:
- validation-only calibration on 45 images;
- confidence threshold: 0.20;
- NMS: 0.65;
- candidate manifest SHA-256: `a78d393a623708b59594a2df5bc6073e7c830fe36db8ab0332e811da054c64fb`.

B4.2 frozen held-out test:
- 45 images / 71 boxes;
- slag inclusion: P 0.5294 / R 0.6429 / F1 0.5806 / AP50 0.5227;
- spatter: P 0.7576 / R 0.6098 / F1 0.6757 / AP50 0.5476;
- undercut diagnostic: P 0.4211 / R 0.5000 / F1 0.4571 / AP50 0.3148;
- consumed marker persisted; no post-test threshold/class/checkpoint tuning is allowed.

The first B4.2 attempt exposed a YOLOX `testdev=False` image-directory binding defect and stopped at DataLoader 0/6 before inference. The successful one-shot run used the minimal `testdev=True` correction. The repository runner now carries that correction permanently.

The one-shot runner did not persist image-level FP/FN examples. That instrumentation gap must be closed using the B7 independent phone/demo sanity set rather than rerunning the frozen test.

B4.3 promoted artifact:
- exact ONNX SHA-256: `b5e980bf03113583a9a21600c3ee49a89daf2c76358fdcecf9c75db2bf7ee714`;
- 3,653,900 bytes, FP32, opset 11;
- `images` float32 `[1,3,416,416]` → `output` float32 `[1,3549,8]`;
- raw YOLOX output preserved; browser adapter remains responsible for decode/scoring/class filtering/NMS;
- PyTorch → Python ONNX Runtime parity PASS on three deterministic non-test inputs;
- ONNX Runtime Web/WASM parity PASS on the same three inputs;
- promoted Playwright test: 1/1 PASS;
- final manifest persisted in Drive.

B4 is closed as TECHNICAL PASS. This does not close the overall Build contract; B5/B6/B7 and required integrated assurance remain.

## Delivery finding

The B2 Vite build emits an ORT Web WASM runtime asset at approximately 26.8 MB, above Cloudflare Workers Static Assets' current 25 MiB per-file limit. B6 must either select a smaller compatible ORT WASM build or serve that runtime artifact through the already-allowed R2/CDN asset seam. This does not change the client-side inference boundary.

## Assurance

- Independent Critic remains required for substantive ML/model-promotion and integrated MVP evidence.
- Integration Review remains required before technical completion of the vertical slice.
- No self-approval is implied by B0/B1/B2 technical PASS evidence.
- Project test remains frozen and must not become a tuning set.

## Next authorized action

B5 is authorized inside the active Build contract. Implement the thin mobile-first client against the final `model-manifest.v0.1.json` contract:

1. image select/capture and preview;
2. local deterministic preprocessing to the exact 416×416 tensor contract;
3. ONNX Runtime Web inference with WASM required and WebGPU optional;
4. model adapter decode/scoring/class filtering/NMS using confidence 0.20 and NMS 0.65;
5. expose only `spatter` and `slag inclusion` as supported classes;
6. overlay detections back onto original-image coordinates;
7. educational result copy with no pass/fail/certification semantics;
8. explicit distinction between no detections and runtime/model failure;
9. retry/new-analysis flow;
10. automated unit/UI/reference-path evidence and proof that the core image path does not upload the user image.

Do not reopen model tuning or modify the promoted model contract during B5.

## Stop condition

Stop only on a material Human Gate trigger from `WV-TC-BUILD-001`, an external Human Action/Input that cannot be executed by the current runtime, or completion/handoff to VALIDATE.
