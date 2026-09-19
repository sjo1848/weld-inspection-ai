# B5 — Thin Client Integrated Evidence

Status: **TECHNICAL PASS WITH EXPLICIT MODEL LIMITATION**

Validated implementation commit: `fe79d5cbf7d0756b098a015f7c40eda3e263326b`  
GitHub Actions: CI #85 — SUCCESS  
Promoted model SHA-256: `b5e980bf03113583a9a21600c3ee49a89daf2c76358fdcecf9c75db2bf7ee714`

## Integrated production-path proof

The B5 reference runner executed the actual browser application path:

`file input → local preview → deterministic preprocessing → ONNX Runtime Web → WASM → YOLOX decode → confidence/class filtering → NMS → UI result`.

Reference evidence:
- partition: `validation`
- frozen test used: **false**
- image: `20230612_102253_jpg.rf.4f90896f91209d67275f4a262585942e.jpg`
- runtime: WASM
- confidence threshold: 0.20
- model version: 0.1.0
- execution status: PASS
- screenshot: Drive `B5/b5-reference-path.png`
- JSON evidence: Drive `B5/b5-reference-path.json`
- summary: Drive `B5/b5-reference-summary.json`

The runner selects its reference image only from validation images carrying at least one annotation belonging to the supported class set (`spatter` or `slag inclusion`). The integrated model returned zero supported detections on the selected reference image.

This is therefore retained as a **reference-path false-negative example**, not as a runtime failure and not as evidence of weld acceptance.

No model threshold, checkpoint or class-set change is authorized from this observation.

## Privacy proof

The Playwright network recorder observed:
- total browser requests: 8
- non-read requests: 0
- requests carrying bodies: 0
- selected image transport: local `blob:` URL
- no POST / PUT / PATCH request occurred during the core analysis path

The user image remained local during inference.

## Runtime behavior

The headless Chromium environment did not expose a usable WebGPU adapter. The application:
1. attempted WebGPU;
2. surfaced the initialization warning;
3. fell back to WASM;
4. completed inference successfully.

This is the required graceful-fallback behavior.

## B5 contract evidence

Proven:
- exact promoted manifest/model integrity path;
- deterministic top-left YOLOX letterbox preprocessing;
- BGR float32 NCHW tensor creation;
- raw YOLOX decode for strides 8/16/32;
- confidence threshold 0.20;
- supported-class filtering;
- diagnostic-only `undercut` exclusion;
- class-aware NMS 0.65;
- coordinate reversal;
- select/capture + preview;
- processing state;
- detection and zero-result UI paths;
- runtime/model error path;
- retry/new-analysis;
- local-image privacy boundary;
- real-image browser/WASM execution;
- B2 browser portability regression remains green.

## Interpretation boundary

B5 proves software/runtime integration. It does **not** prove that every supported anomaly will be detected.

The zero-detection result on a validation image known to contain a supported-class annotation is consistent with the model's measured false-negative behavior from B4. It strengthens, rather than weakens, the requirement for B7 independent phone-image and negative/background validation.

## Closure

B5 exit criteria are satisfied because the exact promoted model loads through the production adapter path, a real validation image traverses the entire client pipeline, zero-detection and failure semantics are distinct, local privacy is evidenced, model-specific filtering and coordinate logic are tested, and CI is green.

B5 is closed as **TECHNICAL PASS**.

Next increment: B6 Cloudflare delivery.
