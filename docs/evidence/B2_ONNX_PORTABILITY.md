# B2 — YOLOX-Nano ONNX Browser Portability Evidence

Status: **RUNNING — bounded browser proof configured; execution pending current candidate**

## Question this increment answers

Can the approved primary architecture family, YOLOX-Nano exported as ONNX, load and execute entirely in a real browser through ONNX Runtime Web using the required WebAssembly compatibility baseline?

This is a portability test only. It does **not** measure welding-defect model quality.

## Reference artifact

Official YOLOX project release:

- repository: `Megvii-BaseDetection/YOLOX`
- release tag: `0.1.1rc0`
- artifact: `yolox_nano.onnx`
- published asset size: `3,659,407` bytes
- reference input used by this probe: `1×3×416×416`, float32
- download source: official GitHub release asset

The reference graph is COCO-pretrained. It is never presented as the welding task model. Its sole role is proving that the selected model family/runtime boundary is viable before spending compute on task-specific fine-tuning.

## Browser proof

The repository now provides:

- `apps/web/portability.html` — development-only probe surface;
- `apps/web/src/portability.ts` — deterministic zero-tensor inference probe;
- `apps/web/src/ml/runtime.ts` — runtime selection with `auto`, forced `wasm`, or forced `webgpu` modes;
- multi-page Vite production build including the probe;
- Playwright test forcing the `wasm` provider in system Chrome;
- bounded GitHub Actions job that downloads the official model, verifies its byte size, records SHA-256, builds the production bundle, and runs the real browser inference proof.

## B2 PASS conditions

The reference graph must, in one bounded CI execution:

1. download from the official YOLOX GitHub release;
2. match the published 3,659,407-byte artifact size;
3. produce a captured SHA-256 identity;
4. be included only as an ephemeral CI/public build artifact, not committed to Git;
5. load through ONNX Runtime Web with the provider forced to `wasm`;
6. accept the expected `1×3×416×416` float32 input;
7. execute one inference in system Chrome without runtime/operator failure;
8. expose at least one output tensor and record its names/shapes;
9. leave WebGPU as an optional optimization rather than a correctness dependency.

## Interpretation

PASS proves the YOLOX-Nano ONNX family is compatible with the browser/WASM architecture at reference-graph level. A later promoted weld model must still repeat export/parity/browser checks because fine-tuning/export choices can change graph details.

FAIL is an implementation/portability defect to debug autonomously. Only material failure of both the primary YOLOX path and the pre-approved SSDLite fallback can trigger the model-strategy Human Gate defined by `WV-TC-BUILD-001`.
