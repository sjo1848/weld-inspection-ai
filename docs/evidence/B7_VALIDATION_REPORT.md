# B7 — MVP Independent Validation Report

Status: **PARTIAL INPUT ACQUIRED / EXECUTION PENDING**

## Frozen v0.1 identity

- deployment: `https://weld-inspection-ai.sjo1848.workers.dev`
- ONNX SHA-256: `b5e980bf03113583a9a21600c3ee49a89daf2c76358fdcecf9c75db2bf7ee714`
- runtime: WASM-only
- confidence: 0.20
- NMS: 0.65
- supported: spatter, slag inclusion
- diagnostic-only: undercut
- frozen test: consumed / not reusable

## Layer A

Status: PROVEN before B7 through B5/B6.

## Layer B

Status: FROZEN / DOCUMENTED before B7.

Do not alter metrics or tune from B7 observations.

## Layer C — independent phone sanity set

Target: 6–12 images if practical.

| Evidence ID | Category | Capture condition | Human visual expectation | App result | Detections | FP/FN/uncertain | Privacy | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B7-PH-001 | supported-positive | landscape phone view, specimen B7-SPEC-001 | many visible droplets consistent with spatter; non-certified expectation | pending structured run | pending | pending | pending | owner-captured, 2048×1536 |
| B7-PH-002 | supported-positive | near-frontal phone view, specimen B7-SPEC-002 | visible droplets consistent with spatter; slag inclusion not asserted | pending structured run | pending | pending | pending | owner-captured, 1536×2048 |
| B7-PH-003 | supported-positive | second near-frontal view, same B7-SPEC-002 | visible droplets consistent with spatter | pending structured run | pending | pending | pending | correlated view; not independent specimen |
| B7-PH-004 | unsupported-condition | oblique/perspective view, same B7-SPEC-002 | spatter-like droplets remain visible under stronger perspective | pending structured run | pending | pending | pending | domain-shift geometry case |

## Independent-input provenance

The project owner confirmed these four source photographs were captured by him and are not derived from train/validation/frozen-test imagery.

Current set:
- 4 independent phone captures;
- 2 specimen groups;
- 3 views belong to the same specimen and are grouped to avoid inflating evidence;
- no true negative/no-target phone case has been supplied yet;
- raw photos remain outside GitHub; only hashes/metadata are persisted.

Structured manifest: `docs/evidence/artifacts/b7-independent-input-manifest.json`.

Derived diagnostic evidence:
- `recort.jpg` is a crop and does not count as an independent capture;
- the supplied app screenshot does not count as an independent capture;
- on the cropped image, the manually observed app result was one `spatter` indication at 32%, with localization appearing materially displaced from the dominant visible spatter field. This is recorded as a diagnostic observation pending a reproducible structured run.

## Required failure/negative evidence

- hard negative / false positive: PENDING
- missed/subtle / false negative: PENDING
- unsupported condition: PENDING

Prior non-independent reference:
- B5/B6 validation reference is a known false negative and remains relevant as prior model-quality evidence, but it does not count toward the independent Layer C target.

## Domain-shift observations

Initial observation before structured execution: the supplied phone imagery already exposes a material scale/domain-shift concern. Large full-specimen views contain many visually apparent small droplets consistent with spatter, while the supplied cropped-run screenshot reports only one 32% spatter indication with questionable localization. This is evidence to investigate, not authorization to retune.

PENDING structured runs on B7-PH-001..004.

## Final supported-class statement

PENDING B7 execution. B7 cannot expand the class set; any contraction must be evidence-driven and treated as a product-scope decision.

## Known limitations

PENDING final synthesis. Existing known limitations remain in force:
- educational prototype only;
- no weld certification/acceptance;
- no NDT replacement;
- undercut unsupported in v0.1;
- canonical dataset has no true negative/background training examples;
- held-out performance is materially below validation;
- independent phone evidence is partially collected (4 captures / 2 specimen groups) but structured app execution and negative/no-target coverage remain incomplete.

## Presentation wording

Current approved wording:

“Prototype educational assistant for detecting selected visible surface anomalies in SMAW weld photographs.”

## B7 conclusion

PARTIAL INPUT ACQUIRED. Structured execution is pending; B7 remains open.
