# B0 — Repository and Harness Bootstrap Evidence

Status: **IMPLEMENTED / EXECUTION CHECK PENDING**

## Implemented surfaces

- Build branch: `build/mvp-v0.1`.
- Draft integration surface: PR #1.
- `AGENTS.md` preserves active scope, authority precedence, architectural boundaries and forbidden actions.
- `docs/harness/ORCHESTRATION_STATE.md` preserves live execution continuity.
- `docs/harness/EVIDENCE_INDEX.md` maps lifecycle claims to durable evidence.
- Python package root at `ml/src/weldvision` with pytest/ruff configuration in `pyproject.toml`.
- Vue 3 + TypeScript + Vite shell at `apps/web` with ONNX Runtime Web declared as the browser inference runtime dependency.
- `.gitignore` prevents raw datasets, checkpoints, model binaries, secrets and generated outputs from being committed accidentally while leaving provenance manifests versionable.

## Reproducibility contract

Python:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
pytest
ruff check .
```

Web:

```bash
corepack enable
pnpm install
pnpm web:typecheck
pnpm web:build
```

Declared runtime ranges:

- Python `>=3.11,<3.13`
- Node `>=20,<23`
- package manager `pnpm@10.15.1`

## Evidence boundary

The repository structure and deterministic commands exist, but this ChatGPT connector runtime cannot execute package installation, Python tests, pnpm type-check/build, browser execution or network-backed dataset/model operations in the checked-out repository.

Therefore B0 is **not** declared TECHNICAL_PASS yet. The minimal remaining B0 proof is execution of the listed Python and web commands in a repository shell with package-network access. A failure there is an execution/harness issue to debug autonomously, not a Human Gate.

## Exit evidence required

- Python environment installs from `pyproject.toml`.
- `pytest` passes.
- `ruff check .` passes.
- `pnpm install` completes.
- `pnpm web:typecheck` passes.
- `pnpm web:build` produces the static web bundle.
- Exact execution HEAD is captured with the evidence.
