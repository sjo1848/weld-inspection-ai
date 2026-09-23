# WV-TC-B7-001 — MVP Independent Validation — ACTIVE

Project: WELD-VISION-001 — Weld Inspection AI — FALDEO  
Phase: BUILD / VALIDATE HANDOFF  
Authority: HG-WV-002 Option A + WV-TC-BUILD-001 + WV-EVAL-001  
Status: **ACTIVE / PARTIAL INPUT ACQUIRED / EXECUTION PENDING**

## 1. Purpose

Close the remaining MVP validation gap without changing the promoted model contract.

B7 combines the already-proven Layer A/B evidence with a bounded Layer C external sanity set. It is a product/domain-shift sanity check, not a statistical benchmark and not a new tuning set.

## 2. Frozen technical contract

Do not change during B7:

- promoted artifact: `weld-yolox-nano-v0.1.onnx`
- ONNX SHA-256: `b5e980bf03113583a9a21600c3ee49a89daf2c76358fdcecf9c75db2bf7ee714`
- runtime: WASM-only
- confidence threshold: `0.20`
- NMS threshold: `0.65`
- supported classes: `spatter`, `slag inclusion`
- diagnostic-only / not supported: `undercut`
- frozen test: CONSUMED — never rerun or tune against

## 3. Existing evidence carried into B7

### Layer A — software/runtime

Already proven:
- deployed Cloudflare application loads;
- capture/select → inference → result works;
- image remains local;
- runtime errors are distinct from zero detections;
- zero detections are not weld approval;
- exact model/runtime identity is inspectable;
- WASM browser inference and deployed privacy smoke PASS.

### Layer B — model evaluation

Already frozen and documented:
- source-aware train/val/test split;
- held-out class metrics;
- promoted supported-class set;
- undercut removed from supported v0.1 set;
- one concrete validation false-negative retained from B5/B6;
- no post-test retuning authorized.

B7 must not reopen Layer B calibration.

## 4. Layer C — independent sanity set

WV-EVAL-001 target: **6–12 independently captured phone photos if practical**.

Preferred mix:
- several weld photos with visually obvious supported anomalies when available;
- at least one image where no target anomaly is expected;
- at least one ambiguous, poor-lighting, severe-perspective or otherwise unsupported-condition image;
- images from the actual phone/user workflow.

Independent means the images are not from train, validation or frozen test and are not derivatives/screenshots of those dataset images.

If the complete 6–12 photo set is not available, record the smaller evidence set honestly and leave B7 PARTIAL rather than fabricating coverage.

## 5. Required capture record per image

For each independent image record:

- stable local evidence ID, not personal identity;
- capture/source provenance;
- device/browser when known;
- condition category: `supported-positive`, `negative/no-target`, `ambiguous`, `unsupported-condition`;
- expected visual condition based on human observation, without claiming certified weld truth;
- application result;
- detected supported classes and confidences;
- detection count;
- zero-result flag;
- runtime status;
- obvious false-positive / false-negative / uncertain observation;
- notes on lighting, distance, angle, blur or occlusion;
- confirmation that the image was not uploaded by the application.

Do not store unnecessary EXIF/location/personally identifying metadata.

## 6. Required negative/failure evidence

Final B7 report must include, when encountered:
- at least one hard negative or false-positive example;
- at least one missed/subtle defect or false-negative example;
- at least one unsupported-condition example.

The existing B5/B6 validation false negative may be referenced as prior evidence, but it does not replace the independent Layer C set.

If an independent false positive or false negative is not encountered in the bounded set, report that fact; do not manufacture one.

## 7. Execution rules

Run every independent image through the deployed v0.1 app:

`https://weld-inspection-ai.sjo1848.workers.dev`

For B7:
- no threshold changes;
- no NMS changes;
- no model/checkpoint changes;
- no class-set changes;
- no training;
- no re-export;
- no frozen-test access;
- no server-side inference;
- no user-image upload.

Observed failures become evidence and limitations, not tuning instructions for v0.1.

## 8. B7 outputs

Required durable outputs:
- `docs/evidence/B7_VALIDATION_REPORT.md`;
- a non-sensitive structured result manifest under `docs/evidence/artifacts/`;
- representative notes for independent cases;
- final supported-class statement;
- final known-limitations statement;
- presentation-ready claim wording.

Raw independent phone photos do not need to be committed to GitHub. Prefer local/private evidence retention with stable IDs or hashes when necessary.

## 9. Exit criteria

B7 may close only when:
- Layer A evidence remains valid;
- Layer B measured results are reported without alteration;
- independent Layer C evidence has actually been executed;
- domain-shift outcomes are documented;
- failure/negative evidence requirements are addressed honestly;
- supported classes remain evidence-bounded;
- product copy remains educational/non-certifying;
- no final-demo evidence has been used for tuning.

A smaller-than-target independent set may justify PARTIAL, not automatic PASS.

## 10. Post-B7 assurance

After B7 evidence is complete:
1. run Independent Critic over integrated MVP evidence;
2. run Integration Review over model/runtime/UI/deployment composition;
3. only then consider the vertical slice technically complete.

PR #1 remains draft/open until the required assurance and owner merge decision.

## 11. Current independent-input checkpoint

Owner-confirmed independent phone evidence is now available:
- 4 phone captures;
- 2 specimen groups;
- 3 correlated views grouped under one specimen;
- one oblique/perspective domain-shift case;
- no true negative/no-target case yet.

Canonical structured input manifest: `docs/evidence/artifacts/b7-independent-input-manifest.json`.

A derived crop and manual result screenshot are retained only as diagnostic evidence and do not count toward the independent-photo target. Structured deployed-app execution remains pending.
