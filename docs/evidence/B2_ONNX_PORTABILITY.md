# B2 — YOLOX-Nano ONNX Browser Portability Evidence

Status: **TECHNICAL PASS — reference graph / WASM browser path**

## Candidate identity

- Build branch: `build/mvp-v0.1`
- Candidate commit: `988ccb5458de6a94c1ab960a4bb839063c8c5fdd`
- GitHub Actions run: `34927649777`
- B2 job: `104249134650`
- Job result: **SUCCESS**
- Browser: Google Chrome `152.0.7977.82` on Ubuntu 24.04 GitHub-hosted runner

## Question answered

Can the approved primary architecture family, YOLOX-Nano exported as ONNX, load and execute entirely in a real browser through ONNX Runtime Web using the required WebAssembly compatibility baseline?

**Yes, for the official YOLOX-Nano reference graph.**

This is a portability proof only. It does **not** measure welding-defect model quality and does not promote this COCO model as the task model.

## Reference artifact identity

Official YOLOX project release:

- repository: `Megvii-BaseDetection/YOLOX`
- release tag: `0.1.1rc0`
- artifact: `yolox_nano.onnx`
- exact downloaded size: `3,659,407` bytes
- SHA-256: `c789161ed43c8269fcd4e67c67eeeb4e80c622da2eb296a20bc6007bd18a0b7d`
- input used by probe: float32 `1×3×416×416`

The CI job downloaded the artifact directly from the official GitHub release and verified the exact published byte size before execution. The binary remains ephemeral and is not committed to Git.

## Real-browser execution result

Playwright launched system Chrome against the production Vite preview and forced ONNX Runtime Web to the `wasm` provider.

Captured result:

```json
{
  "status": "PASS",
  "requestedProvider": "wasm",
  "provider": "wasm",
  "warnings": [],
  "inputName": "images",
  "inputShape": [1, 3, 416, 416],
  "outputNames": ["output"],
  "outputs": {
    "output": {
      "type": "float32",
      "dims": [1, 3549, 85]
    }
  },
  "elapsedMs": 309.3
}
```

The 309.3 ms measurement is a CI-runner smoke-test latency only. It is **not** a mobile performance claim.

## Proven properties

- official YOLOX-Nano ONNX artifact is retrievable and identity-pinned;
- Vite produces the multi-page portability candidate;
- ONNX Runtime Web initializes with WebAssembly in real Chrome;
- the graph accepts the expected `images` tensor shape;
- one full inference executes without operator/runtime failure;
- output contract for this reference graph is `output: float32[1,3549,85]`;
- WebGPU is not required for correctness and remains an optional optimization.

## Delivery-size finding

The same production build emitted an ONNX Runtime Web WASM asset of approximately **26.8 MB** (`ort-wasm-simd-threaded.asyncify...wasm`). Cloudflare Workers Static Assets currently limit an individual static asset to **25 MiB**.

Therefore B6 must not assume this exact ORT WASM artifact can be uploaded unchanged as a Workers Static Asset. The approved architecture already permits an asset-delivery seam, so the implementation must choose one evidence-backed zero-cost option before deployment, such as:

1. reduce/select a smaller ORT Web WASM build while preserving the required fallback behavior; or
2. deliver the oversized runtime artifact through R2/CDN while keeping application inference entirely client-side.

This is a delivery implementation constraint, not a model-strategy Human Gate and not a failure of B2 browser portability.

## Remaining boundary

A task-specific weld detector must repeat export identity, Python→ONNX parity and browser runtime checks during B4. Fine-tuning/export can alter graph operators, inputs or outputs; the reference PASS cannot be inherited automatically.

Independent critic/integration assurance remains required before the full Build vertical slice is declared complete.
