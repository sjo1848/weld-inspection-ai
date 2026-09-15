# Engineering Evidence Index — WELD-VISION-001

This file indexes durable evidence. It is not a second source of truth for project governance.

| Dimension | Coverage | Canonical evidence |
| --- | --- | --- |
| Problem | PROVEN | `WV-REQ-001 — MVP Requirements Baseline v0.1` in project Drive |
| Design | PROVEN | `WV-ARCH-001`, `WV-ADR-001`, `WV-ML-001`, `WV-RTC-001`, `WV-WF-001`, and `WV-DR-001` in project Drive |
| Implementation | PARTIAL | B0 technical PASS at `1483bbb2...` / CI `34924440930`; B1/B2 active on `build/mvp-v0.1` |
| Validation | PARTIAL | `WV-EVAL-001`; B0 execution proven, model/runtime validation still incomplete |
| Release / Deployment | UNKNOWN | No Cloudflare deployment evidence yet |
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
- Node/pnpm dependency install: PASS
- Vue/TypeScript type-check: PASS
- Vite production build: PASS

## Required Build evidence still outstanding

- B1: canonical dataset byte identity, annotation audit, source-photo mapping, leakage-safe split manifest and negative/background supplementation plan.
- B2: official YOLOX-Nano reference ONNX SHA-256 plus successful ORT Web/WASM real-browser inference and actual output tensor contract.
- B3: bounded training configuration, checkpoint identity, measured validation metrics and failure examples.
- B4: promoted ONNX identity/hash, manifest, Python → ONNX parity evidence and browser runtime evidence for the task model.
- B5: local-inference privacy evidence plus unit/UI/reference-path evidence.
- B6: Cloudflare deployment identity and smoke-test evidence.
- B7: final validation report, supported class set and known limitations.

## Dataset validity finding

Public secondary provenance/audit evidence for the selected Mendeley dataset confirms that the original processed-image split is not independent at source-photo level and that all 448 retained tiles contain a defect. Therefore neither the original test split nor this dataset alone is accepted as evidence of generalization or negative/no-defect behavior.

## Claim boundary

The project may claim only an educational computer-vision prototype for selected visible SMAW surface anomalies. No evidence in this index supports certified inspection, weld acceptance, AWS/ISO/ASME compliance, industrial-grade reliability or detection of all welding defects.
