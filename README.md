# Weld Inspection AI

Educational computer-vision prototype for detecting selected visible surface anomalies in SMAW weld photographs.

## Status

Current phase: **BUILD** (`WELD-VISION-001`). The active bounded delivery contract is `WV-TC-BUILD-001` under the FALDEO Project Method v1.0.

This project is an educational assistant. It does **not** certify, accept or reject welds and it is not an industrial NDT replacement.

## MVP architecture

```text
phone/browser photo
      ↓
input validation + preprocessing
      ↓
ONNX Runtime Web
  ├─ WebAssembly compatibility baseline
  └─ WebGPU optional acceleration
      ↓
model adapter + postprocessing
      ↓
localized potential anomaly detections
      ↓
educational result UI
```

The image stays on the user's device during the core inference path. Cloudflare is used only to deliver static application/model/config assets. Python is the authoritative environment for dataset preparation, transfer learning, evaluation, ONNX export and parity checks.

## Initial target classes

- spatter
- undercut
- visible slag inclusion

The supported demo class set may be reduced if validation evidence shows a class is materially unreliable.

## Repository layout

```text
apps/web/          Vue/TypeScript browser client
ml/src/weldvision/ Python ML/data tooling
docs/harness/      execution continuity and evidence index
AGENTS.md           FALDEO execution boundaries
```

## Environment bootstrap

Python:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
pytest
ruff check .
```

Web workspace:

```bash
pnpm install
pnpm web:typecheck
pnpm web:build
```

The web source is introduced later in the risk-first Build sequence; until then only the workspace/runtime dependency contract is present.

## Build sequence

`B0 bootstrap → B1 dataset audit/split → B2 browser portability spike → B3 transfer learning → B4 model promotion/parity → B5 thin client → B6 Cloudflare delivery → B7 validation`

## Dataset provenance

The current design candidate is the CC BY 4.0 *Annotated Image Dataset for Shielded Metal Arc Welding (SMAW) Surface Defect Detection*, DOI `10.17632/f7j76vz53p.1`. Build must audit provenance and split integrity before using metrics as evidence.

## Claims boundary

A zero-detection result means only that no supported target anomaly exceeded the configured threshold. It must never be interpreted as “weld approved”, “defect-free” or “safe”.
