# Orchestration State — WELD-VISION-001

As of: 2026-09-15
Runtime: ChatGPT / GitHub connector
Canonical branch: `build/mvp-v0.1`
Active Task Contract: `WV-TC-BUILD-001 — Thursday MVP Vertical Slice — ACTIVE`
Draft integration surface: PR #1

## Current execution

| Increment | Status | Purpose | Evidence target |
| --- | --- | --- | --- |
| B0 Repository and harness bootstrap | IMPLEMENTED / CHECK PENDING | Create a resumable repo, Python/web environments and execution boundaries | structure exists; install/test/build commands still require execution in a package/network-capable runtime |
| B1 Dataset audit and split | RUNNING / PARTIAL | Verify source, license, annotations, class counts and leakage risk | public provenance analysis + acquisition/audit tooling exist; downloaded-file audit and split manifest pending |
| B2 Browser portability spike | PLANNED | Prove YOLOX-Nano export/runtime path before costly training | ONNX graph runnable in ORT Web/WASM or documented portability defect |
| B3 Transfer learning candidate | PLANNED | Fine-tune one bounded baseline | checkpoint + config + validation metrics + failure examples |
| B4 Model promotion | PLANNED | Export, parity-check and freeze model contract | ONNX identity/hash + manifest + parity/runtime evidence |
| B5 Thin client | PLANNED | Implement P0 mobile journey | tests + reference-path evidence |
| B6 Cloudflare delivery | PLANNED | Publish static app/model/config | deployment identity + smoke test |
| B7 Validate MVP | PLANNED | Execute acceptance/evaluation layers | validation report + supported class set |

## Current branch and candidate identity
- Candidate ref: branch `build/mvp-v0.1`, surfaced through draft PR #1.
- `execution_head` must be resolved dynamically from Git at each gate/run.
- No promoted model or substantive product artifact exists yet; repository work is bootstrap/data-tooling evidence only.

## Assurance
- Independent Critic: required for substantive artifacts and model promotion.
- Integration Review: required before technical completion of the vertical slice.
- Architecture/privacy re-review only if implementation crosses the approved client-side boundary.

## Current evidence / unknowns
- Public dataset provenance/license and source-lineage risk are documented.
- Mendeley acquisition and COCO-audit tools are implemented but have not been executed against source bytes in this runtime.
- Exact source file hashes, annotation counts, background-image coverage, original-image grouping and split integrity remain UNKNOWN.
- Python dependency install/tests and pnpm typecheck/build remain unexecuted in this runtime; B0 is therefore not declared PASS.

## External execution constraint
The current runtime can mutate GitHub/Drive but does not provide a network-capable repository shell for package installation, dataset download, ONNX export or browser execution. This is an execution constraint, not a Human Gate and not a product failure.

## Next action
Complete all static B1 preparation/critic rework available here, then hand the exact repository branch/commands to a network-capable execution runtime for the minimal B0 checks and B1 source audit. If those pass, proceed immediately to the B2 YOLOX-Nano → ONNX Runtime Web/WASM portability spike.

## Stop condition
Stop only on a material Human Gate trigger from WV-TC-BUILD-001, an unrecoverable external blocker, or completion/handoff to VALIDATE.
