# WELD-VISION-001 — Execution Contract

This repository implements the bounded Thursday MVP defined by the FALDEO Project Method v1.0.

## Authority and source precedence
1. Latest approved Human Gate / active Task Contract in the project Drive.
2. Current Authoritative Project State in the project Drive.
3. Approved requirements and ADRs.
4. Specialized evidence/design artifacts.
5. Repository implementation evidence.
6. Conversation history is context only, never sole authority.

## Active scope
- Educational assistant for visible SMAW surface anomalies.
- Target labels: spatter, undercut, visible slag inclusion; final supported set may contract based on evidence.
- Browser-side inference with ONNX Runtime Web.
- WebAssembly compatibility baseline; WebGPU optional optimization.
- Python owns dataset, training, evaluation, export and parity tooling.
- Cloudflare serves static application/model/config assets.

## Non-goals / forbidden changes
- No certified inspection or weld pass/fail claims.
- No server-side image inference for the MVP.
- No Workers AI dependency for the core detector.
- No paid infrastructure or paid model/API calls.
- No auth, database, payments or multi-tenancy.
- No training from scratch.

## Current Build sequence
B0 bootstrap -> B1 dataset audit/split -> B2 ONNX browser portability spike -> B3 transfer learning -> B4 model promotion/parity -> B5 thin client -> B6 Cloudflare delivery -> B7 validation.

## Working rules
- Work on short-lived branches; do not commit directly to main after bootstrap.
- Prefer local/deterministic evidence before CI/provider runs.
- Do not fabricate PASS. UNKNOWN remains UNKNOWN until evidence exists.
- Zero detections means only: no supported target anomaly exceeded the configured threshold.
- Model-specific tensors must stay behind an adapter boundary.
- Any new model artifact is versioned and immutable once promoted.
- Human Gate only for material scope/risk/cost/architecture decisions defined by the active contract.
