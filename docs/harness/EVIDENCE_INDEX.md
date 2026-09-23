# Engineering Evidence Index — WELD-VISION-001

This file indexes durable evidence. It is not a second source of truth for project governance.

| Dimension | Coverage | Canonical evidence |
| --- | --- | --- |
| Problem | PROVEN | `WV-REQ-001 — MVP Requirements Baseline v0.1` in project Drive |
| Design | PROVEN | `WV-ARCH-001`, `WV-ADR-001`, `WV-ML-001`, `WV-RTC-001`, `WV-WF-001`, and `WV-DR-001` in project Drive |
| Implementation | PARTIAL | B0/B1/B2 technical PASS; B3 training complete; B4/B5/B6 TECHNICAL PASS; B7 validation outstanding |
| Validation | PARTIAL | source-aware split, frozen-test metrics, promoted ONNX identity/parity and B5 real-image integrated path proven; independent phone/mobile validation outstanding |
| Release / Deployment | PROVEN | WASM-only assets-only deployment live on workers.dev; remote manifest/ONNX/WASM identity PASS; deployed browser/inference/privacy smoke PASS |
| Maintenance / Operations | NOT_APPLICABLE | MVP phase; evolution path only |
| Judgment / Material Decisions | PROVEN | Approved Definition and DESIGN → BUILD Human Gate in project Drive |

## Proven Build evidence

### B0 — repository/bootstrap
- validated commit: `1483bbb2a32b23b805da26a061f39643fdcbe203`
- GitHub Actions run: `34924440930`
- result: SUCCESS
- Python editable install: PASS
- pytest: 8 PASS
- Ruff: PASS
- Node/pnpm install: PASS
- Vue/TypeScript type-check: PASS
- Vite production build: PASS

### B1 — canonical dataset basis and project split
- canonical archive SHA-256: `6f600d8d3f8aa7bbada0f3092a7712680ca8b1c02153ecb761cf3a22d2215868`
- archive: 18,001 entries / 1,157,926,436 uncompressed bytes
- canonical base pool: 71 source photos / 448 tiles / 717 boxes
- classes: slag inclusion 138 / spatter 417 / undercut 162
- canonical negative/background tiles: 0
- published test leakage: 46 of 47 test source photos also occur in train
- frozen project split:
  - train: 57 sources / 358 tiles / 575 boxes
  - validation: 7 sources / 45 tiles / 71 boxes
  - test: 7 sources / 45 tiles / 71 boxes
- validation class counts: 14 / 41 / 16
- test class counts: 14 / 41 / 16
- source overlap across project partitions: 0
- manifest: `data/manifests/b1-source-split-manifest.json`
- negative/background independent phone sanity evidence remains a B7 requirement, not a B3 blocker

### B2 — reference ONNX browser portability
- validated candidate: `988ccb5458de6a94c1ab960a4bb839063c8c5fdd`
- GitHub Actions run: `34927649777`
- official YOLOX-Nano ONNX size: `3,659,407` bytes
- SHA-256: `c789161ed43c8269fcd4e67c67eeeb4e80c622da2eb296a20bc6007bd18a0b7d`
- forced provider: WASM
- input: `images`, float32 `[1,3,416,416]`
- output: `output`, float32 `[1,3549,85]`
- CI smoke inference: 309.3 ms
- Playwright: 1/1 PASS

This proves reference-family browser portability, not welding task-model quality or mobile latency.

### B3 — transfer-learning candidate
- training: 80/80 epochs on Tesla T4
- promoted checkpoint candidate: `best_ckpt.pth`
- checkpoint SHA-256: `7e5cd8915262a0f912de33a04262e7fab7b984badf70cf2f92f1a38fbac7fb8b`
- persistent logs/checkpoints/evidence package: Drive `WELD-VISION-001/B3`
- validation identified `spatter` and `slag inclusion` as promotion candidates
- `undercut` remains diagnostic-only / not promoted

### B4.1/B4.2 — calibration and frozen held-out evaluation
- B4.1 candidate manifest SHA-256: `a78d393a623708b59594a2df5bc6073e7c830fe36db8ab0332e811da054c64fb`
- frozen confidence threshold: `0.20`
- frozen NMS threshold: `0.65`
- frozen test: 45 images / 71 boxes / 7 source photos
- frozen test status: **CONSUMED — do not rerun/tune**
- held-out slag inclusion: P 0.5294 / R 0.6429 / F1 0.5806 / AP50 0.5227
- held-out spatter: P 0.7576 / R 0.6098 / F1 0.6757 / AP50 0.5476
- diagnostic undercut: P 0.4211 / R 0.5000 / F1 0.4571 / AP50 0.3148
- promoted classes remain `spatter` + `slag inclusion`
- durable evidence: `docs/evidence/B4_MODEL_PROMOTION.md` plus Drive `B4` JSON artifacts
- image-level FP/FN examples were not persisted by the one-shot runner; B7 independent phone/demo evidence must close that gap without rerunning the frozen test

