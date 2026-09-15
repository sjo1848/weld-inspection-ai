# B0 — Repository and Harness Bootstrap Evidence

Status: **TECHNICAL PASS**

## Candidate identity

- Build branch: `build/mvp-v0.1`
- Draft integration surface: PR #1
- Validated candidate commit: `1483bbb2a32b23b805da26a061f39643fdcbe203`
- GitHub Actions workflow run: `34924440930`
- Result: **SUCCESS**

## Executed evidence

The bounded B0 CI run executed the repository's actual bootstrap commands on Ubuntu and passed all required checks:

- Python 3.11 environment and editable package install: PASS
- pytest: **8 tests passed**
- Ruff: PASS
- Node 20 and pnpm 10.15.1 setup: PASS
- workspace dependency installation: PASS
- Vue/TypeScript type-check: PASS
- Vite production build: PASS

B0 is therefore closed as a technical implementation increment. Later commits may change `execution_head`; they do not erase this evidence. Any material bootstrap regression must be detected by CI on the new candidate.

## Implemented surfaces

- `AGENTS.md` preserves active scope, authority precedence, architecture boundaries and forbidden actions.
- `docs/harness/ORCHESTRATION_STATE.md` preserves execution continuity.
- `docs/harness/EVIDENCE_INDEX.md` maps lifecycle claims to durable evidence.
- Python package root at `ml/src/weldvision` with pytest/ruff configuration in `pyproject.toml`.
- Vue 3 + TypeScript + Vite shell at `apps/web` with ONNX Runtime Web as browser inference runtime.
- `.gitignore` excludes raw datasets, checkpoints, ONNX binaries, secrets and generated outputs while keeping provenance manifests versionable.

## Reproducibility contract

Python:

```bash
python -m pip install -e '.[dev]'
pytest
ruff check .
```

Web:

```bash
corepack enable
corepack prepare pnpm@10.15.1 --activate
pnpm install --no-frozen-lockfile
pnpm web:typecheck
pnpm web:build
```

## Boundary

The B0 PASS proves repository/bootstrap correctness only. It does not prove dataset validity, model quality, ONNX browser portability, deployment, or weld-defect detection quality.
