# WV-TC-B6-001 — Cloudflare Delivery — ACTIVE

Project: WELD-VISION-001 — Weld Inspection AI — FALDEO  
Phase: BUILD  
Authority: HG-WV-002 Option A + WV-TC-BUILD-001  
Status: B6 ACTIVE / REMOTE DEPLOY PASS / BROWSER SMOKE PENDING

## 1. Purpose

Deploy the B5 browser application on Cloudflare without changing the client-side inference boundary or the promoted model contract.

## 2. Proven entry state

- B5: TECHNICAL PASS
- promoted ONNX: `weld-yolox-nano-v0.1.onnx`
- ONNX SHA-256: `b5e980bf03113583a9a21600c3ee49a89daf2c76358fdcecf9c75db2bf7ee714`
- B5 already completed real-image inference through ONNX Runtime Web/WASM
- frozen test remains consumed
- thresholds/classes/checkpoint remain frozen

## 3. v0.1 delivery decision

For v0.1, the browser runtime is **WASM-only**.

The prior WebGPU-capable bundle emitted an asyncify/JSEP-oriented WASM asset larger than Cloudflare Workers Static Assets' 25 MiB individual-file limit. The project owner approved simplifying v0.1 to the standard ONNX Runtime Web WASM execution provider.

Consequences:
- import `onnxruntime-web`, not `onnxruntime-web/webgpu`;
- execution provider is `wasm`;
- no WebGPU attempt/fallback path in v0.1;
- no R2 bucket;
- no Worker R2 route;
- no external CDN runtime dependency;
- HTML/JS/CSS/manifest/ONNX/ORT WASM all deploy as Cloudflare Static Assets.

WebGPU remains a post-v0.1 optimization candidate only after measured mobile latency justifies reintroducing it.

## 4. Cloudflare delivery

Use an assets-only Cloudflare Worker deployment:
- `assets.directory = ./dist`;
- SPA fallback enabled;
- no Worker script is required;
- no R2 binding is required.

The build gate must fail if any generated asset exceeds 25 MiB.

## 5. Required B6 evidence

Before remote deployment:
- TypeScript/tests/build PASS;
- B2 browser WASM portability regression PASS;
- production build records exact generated static asset sizes/hashes;
- largest generated file is <=25 MiB;
- Wrangler assets-only deployment dry-run PASS.

Remote B6 closure additionally requires:
- exact promoted ONNX staged and SHA-verified;
- successful Workers Static Assets deployment;
- real workers.dev URL;
- remote manifest/ONNX/WASM GET PASS;
- remote ONNX SHA verification;
- browser smoke through deployed origin;
- one validation-image analysis through deployed origin;
- proof that user image remains local.

## 6. Forbidden actions

- no server-side inference;
- no image upload/persistence;
- no R2 dependency in v0.1;
- no threshold/class/checkpoint modification;
- no frozen-test reuse;
- no substitution of the promoted ONNX;
- no certification/pass-fail claim.

## 7. Stop condition

Repository/CI preparation proceeds autonomously.

Remote Cloudflare login and providing the exact promoted ONNX file on the deployment machine remain Human Actions when required.

## 8. Remote deployment checkpoint

- deployed checkpoint: `8ca900ab0bf4164ba793a3adaeedbf9d47f5817e`
- predeploy CI: #107 SUCCESS
- workers.dev URL: `https://weld-inspection-ai.sjo1848.workers.dev`
- Cloudflare version ID: `da7a9f51-e932-4ba5-8e93-09925c82c6a5`
- assets published: 10
- promoted ONNX remote identity: PASS, 3,653,900 bytes, SHA-256 `b5e980bf03113583a9a21600c3ee49a89daf2c76358fdcecf9c75db2bf7ee714`
- runtime: WASM-only; R2/WebGPU not used
- final closure item: deployed Chromium/inference/privacy smoke