### B4.3 — promoted ONNX artifact and browser parity
- status: **TECHNICAL PASS**
- tooling commit: `2853fe53335cd4ffcc769610145198fd4dfa6943`
- ONNX artifact: `weld-yolox-nano-v0.1.onnx`
- ONNX size: `3,653,900` bytes
- ONNX SHA-256: `b5e980bf03113583a9a21600c3ee49a89daf2c76358fdcecf9c75db2bf7ee714`
- opset: 11
- input: `images` float32 `[1,3,416,416]`
- output: `output` float32 `[1,3549,8]`
- raw output decode in model: false
- Python PyTorch → ONNX Runtime parity: PASS on `zero`, `fill114`, `ramp251`; max abs diff <= `9.18e-5`
- ONNX Runtime Web/WASM parity: PASS on the same three deterministic patterns
- Playwright promoted-model browser test: 1/1 PASS
- final manifest: `model-manifest.v0.1.json`
- final supported classes: `spatter`, `slag inclusion`
- diagnostic-only: `undercut`
- confidence/NMS remain frozen at 0.20 / 0.65
- frozen test remains consumed and must not be rerun/tuned

### B5 — thin client integrated reference path
- status: **TECHNICAL PASS**
- validated implementation commit: `fe79d5cbf7d0756b098a015f7c40eda3e263326b`
- CI #85: SUCCESS
- reference image partition: validation
- frozen test used: false
- production path: Vue → preprocessing → ORT Web/WASM → YOLOX adapter → result UI
- runtime: WASM after graceful WebGPU failure
- network privacy: 8 total GET/blob reads, 0 non-read requests, 0 request bodies
- selected image remained local through a `blob:` URL
- integrated result: 0 detections on a validation image chosen from the supported-class GT set; retained as an explicit false-negative example, not used for tuning
- durable evidence: `docs/evidence/B5_THIN_CLIENT.md` and Drive `WELD-VISION-001/B5`

### B6 — Cloudflare deployment
- status: **TECHNICAL PASS**
- deployed checkpoint: `8ca900ab0bf4164ba793a3adaeedbf9d47f5817e`
- predeploy CI #107: SUCCESS
- workers.dev: `https://weld-inspection-ai.sjo1848.workers.dev`
- Cloudflare version ID: `da7a9f51-e932-4ba5-8e93-09925c82c6a5`
- assets: 10
- runtime: WASM-only / ORT Web 1.20.1
- R2/WebGPU: not used
- standard WASM: 11,246,032 bytes / SHA-256 `207d02be4591c156b0a98f024f3d58005b5b04c92274d759fb390338c63559ea`
- Cloudflare 25 MiB static-asset gate: PASS
- assets-only Wrangler dry-run: PASS
- remote manifest and promoted ONNX identity: PASS
- remote ONNX: 3,653,900 bytes / SHA-256 `b5e980bf03113583a9a21600c3ee49a89daf2c76358fdcecf9c75db2bf7ee714`
- deployed Chromium/inference/privacy smoke: **PASS**
- reference partition: validation
- reference image: `20230612_102253_jpg.rf.4f90896f91209d67275f4a262585942e.jpg`
- runtime: WASM
- detection count: 0; zero result: true; runtime error: absent
- privacy: 9 total requests, 0 non-read requests, 0 request bodies
- frozen test used: false
- durable smoke evidence: `docs/evidence/artifacts/b6-deployed-smoke.json`
- durable deployment evidence: `docs/evidence/B6_CLOUDFLARE_DELIVERY.md`

## Delivery constraint evidence — resolved

The earlier WebGPU/JSEP-oriented runtime exceeded the Static Assets per-file ceiling. v0.1 now uses the standard ONNX Runtime Web 1.20.1 WASM-only entrypoint. The deployed WASM is 11,246,032 bytes and passes the asset-size gate; no R2/CDN seam is required.

## Required Build evidence still outstanding

- B7: execute `WV-TC-B7-001` with genuinely independent phone/domain evidence, then finalize validation report, supported-class statement and known limitations.
- Independent Critic / Integration Review as required by the active FALDEO contract before overall technical completion.

## Claim boundary

The project may claim only an educational computer-vision prototype for selected visible SMAW surface anomalies. No evidence in this index supports certified inspection, weld acceptance, AWS/ISO/ASME compliance, industrial-grade reliability or detection of all welding defects.
