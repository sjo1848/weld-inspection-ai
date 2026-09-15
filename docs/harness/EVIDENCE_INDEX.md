# Engineering Evidence Index — WELD-VISION-001

This file indexes durable evidence. It is not a second source of truth for project governance.

| Dimension | Coverage | Canonical evidence |
| --- | --- | --- |
| Problem | PROVEN | `WV-REQ-001 — MVP Requirements Baseline v0.1` in project Drive |
| Design | PROVEN | `WV-ARCH-001`, `WV-ADR-001`, `WV-ML-001`, `WV-RTC-001`, `WV-WF-001`, and `WV-DR-001` in project Drive |
| Implementation | PARTIAL | Build branch `build/mvp-v0.1`; `docs/evidence/B0_BOOTSTRAP.md`; B1 acquisition/audit tooling; B2 browser portability probe prepared |
| Validation | PARTIAL | `WV-EVAL-001 — MVP Acceptance & Model Evaluation Plan v0.1`; execution evidence not yet produced |
| Release / Deployment | UNKNOWN | No Cloudflare deployment evidence yet |
| Maintenance / Operations | NOT_APPLICABLE | MVP phase; evolution path only |
| Judgment / Material Decisions | PROVEN | Approved Definition and DESIGN → BUILD Human Gate in project Drive; static B0/B1 critic review PASS for continuation |

## Current Build evidence surfaces
- `docs/evidence/B0_BOOTSTRAP.md` — bootstrap structure and explicit execution-proof boundary.
- `docs/evidence/B1_DATASET_AUDIT.md` — dataset provenance, license, lineage/leakage analysis and remaining file-level evidence.
- `docs/evidence/B2_PORTABILITY_SPIKE.md` — official YOLOX-Nano reference-graph portability contract and execution recipe.
- `apps/web/portability.html` + `apps/web/src/portability.ts` — development-only graph execution probe.
- `ml/scripts/download_dataset.py` + `ml/scripts/audit_dataset.py` — reproducible B1 acquisition/audit tooling.

## Required Build evidence still outstanding
- B0 executed dependency install, Python tests/lint, web typecheck/build and execution HEAD.
- B1 dataset file hashes, class/instance counts, annotation schema, negative/background coverage, source grouping, split manifest and leakage statement.
- B2 actual YOLOX-Nano ONNX portability result through ONNX Runtime Web/WASM; WebGPU result where supported.
- B3 bounded training configuration, checkpoint identity, measured validation metrics and failure examples.
- B4 ONNX model identity/hash, manifest, Python → ONNX parity evidence and promoted browser runtime evidence.
- B5 local-inference privacy evidence plus unit/UI/reference-path evidence.
- B6 Cloudflare deployment identity and smoke-test evidence.
- B7 final validation report, supported class set and known limitations.

## Claim boundary
The project may claim only an educational computer-vision prototype for selected visible SMAW surface anomalies. No evidence in this index supports certified inspection, weld acceptance, AWS/ISO/ASME compliance, industrial-grade reliability or detection of all welding defects.
