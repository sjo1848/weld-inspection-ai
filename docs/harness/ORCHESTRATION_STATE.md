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
| B1 Dataset audit and split | **TECHNICAL PASS** | Canonical identity, annotation audit and source-independent project split | archive SHA + 448/717 canonical audit + frozen 57/7/7 source split |
| B2 Browser portability spike | **TECHNICAL PASS** | Prove YOLOX-Nano reference graph through ORT Web/WASM | commit `988ccb54...`, CI `34927649777`, real Chrome/WASM inference PASS |
| B3 Transfer learning candidate | **READY / EXECUTION DATA LOCAL** | Fine-tune one bounded YOLOX-Nano baseline | checkpoint + config + validation metrics + failure examples |
| B4 Model promotion | PLANNED | Export, parity-check and freeze task model contract | ONNX identity/hash + manifest + parity/runtime evidence |
| B5 Thin client | PLANNED | Implement P0 mobile journey | tests + reference-path evidence |
| B6 Cloudflare delivery | PLANNED / DELIVERY CONSTRAINT KNOWN | Publish static app/model/config | resolve ~26.8 MB ORT WASM vs 25 MiB Static Assets limit, then deployment + smoke test |
| B7 Validate MVP | PLANNED / NEGATIVE SANITY SET REQUIRED | Execute acceptance/evaluation layers | validation report + supported class set + independent phone sanity set |

## Current branch and candidate identity

- Candidate ref: branch `build/mvp-v0.1`, surfaced through draft PR #1.
- Last B0 validated candidate: `1483bbb2a32b23b805da26a061f39643fdcbe203`.
- B2 validated implementation candidate: `988ccb5458de6a94c1ab960a4bb839063c8c5fdd`.
- No promoted welding task model exists yet.

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

## Delivery finding

The B2 Vite build emits an ORT Web WASM runtime asset at approximately 26.8 MB, above Cloudflare Workers Static Assets' current 25 MiB per-file limit. B6 must either select a smaller compatible ORT WASM build or serve that runtime artifact through the already-allowed R2/CDN asset seam. This does not change the client-side inference boundary.

## Assurance

- Independent Critic remains required for substantive ML/model-promotion and integrated MVP evidence.
- Integration Review remains required before technical completion of the vertical slice.
- No self-approval is implied by B0/B1/B2 technical PASS evidence.
- Project test remains frozen and must not become a tuning set.

## Next authorized action

B3 may start. The raw 1.1 GB archive exists on the user's machine and is intentionally not committed. The next execution step is to materialize the frozen project split against those local bytes, then run one bounded YOLOX-Nano transfer-learning candidate.

If the current runtime cannot access the local raw archive, that is a `HUMAN_ACTION` for data execution handoff, not a Human Gate and not a reason to reopen B1.

## Stop condition

Stop only on a material Human Gate trigger from `WV-TC-BUILD-001`, an external Human Action/Input that cannot be executed by the current runtime, or completion/handoff to VALIDATE.
