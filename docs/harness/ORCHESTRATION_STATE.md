# Orchestration State — WELD-VISION-001

As of: 2026-09-15
Runtime: ChatGPT / GitHub connector
Canonical branch: `build/mvp-v0.1`
Active Task Contract: `WV-TC-BUILD-001 — Thursday MVP Vertical Slice — ACTIVE`
Draft integration surface: PR #1

## Current execution

| Increment | Status | Purpose | Evidence target |
| --- | --- | --- | --- |
| B0 Repository and harness bootstrap | **TECHNICAL PASS** | Resumable repo, Python/web environments and execution boundaries | commit `1483bbb2...`, CI `34924440930` SUCCESS |
| B1 Dataset audit and split | **PARTIAL / CANONICAL STRUCTURE AUDITED** | Verify source, annotations, negatives and leakage-safe split | direct archive/file-list audit + train-fold COCO audit complete; test COCO + archive SHA + project split manifest still open |
| B2 Browser portability spike | **TECHNICAL PASS** | Prove YOLOX-Nano reference graph through ORT Web/WASM | commit `988ccb54...`, CI `34927649777`, real Chrome/WASM inference PASS |
| B3 Transfer learning candidate | **BLOCKED BY B1 DATA BASIS** | Fine-tune one bounded baseline | checkpoint + config + validation metrics + failure examples |
| B4 Model promotion | PLANNED | Export, parity-check and freeze task model contract | ONNX identity/hash + manifest + parity/runtime evidence |
| B5 Thin client | PLANNED | Implement P0 mobile journey | tests + reference-path evidence |
| B6 Cloudflare delivery | PLANNED / DELIVERY CONSTRAINT KNOWN | Publish static app/model/config | resolve ~26.8 MB ORT WASM vs 25 MiB Static Assets limit, then deployment + smoke test |
| B7 Validate MVP | PLANNED | Execute acceptance/evaluation layers | validation report + supported class set |

## Current branch and candidate identity

- Candidate ref: branch `build/mvp-v0.1`, surfaced through draft PR #1.
- Last B0 validated candidate: `1483bbb2a32b23b805da26a061f39643fdcbe203`.
- B2 validated implementation candidate: `988ccb5458de6a94c1ab960a4bb839063c8c5fdd`.
- No promoted welding task model exists yet.

## B1 direct canonical findings

The user retained the downloaded ~1.1 GB Mendeley archive locally and supplied its complete archive listing, extracted-file listing and canonical `train_fold_1` COCO JSON.

Direct audit now establishes:

- `18,001` archive entries / `17,990` images / `11` COCO JSON files;
- `90` test images;
- five train folds × `2,864` images and five validation folds × `716` images;
- `71` source-photo identities total;
- published test uses `47` source photos and train uses `70`;
- `46 / 47` test source photos also occur in train;
- each fold pair represents `358` base train tiles with `10` augmentation variants each;
- train/validation folds share both source photos and hundreds of base-tile lineages;
- `train_fold_1` COCO: `2,864` positive images, `4,545` boxes;
- one representative per `358` base train tiles yields `568` boxes: 107 slag inclusion, 326 spatter, 135 undercut;
- no true negative/background image exists in the audited train-fold annotations.

This converts the prior leakage concern from secondary evidence into a direct canonical filename/annotation finding.

## B1 remaining Human Action

Only two small inputs are still required from the retained local archive:

1. `test/_annotations.coco.json` (`211,785` bytes);
2. `sha256sum` output for the original downloaded ZIP.

No other train/validation annotation JSON is required to establish the base-train lineage/classes for this checkpoint.

Once supplied, resume automatically with exact full-dataset annotation totals, archive pinning, deterministic source-photo-aware zero-leak split generation and then bounded B3 training.

## B2 validated result

- official YOLOX-Nano ONNX: 3,659,407 bytes;
- SHA-256: `c789161ed43c8269fcd4e67c67eeeb4e80c622da2eb296a20bc6007bd18a0b7d`;
- forced browser provider: WASM;
- input: `images`, float32 `[1,3,416,416]`;
- output: `output`, float32 `[1,3549,85]`;
- smoke inference latency on CI Chrome: 309.3 ms;
- Playwright result: 1/1 PASS.

B2 proves architecture-family/runtime portability only. It does not establish weld-model quality or mobile latency.

## Delivery finding

The B2 Vite build emits an ORT Web WASM runtime asset at approximately 26.8 MB, above Cloudflare Workers Static Assets' current 25 MiB per-file limit. B6 must either select a smaller compatible ORT WASM build or serve that runtime artifact through the already-allowed R2/CDN asset seam. This does not change the client-side inference boundary.

## Assurance

- Independent Critic remains required for substantive ML/model-promotion and integrated MVP evidence.
- Integration Review remains required before technical completion of the vertical slice.
- No self-approval is implied by B0/B2 technical PASS evidence.

## Stop condition

Current stop condition is bounded `HUMAN_ACTION` for the two small B1 inputs above. No new Human Gate is open.
