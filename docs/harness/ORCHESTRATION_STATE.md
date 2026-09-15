# Orchestration State — WELD-VISION-001

As of: 2026-09-15
Runtime: ChatGPT / GitHub connector
Canonical branch: `build/mvp-v0.1`
Active Task Contract: `WV-TC-BUILD-001 — Thursday MVP Vertical Slice — ACTIVE`

## Current execution

| Increment | Status | Purpose | Evidence target |
| --- | --- | --- | --- |
| B0 Repository and harness bootstrap | RUNNING | Create a resumable repo, Python/web environments and execution boundaries | repository structure + install/test commands + branch identity |
| B1 Dataset audit and split | READY | Verify source, license, annotations, class counts and leakage risk | dataset audit + split manifest + leakage statement |
| B2 Browser portability spike | PLANNED | Prove YOLOX-Nano export/runtime path before costly training | ONNX graph runnable in ORT Web/WASM or documented portability defect |
| B3 Transfer learning candidate | PLANNED | Fine-tune one bounded baseline | checkpoint + config + validation metrics + failure examples |
| B4 Model promotion | PLANNED | Export, parity-check and freeze model contract | ONNX identity/hash + manifest + parity/runtime evidence |
| B5 Thin client | PLANNED | Implement P0 mobile journey | tests + reference-path evidence |
| B6 Cloudflare delivery | PLANNED | Publish static app/model/config | deployment identity + smoke test |
| B7 Validate MVP | PLANNED | Execute acceptance/evaluation layers | validation report + supported class set |

## Current branch and candidate identity
- Candidate ref: branch `build/mvp-v0.1`.
- `execution_head` must be resolved dynamically from Git at each gate/run.
- No `substantive_product_sha` exists yet; implementation has only begun.

## Assurance
- Independent Critic: required for substantive ML/model-promotion and integrated MVP evidence.
- Integration Review: required before technical completion of the vertical slice.
- Additional architecture/privacy review only if implementation crosses the approved client-side boundary.

## Blockers
None at B0 after repository initialization.

## Next action
Finish B0 bootstrap checks, then execute B1 dataset audit and provenance/split design.

## Stop condition
Stop only on a material Human Gate trigger from WV-TC-BUILD-001, an external blocker that cannot be recovered autonomously, or completion/handoff to VALIDATE.
