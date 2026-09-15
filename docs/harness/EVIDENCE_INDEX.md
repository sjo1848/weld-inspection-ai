# Engineering Evidence Index — WELD-VISION-001

This file indexes durable evidence. It is not a second source of truth for project governance.

| Dimension | Coverage | Canonical evidence |
| --- | --- | --- |
| Problem | PROVEN | `WV-REQ-001 — MVP Requirements Baseline v0.1` in project Drive |
| Design | PROVEN | `WV-ARCH-001`, `WV-ADR-001`, `WV-ML-001`, `WV-RTC-001`, `WV-WF-001`, and `WV-DR-001` in project Drive |
| Implementation | PARTIAL | Build branch `build/mvp-v0.1`; B0 bootstrap artifacts in this repository |
| Validation | PARTIAL | `WV-EVAL-001 — MVP Acceptance & Model Evaluation Plan v0.1`; execution evidence not yet produced |
| Release / Deployment | UNKNOWN | No Cloudflare deployment evidence yet |
| Maintenance / Operations | NOT_APPLICABLE | MVP phase; evolution path only |
| Judgment / Material Decisions | PROVEN | Approved Definition and DESIGN → BUILD Human Gate in project Drive |

## Required Build evidence still outstanding
- B1 dataset audit, class/instance counts, annotation schema, split manifest and leakage statement.
- B2 YOLOX-Nano ONNX portability result through ONNX Runtime Web/WASM.
- B3 bounded training configuration, checkpoint identity, measured validation metrics and failure examples.
- B4 ONNX model identity/hash, manifest, Python → ONNX parity evidence and browser runtime evidence.
- B5 local-inference privacy evidence plus unit/UI/reference-path evidence.
- B6 Cloudflare deployment identity and smoke-test evidence.
- B7 final validation report, supported class set and known limitations.

## Claim boundary
The project may claim only an educational computer-vision prototype for selected visible SMAW surface anomalies. No evidence in this index supports certified inspection, weld acceptance, AWS/ISO/ASME compliance, industrial-grade reliability or detection of all welding defects.
