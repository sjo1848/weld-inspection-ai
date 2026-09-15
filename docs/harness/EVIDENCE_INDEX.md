# Engineering Evidence Index — WELD-VISION-001

This file indexes durable evidence. It is not a second source of truth for project governance.

| Dimension | Coverage | Canonical evidence |
| --- | --- | --- |
| Problem | PROVEN | `WV-REQ-001 — MVP Requirements Baseline v0.1` in project Drive |
| Design | PROVEN | `WV-ARCH-001`, `WV-ADR-001`, `WV-ML-001`, `WV-RTC-001`, `WV-WF-001`, and `WV-DR-001` in project Drive |
| Implementation | PARTIAL | B0 technical PASS; B2 reference ONNX browser/WASM technical PASS; B1 data basis incomplete |
| Validation | PARTIAL | B0 CI and B2 real-browser runtime evidence proven; task-model/data validation incomplete |
| Release / Deployment | UNKNOWN | No Cloudflare deployment evidence; ORT WASM static-asset size constraint identified |
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

### B2 — reference ONNX browser portability
- validated candidate: `988ccb5458de6a94c1ab960a4bb839063c8c5fdd`
- GitHub Actions run: `34927649777`
- B2 job: `104249134650`
- official YOLOX-Nano ONNX size: `3,659,407` bytes
- SHA-256: `c789161ed43c8269fcd4e67c67eeeb4e80c622da2eb296a20bc6007bd18a0b7d`
- Chrome: `152.0.7977.82`
- forced provider: `wasm`
- input: `images`, float32 `[1,3,416,416]`
- output: `output`, float32 `[1,3549,85]`
- CI smoke inference: 309.3 ms
- Playwright: 1/1 PASS

This proves reference-family browser portability, not welding task-model quality or mobile latency.

## Dataset validity evidence

The selected Mendeley source remains CC BY 4.0 and reports 71 source photographs / 448 processed defect tiles. Secondary public audit evidence confirms:

- 717 deduplicated annotations: spatter 417, undercut 162, slag inclusion 138;
- 46 of the authors' 47 test source photographs also occur in train;
- all 448 retained tiles contain at least one target defect;
- a source-photo-wise zero-overlap split is feasible, but the project has not yet reproduced its own split from acquired canonical bytes.

B1 therefore remains PARTIAL and blocks trustworthy task-specific training/evaluation.

## Delivery constraint evidence

The B2 production build emitted an ONNX Runtime Web WASM file at approximately 26.8 MB. Current Cloudflare Workers Static Assets impose a 25 MiB per-file limit. B6 must resolve this through an evidence-backed smaller ORT build or the pre-approved R2/CDN asset seam while preserving client-side inference.

## Required Build evidence still outstanding

- B1: canonical dataset byte identity, local annotation audit, source-photo mapping, leakage-safe split manifest, and negative/background supplementation.
- B3: bounded training configuration, checkpoint identity, measured validation metrics and failure examples.
- B4: promoted task-model ONNX identity/hash, manifest, Python → ONNX parity and browser runtime evidence.
- B5: local-inference privacy evidence plus unit/UI/reference-path evidence.
- B6: resolved runtime/model asset delivery, Cloudflare deployment identity and smoke test.
- B7: final validation report, supported class set and known limitations.
- Independent Critic / Integration Review as required by the active FALDEO contract before overall technical completion.

## Claim boundary

The project may claim only an educational computer-vision prototype for selected visible SMAW surface anomalies. No evidence in this index supports certified inspection, weld acceptance, AWS/ISO/ASME compliance, industrial-grade reliability or detection of all welding defects.
