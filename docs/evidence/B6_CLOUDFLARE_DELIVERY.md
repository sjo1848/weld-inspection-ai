# B6 — Cloudflare Delivery Evidence

Status: **TECHNICAL PASS**

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

## Deployed-origin browser smoke

- browser smoke: **PASS**, Playwright `1 passed`;
- runtime: `WASM`;
- inference: completed through the deployed production path;
- reference partition: validation;
- reference image: `20230612_102253_jpg.rf.4f90896f91209d67275f4a262585942e.jpg`;
- detection count: `0`;
- zero result: `true`;
- runtime error: absent;
- privacy request count: `9`;
- non-read request count: `0`;
- request bodies count: `0`;
- frozen test used: `false`;
- evidence JSON: `docs/evidence/artifacts/b6-deployed-smoke.json`;
- screenshot: retained locally at `/tmp/b6-deployed-smoke.png`.

The zero-detection result is retained as a known validation false-negative and was not used to retune thresholds, classes or the model.

The public smoke observed only read requests for the application, manifest, promoted ONNX and ORT WASM assets; the selected image remained local through a `blob:` URL.

## Claim boundary

Remote deployment does not alter model-quality evidence. B5 and B6 retain the same validation reference as a concrete false-negative example. B7 independent phone/negative evidence remains mandatory.
