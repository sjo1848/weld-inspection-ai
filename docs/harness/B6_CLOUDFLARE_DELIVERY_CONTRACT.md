# WV-TC-B6-001 — Cloudflare Delivery — ACTIVE

Project: WELD-VISION-001 — Weld Inspection AI — FALDEO  
Phase: BUILD  
Authority: HG-WV-002 Option A + WV-TC-BUILD-001  
Status: B6 ACTIVE / B5 TECHNICAL PASS / NO NEW HUMAN GATE

## 1. Purpose

Deploy the B5 browser application on Cloudflare without changing the client-side inference boundary or the promoted model contract.

## 2. Proven entry state

- B5 implementation commit: `fe79d5cbf7d0756b098a015f7c40eda3e263326b`
- CI #85: SUCCESS
- B5 real-image reference path: PASS
- B5 privacy evidence: 0 non-read requests / 0 request bodies
- promoted ONNX: `weld-yolox-nano-v0.1.onnx`
- ONNX SHA-256: `b5e980bf03113583a9a21600c3ee49a89daf2c76358fdcecf9c75db2bf7ee714`
- frozen test remains consumed; B6 must not alter model thresholds/classes/checkpoint

## 3. Delivery constraint

Cloudflare Workers Static Assets currently limits an individual static asset to 25 MiB.

The Vite/ORT WebGPU build emits an ONNX Runtime Web WASM binary at approximately 26.8 MB. That file cannot be uploaded as a normal Worker Static Asset.

## 4. Approved B6 seam

Use one Cloudflare Worker with:
- Static Assets for HTML/JS/CSS/model/manifest and all files <=25 MiB;
- one private R2 Standard bucket bound as `RUNTIME_BUCKET`;
- the oversized generated ORT WASM object stored in R2 under the same URL path/key used by the generated JS bundle;
- selective `assets.run_worker_first` for `/assets/*.wasm`;
- Worker code that reads that key from R2 and streams it back as `application/wasm`;
- fallback to `env.ASSETS.fetch(request)` for any WASM path not present in R2.

This keeps the browser request same-origin and avoids a public-bucket/CORS dependency.

## 5. Cost boundary

R2 Standard is the only storage class authorized for this seam.

The runtime object is far below the current 10 GB-month free storage allocation. The MVP must stay inside free-tier operational usage; no paid optimization or external inference service is authorized.

## 6. Build/deploy mechanics

Cloudflare build preparation must:
1. stage the exact promoted ONNX after SHA verification;
2. run the production Vite build;
3. identify generated WASM assets larger than 25 MiB;
4. move those files out of `dist` into a deployment staging directory while preserving their relative URL key;
5. emit a machine-readable runtime-asset manifest with path, bytes and SHA-256;
6. assert that no file remaining in `dist` exceeds 25 MiB;
7. upload the staged WASM object(s) to the bound R2 bucket;
8. deploy the Worker + remaining Static Assets.

## 7. Required evidence

B6 can close only with:
- deterministic delivery-preparation test;
- Worker route unit test;
- exact oversized runtime asset bytes/SHA/key recorded;
- no >25 MiB object remaining in Static Assets payload;
- successful R2 object upload identity;
- successful Worker deployment URL/identity;
- deployed GET of app, manifest, ONNX and R2-backed WASM;
- browser smoke test through the deployed origin;
- one real-image deployed analysis with explicit WASM fallback allowed;
- proof that user image remains local after deployment.

## 8. Forbidden actions

- no server-side model inference;
- no image upload to Worker/R2;
- no model/threshold/class changes;
- no frozen-test reuse;
- no public write route to R2;
- no deployment that silently omits the exact promoted ONNX;
- no claim that deployment quality resolves B7 model-quality limitations.

## 9. Stop condition

Repository preparation and local/CI verification proceed autonomously.

External Cloudflare authentication, initial R2 subscription activation if absent, bucket creation, or account-bound deployment credentials are Human Actions when the runtime cannot perform them directly.
