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
| B1 Dataset audit and split | **PARTIAL / EXTERNAL ACQUISITION BLOCKER** | Verify source, annotations, negatives and leakage-safe split | leakage/negative risks confirmed; canonical source bytes + project split manifest still missing |
| B2 Browser portability spike | **TECHNICAL PASS** | Prove YOLOX-Nano reference graph through ORT Web/WASM | commit `988ccb54...`, CI `34927649777`, real Chrome/WASM inference PASS |
| B3 Transfer learning candidate | BLOCKED BY B1 DATA BASIS | Fine-tune one bounded baseline | checkpoint + config + validation metrics + failure examples |
| B4 Model promotion | PLANNED | Export, parity-check and freeze task model contract | ONNX identity/hash + manifest + parity/runtime evidence |
| B5 Thin client | PLANNED | Implement P0 mobile journey | tests + reference-path evidence |
| B6 Cloudflare delivery | PLANNED / DELIVERY CONSTRAINT KNOWN | Publish static app/model/config | resolve ~26.8 MB ORT WASM vs 25 MiB Static Assets limit, then deployment + smoke test |
| B7 Validate MVP | PLANNED | Execute acceptance/evaluation layers | validation report + supported class set |

## Current branch and candidate identity

- Candidate ref: branch `build/mvp-v0.1`, surfaced through draft PR #1.
- Last B0 validated candidate: `1483bbb2a32b23b805da26a061f39643fdcbe203`.
- B2 validated implementation candidate: `988ccb5458de6a94c1ab960a4bb839063c8c5fdd`.
- `execution_head` is resolved dynamically from Git for each run.
- No promoted welding task model exists yet.

## B2 validated result

- official YOLOX-Nano ONNX: 3,659,407 bytes;
- SHA-256: `c789161ed43c8269fcd4e67c67eeeb4e80c622da2eb296a20bc6007bd18a0b7d`;
- forced browser provider: WASM;
- input: `images`, float32 `[1,3,416,416]`;
- output: `output`, float32 `[1,3549,85]`;
- smoke inference latency on CI Chrome: 309.3 ms;
- Playwright result: 1/1 PASS.

B2 proves architecture-family/runtime portability only. It does not establish weld-model quality or mobile latency.

## Dataset findings / blocker

- Mendeley remains the canonical CC BY 4.0 dataset source.
- Secondary public audit confirms severe source-photo leakage in the authors' split: 46 of 47 test source photographs also occur on the train side.
- All 448 retained tiles contain at least one target defect; negative/background coverage must be supplemented.
- The former unauthenticated Mendeley files endpoint returns HTTP 403. Current official Mendeley API documentation requires OAuth Bearer authorization for dataset/file API access.
- The public Mendeley page exposes a human `Download All` action, but this runtime has no supported authenticated/browser download action for that button.

## Delivery finding

The B2 Vite build emits an ORT Web WASM runtime asset at approximately 26.8 MB, above Cloudflare Workers Static Assets' current 25 MiB per-file limit. B6 must either select a smaller compatible ORT WASM build or serve that runtime artifact through the already-allowed R2/CDN asset seam. This does not change the client-side inference boundary.

## Assurance

- Independent Critic remains required for substantive ML/model-promotion and integrated MVP evidence.
- Integration Review remains required before technical completion of the vertical slice.
- No self-approval is implied by B0/B2 technical PASS evidence.

## Next authorized action

B3 training must not start on the leaked/unverified data basis. Exhaust supported canonical acquisition routes for B1. If no autonomous authenticated/source-byte route is available, request one bounded `HUMAN_ACTION`: download the Mendeley dataset through its public `Download All` UI and provide the archive for audit. Once bytes are available, immediately execute B1 hash/COCO/group-split audit and continue to B3 without a new Human Gate.

## Stop condition

Stop only on a material Human Gate trigger from `WV-TC-BUILD-001`, an external Human Action/Input that cannot be executed by the current runtime, or completion/handoff to VALIDATE.
