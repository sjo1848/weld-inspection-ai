# Orchestration State — WELD-VISION-001

As of: 2026-09-15
Runtime: ChatGPT / GitHub connector
Canonical branch: `build/mvp-v0.1`
Active Task Contract: `WV-TC-BUILD-001 — Thursday MVP Vertical Slice — ACTIVE`
Draft integration surface: PR #1

## Current execution

| Increment | Status | Purpose | Evidence target |
| --- | --- | --- | --- |
| B0 Repository and harness bootstrap | **TECHNICAL PASS** | Resumable repo, Python/web environments and execution boundaries | validated commit `1483bbb2...`, CI run `34924440930` SUCCESS |
| B1 Dataset audit and split | **RUNNING / PARTIAL** | Verify source, license, annotations, negatives and leakage risk | leakage independently confirmed; canonical byte acquisition + local split manifest still open |
| B2 Browser portability spike | **RUNNING** | Prove YOLOX-Nano reference ONNX through ORT Web/WASM before training | bounded Chrome/WASM CI proof configured on current branch |
| B3 Transfer learning candidate | PLANNED | Fine-tune one bounded baseline | checkpoint + config + validation metrics + failure examples |
| B4 Model promotion | PLANNED | Export, parity-check and freeze model contract | ONNX identity/hash + manifest + parity/runtime evidence |
| B5 Thin client | PLANNED | Implement P0 mobile journey | tests + reference-path evidence |
| B6 Cloudflare delivery | PLANNED | Publish static app/model/config | deployment identity + smoke test |
| B7 Validate MVP | PLANNED | Execute acceptance/evaluation layers | validation report + supported class set |

## Current branch and candidate identity

- Candidate ref: branch `build/mvp-v0.1`, surfaced through draft PR #1.
- Last validated B0 candidate: `1483bbb2a32b23b805da26a061f39643fdcbe203`.
- `execution_head` is resolved dynamically from Git for each new CI run.
- No promoted welding model exists yet.

## Assurance

- Independent Critic is required for substantive ML/model-promotion and integrated MVP evidence.
- Integration Review is required before technical completion of the vertical slice.
- Architecture/privacy re-review applies only if implementation crosses the approved client-side boundary.

## Current findings

- B0 is proven by actual CI execution: package install, 8 Python tests, Ruff, TypeScript and Vite build all passed.
- Mendeley remains the canonical CC BY 4.0 dataset source.
- Secondary public audit confirms severe source-photo leakage in the authors' split: 46 of 47 test source photographs also occur on the train side.
- The same audit reports that every one of the 448 retained tiles contains at least one defect; negative/background coverage must therefore be supplemented.
- The old unauthenticated Mendeley public API files endpoint returns HTTP 403 from CI; canonical raw-byte acquisition remains unresolved.
- Official YOLOX release metadata exposes a 3,659,407-byte `yolox_nano.onnx` artifact suitable for the risk-first B2 portability proof.

## Next authorized action

Execute the bounded B2 real-browser/WASM CI proof on the official YOLOX-Nano reference graph. In parallel, continue only low-cost source acquisition investigation for B1. Do not begin task-specific training until a leakage-safe dataset manifest and evaluation basis are available.

## Stop condition

Stop only on a material Human Gate trigger from `WV-TC-BUILD-001`, an unrecoverable external blocker requiring a Human Action/Input, or completion/handoff to VALIDATE.
