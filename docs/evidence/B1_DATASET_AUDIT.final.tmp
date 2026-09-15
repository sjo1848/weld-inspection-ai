# B1 — Dataset Audit and Split Evidence

Status: **TECHNICAL PASS — canonical data basis audited and project split frozen**

## Canonical source

Mendeley Data: *Annotated Image Dataset for Shielded Metal Arc Welding (SMAW) Surface Defect Detection*

- Dataset ID: `f7j76vz53p`
- Version: `1`
- DOI: `10.17632/f7j76vz53p.1`
- Contributor: Mubessirul Ummah
- Published: 2026-08-19
- License: CC BY 4.0
- Archive: `Annotated-Image-Dataset-for-Shielded-Metal-Arc-Wel.zip`
- Archive SHA-256: `6f600d8d3f8aa7bbada0f3092a7712680ca8b1c02153ecb761cf3a22d2215868`

The raw archive remains outside Git. The archive hash pins the exact retained source bytes.

## Direct canonical evidence

The retained archive listing establishes:

- `18,001` archive entries;
- `1,157,926,436` uncompressed bytes;
- `17,990` image files;
- `11` COCO JSON files;
- `90` published test images;
- five train folds of `2,864` images each;
- five validation folds of `716` images each.

The three annotation inputs used to reconstruct the base pool are pinned as:

| Input | Bytes | SHA-256 | Images | Boxes |
| --- | ---: | --- | ---: | ---: |
| `train/train_fold_1/_annotations.coco.json` | 1,416,530 | `bdb8abed1099631ead7a5bda65e0f617cd63540407ec8ed16ada35188c48530a` | 2,864 | 4,545 |
| `val/val_fold_1/_annotations.coco.json` | 353,810 | `c9fb2544e60ead164da2070c946179345fb8f074c4dfca69e49574d13dc4e454` | 716 | 1,135 |
| `test/_annotations.coco.json` | 211,785 | `da25b8fc35d9c087da0871e01c857dc948996ee1506f6cc1d683d42423dfe0aa` | 90 | 149 |

All images are 640×640 in these COCO files. Target categories are `slag inclusion`, `spatter`, and `undercut`; category `0` (`weld-defect-det`) is a placeholder with no target annotations.

## Pre-generated augmentation lineage

Combining `train_fold_1` + `val_fold_1` gives exactly `3,580` images, which resolve to:

- `358` base tile lineages;
- exactly `10` variants per lineage:
  `orig`, `Original`, `Flip_H`, `Flip_V`, `Rotate_90_CW`, `Rotate_90_CCW`, `Rotate_180`, `Grayscale`, `Color_Jitter`, `Blur`.

For the project base pool, only the `orig_` representative is retained from each of these 358 lineages. All other pre-generated augmentation variants are excluded from project validation/test and are not needed for the frozen split.

## Exact canonical base-pool counts

Collapsing the 3,580 augmented fold-pair records to the 358 `orig_` base tiles and adding the 90 published test tiles yields exactly:

- **448 base tiles**
- **717 object annotations**
- `slag inclusion`: **138**
- `spatter`: **417**
- `undercut`: **162**
- **0 true negative/background tiles**

The published test COCO alone contains:

- 90 images;
- 149 boxes;
- `slag inclusion`: 31;
- `spatter`: 91;
- `undercut`: 27;
- 0 background images.

This reproduces the earlier secondary audit totals directly from canonical material.

## Published split leakage — directly confirmed

Source-photo identity is reconstructed from the camera basename after stripping augmentation prefixes and the Roboflow `_jpg.rf.<hash>` suffix.

The canonical material contains **71 source-photo identities**.

Published split:

- published train side: 70 source photos;
- published test: 47 source photos;
- shared: **46**;
- overlap: **46 / 47 = 97.9%** of published test source photos.

The original train/validation folds also split augmented derivatives and source photos across both sides. Therefore neither the published test split nor the supplied cross-validation folds are accepted as independent generalization evidence for this project.

## Frozen WELD-VISION-001 split

The project pools the 448 base tiles, groups them by source photograph, and freezes a source-photo-aware **80/10/10** split.

Policy:

1. source-photo groups are indivisible;
2. no source photo may appear in more than one partition;
3. no pre-generated augmentation is used in validation or test;
4. training augmentation may be applied only after the split;
5. the assignment is frozen in `data/manifests/b1-source-split-manifest.json`.

Result:

| Project split | Source photos | Base tiles | Boxes | Slag inclusion | Spatter | Undercut |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Train | 57 | 358 | 575 | 110 | 335 | 130 |
| Validation | 7 | 45 | 71 | 14 | 41 | 16 |
| Test | 7 | 45 | 71 | 14 | 41 | 16 |

Source-photo overlap across train/validation/test: **0**.

The frozen manifest contains the source assignments, canonical input identities, reconstruction rule, class balance and downstream negative/background requirement.

## Negative/background limitation

All 448 canonical base tiles contain at least one target defect. Therefore this dataset can support localization/classification training of the three selected visible anomaly classes, but it cannot by itself validate the semantic claim that a new image contains no supported anomaly.

Downstream requirement:

- B7 must include an independent phone-image sanity set containing clean/ambiguous/background weld scenes.
- For the Thursday MVP, target approximately 6–12 such images if available.
- The independent sanity set must not be used to tune the final test result.
- Until that evidence exists, “no supported anomaly detected” remains a bounded runtime outcome, not a validated weld-absence claim.

This limitation does **not** block B3 transfer learning.

## B1 exit verdict

B1 is **TECHNICAL PASS** because:

- canonical archive identity is pinned by SHA-256;
- canonical structure and COCO layout are audited;
- exact base-tile/class counts are reproduced;
- source-photo leakage is directly verified;
- source-photo grouping is reconstructed;
- a deterministic project split is frozen with zero source overlap;
- negative/background limitations and the required validation supplementation are explicit.

Raw image bytes remain local and intentionally outside Git.

## Next authorized action

Proceed to B3:

1. materialize the 448-base-tile project split from the local archive;
2. create COCO train/validation/test subsets from the frozen manifest;
3. fine-tune **YOLOX-Nano only** as the first bounded candidate;
4. evaluate on project validation data;
5. record checkpoint/config/metrics/failure examples;
6. do not inspect/tune against the frozen project test set until promotion evaluation.

B1 does not authorize any certified weld-quality claim.
