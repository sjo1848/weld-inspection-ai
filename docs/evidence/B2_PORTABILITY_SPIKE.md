# B2 — YOLOX-Nano Browser Portability Spike

Status: **PREPARED / EXECUTION PENDING**

## Purpose

De-risk browser deployment before any project-specific training. This spike proves only graph/runtime portability; it does not prove weld-defect quality.

## Reference model

Use the official upstream YOLOX-Nano COCO ONNX artifact as a graph-family reference:

- Upstream repository: `https://github.com/Megvii-BaseDetection/YOLOX`
- Official ONNX export tool: `tools/export_onnx.py`
- Official ONNX Runtime demo: `demo/ONNXRuntime/README.md`
- Reference release artifact: `https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_nano.onnx`
- Upstream-reported model size class: ~0.91M parameters
- Reference input: `1×3×416×416`
- Upstream export default: ONNX opset 11

The reference model has COCO classes and is **not** a weld detector. It is used only to answer: “Can the YOLOX-Nano graph family load and execute in the intended browser runtime path?”

## Runtime surface

`apps/web/portability.html` is a development-only probe. `apps/web/src/ml/runtime.ts` owns provider selection:

1. attempt WebGPU when the browser exposes it;
2. on WebGPU initialization/execution-provider failure, record a warning and fall back to WebAssembly;
3. WebAssembly remains the compatibility baseline.

The probe creates a deterministic zero-valued `float32` tensor with shape `1×3×416×416`, executes one inference, and records provider, input/output names, output shapes, warnings and elapsed time.

## Minimal execution recipe

```bash
corepack enable
pnpm install
mkdir -p apps/web/public/models
curl -L \
  https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_nano.onnx \
  -o apps/web/public/models/yolox_nano-coco-ref.onnx
pnpm web:typecheck
pnpm web:dev
```

Open:

```text
http://localhost:5173/portability.html?model=/models/yolox_nano-coco-ref.onnx
```

Run the probe and capture exact Git HEAD, browser/version, provider, output tensor metadata and result.

## Exit classification

**PASS for B2 primary-family portability** when the official YOLOX-Nano graph completes an inference through ONNX Runtime Web using WASM on the reference Chromium path. WebGPU success is valuable but is not required for correctness.

**REWORK** when the graph fails for a repairable packaging/import/export/configuration reason.

**PRIMARY MODEL PORTABILITY DEFECT** when a valid official/reference YOLOX-Nano graph cannot execute through the required WASM path after bounded debugging. This is evidence for testing the pre-approved SSDLite fallback; it is not automatically a Human Gate.

## Important limitations

- Reference-graph PASS does not prove the later 3-class custom export will pass. The promoted project model must be re-tested.
- Dummy-tensor inference proves runtime execution only, not preprocessing correctness or meaningful detections.
- WebGPU is an optimization; failure must not prevent WASM fallback.
- Do not tune product thresholds or draw product-quality conclusions from this reference model.
- The downloaded reference `.onnx` is execution evidence/artifact only and must not be committed to Git.

## Evidence still pending

- reference model SHA-256 and byte size;
- package install/typecheck result;
- actual browser/WASM execution result;
- actual WebGPU result where supported;
- exact observed input/output tensor names/shapes;
- runtime/browser version and execution HEAD.
