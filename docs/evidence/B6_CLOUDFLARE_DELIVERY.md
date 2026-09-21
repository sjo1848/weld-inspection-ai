# B6 — Cloudflare Delivery Evidence

Status: **REMOTE DEPLOY PASS / BROWSER SMOKE PENDING**

## Deployment identity

- deployed code checkpoint: `8ca900ab0bf4164ba793a3adaeedbf9d47f5817e`
- predeploy CI: **#107 SUCCESS**
- deployment URL: `https://weld-inspection-ai.sjo1848.workers.dev`
- Cloudflare version ID: `da7a9f51-e932-4ba5-8e93-09925c82c6a5`
- published asset count: 10
- runtime: WASM-only
- R2: not used
- WebGPU: not used

## Promoted model identity

User/Codex remote verification reported:
- artifact: `weld-yolox-nano-v0.1.onnx`
- local + public bytes: `3,653,900`
- local + public SHA-256: `b5e980bf03113583a9a21600c3ee49a89daf2c76358fdcecf9c75db2bf7ee714`
- manifest and remote ONNX identity: PASS

No alternate model, re-export, threshold change, class change or frozen-test reuse occurred.

## Runtime asset identity

Predeploy CI #107 proved:
- ONNX Runtime Web version: 1.20.1
- entrypoint: `onnxruntime-web/wasm`
- runtime asset: `assets/ort-wasm-simd-threaded.wasm`
- bytes: `11,246,032`
- SHA-256: `207d02be4591c156b0a98f024f3d58005b5b04c92274d759fb390338c63559ea`
- companion: `assets/ort-wasm-simd-threaded.mjs`
- Cloudflare 25 MiB per-file gate: PASS
- assets-only Wrangler dry-run: PASS
- Chrome/WASM portability smoke: PASS

## Deployment architecture

v0.1 is intentionally simple:
- Cloudflare Workers Static Assets only;
- browser-side WASM inference;
- no R2;
- no custom Worker inference route;
- no WebGPU dependency;
- no server-side image processing;
- no image persistence.

## Outstanding B6 closure evidence

The deployment itself and HTTP model identity are proven by the deployment execution report.

B6 must **not** be marked TECHNICAL PASS until the public deployed origin also passes:
1. Chromium/Playwright application smoke;
2. runtime reports WASM and completes inference;
3. validation image input traverses the deployed production path;
4. zero-detection remains distinct from runtime failure;
5. image privacy recorder observes 0 non-read requests and 0 request bodies;
6. frozen test remains unused.

The reference image for this smoke must come from validation, not frozen test:
`20230612_102253_jpg.rf.4f90896f91209d67275f4a262585942e.jpg`.

## Claim boundary

Remote deployment does not alter model-quality evidence. B5 already retained the same validation reference as a concrete false-negative example. B7 independent phone/negative evidence remains mandatory.
