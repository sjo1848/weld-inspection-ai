# WV-TC-B5-001 — Thin Client Vertical Slice — COMPLETE

Project: WELD-VISION-001 — Weld Inspection AI — FALDEO  
Phase: BUILD  
Authority: HG-WV-002 Option A + WV-TC-BUILD-001  
Status: B5 COMPLETE / TECHNICAL PASS / B4 TECHNICAL PASS / NO NEW HUMAN GATE

## 1. Purpose

Implement the smallest integrated mobile-first browser client that consumes the promoted B4 model contract and proves the end-to-end user journey without changing model semantics.

## 2. Frozen model/runtime inputs

- model: `weld-yolox-nano-v0.1.onnx`
- ONNX SHA-256: `b5e980bf03113583a9a21600c3ee49a89daf2c76358fdcecf9c75db2bf7ee714`
- artifact bytes: `3,653,900`
- input: `images` float32 NCHW `[1,3,416,416]`
- output: `output` float32 `[1,3549,8]`
- raw model output: decode is NOT embedded in ONNX
- supported classes: `spatter`, `slag inclusion`
- diagnostic-only / not user-supported: `undercut`
- confidence threshold: `0.20`
- NMS threshold: `0.65`
- manifest: `model-manifest.v0.1.json`
- B4 frozen test: CONSUMED; must not be reused for tuning

## 3. P0 journey

1. User selects or captures a weld image.
2. App validates the selected file and renders a local preview.
3. Browser preprocesses the image deterministically to the promoted 416×416 model tensor.
4. ONNX Runtime Web executes inference locally.
5. Model adapter decodes raw YOLOX output.
6. Adapter applies confidence threshold, supported-class filtering and NMS.
7. Coordinates are mapped back to the original preview.
8. UI overlays localized potential anomalies.
9. UI presents educational result text and limitations.
10. User may retry or start a new analysis.

## 4. Required semantics

- A zero-detection result means only: no supported anomaly was detected above the configured threshold.
- Zero detections must never be rendered as weld approval, acceptance, safety or certification.
- Runtime/model/preprocessing failures must be visibly distinct from zero detections.
- Unsupported/diagnostic-only `undercut` output must not be presented as a supported result.
- User image must remain local in the core analysis path.
- Model/runtime version must be visible or inspectable in the result/debug surface.

## 5. Technical boundaries

- Vue 3 + TypeScript + Vite.
- ONNX Runtime Web.
- WASM is the required correctness baseline.
- WebGPU may be attempted as an optimization only with graceful WASM fallback.
- No server-side inference.
- No image upload/persistence.
- No auth/database/payments/multi-tenancy.
- UI/domain layer must not depend directly on raw tensor layout; model adapter owns model-specific decoding.

## 6. Required implementation units

### B5.1 — Manifest/model integration
- ingest/promote final B4 manifest into the web build;
- load exact model artifact;
- verify runtime tensor names/shapes against manifest;
- expose model/version/runtime state.

### B5.2 — Preprocessing
- deterministic image decode;
- preserve original width/height;
- resize/letterbox exactly to model input;
- produce float32 NCHW tensor;
- preserve transform metadata required for coordinate reversal.

### B5.3 — YOLOX adapter
- decode raw `[1,3549,8]`;
- combine objectness/class confidence according to YOLOX contract;
- filter to supported classes only;
- apply confidence 0.20;
- apply class-aware or contract-consistent NMS 0.65;
- map boxes back to original image coordinates;
- return stable domain detections independent of raw tensor format.

### B5.4 — UI journey
- select/capture;
- preview;
- processing state;
- overlay boxes;
- result list/counts;
- educational explanations;
- no-detection state;
- runtime/model error state;
- retry/new analysis.

### B5.5 — Evidence
- unit tests for preprocessing transforms;
- unit tests for decode/threshold/NMS/class filtering;
- tests for coordinate reversal;
- UI test for successful detection path;
- UI test for zero-detection path;
- UI test for runtime failure path;
- network/privacy evidence that user image is not uploaded;
- reference-path evidence on at least one known image before deployment.

## 7. Forbidden actions

- no threshold retuning;
- no class-set expansion;
- no checkpoint/model replacement;
- no rerunning the frozen test for UI development;
- no certification/pass/fail language;
- no hidden server inference fallback;
- no silent conversion of runtime errors into a no-detection result.

## 8. Exit criteria

B5 is TECHNICAL PASS only if:
- promoted ONNX loads through the production adapter path;
- one real image can traverse select → preprocess → inference → decode/NMS → overlay/result;
- zero detections and failures have distinct semantics;
- supported-class filtering is proven;
- image-coordinate reversal is correct;
- core image path remains local;
- automated tests are green;
- manual/reference-path evidence is recorded.

## 9. Next step after B5

B6 Cloudflare delivery. The known ORT WASM ~26.8 MB single-file issue must be resolved there without changing the client-side inference boundary.

## 10. Closure evidence

- validated implementation commit: `fe79d5cbf7d0756b098a015f7c40eda3e263326b`
- CI #85: SUCCESS
- real validation-image production path: PASS
- runtime: WASM fallback after unavailable WebGPU
- privacy: 0 non-read requests / 0 request bodies
- frozen test used: false
- integrated reference result: 0 detections on a validation image selected because it contains at least one supported-class ground-truth annotation; retained as a false-negative example and not used for tuning
- durable evidence: `docs/evidence/B5_THIN_CLIENT.md` and Drive `WELD-VISION-001/B5`

B5 is closed as **TECHNICAL PASS**. Model-quality limitations remain active and move forward to B7; they are not repaired by post-test tuning.
