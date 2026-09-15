# B1 — Dataset Audit and Split Evidence

Status: **PARTIAL — canonical structure/leakage directly audited; test annotation + archive SHA still required**

## Canonical source

Mendeley Data: *Annotated Image Dataset for Shielded Metal Arc Welding (SMAW) Surface Defect Detection*

- Dataset ID: `f7j76vz53p`
- Version: `1`
- DOI: `10.17632/f7j76vz53p.1`
- Contributor: Mubessirul Ummah
- Published: 2026-08-19
- License: CC BY 4.0
- Public record: `https://data.mendeley.com/datasets/f7j76vz53p/1`

The deposit reports 71 original smartphone photographs, three target classes and 448 processed 640×640 tiles.

## Canonical local evidence received 2026-09-15

The project now has user-supplied evidence derived from the downloaded Mendeley archive:

- complete `unzip -l` archive listing;
- complete extracted-file listing;
- canonical `train/train_fold_1/_annotations.coco.json`;
- local confirmation that the original archive is retained outside Git because it is about 1.1 GB.

Input identities captured by the project audit:

- archive-listing SHA-256: `fe15a3c74dee65fcd0d4821e0b92c02a69ea00502ba82a7c4ad3cdd524fd3c9f`;
- extracted-file-list SHA-256: `35adfa39453b1c33c24c904261c8c4ab336b6a4f647e2dd58c34716d7ddfef2a`;
- `train_fold_1` COCO SHA-256: `bdb8abed1099631ead7a5bda65e0f617cd63540407ec8ed16ada35188c48530a`.

The `train_fold_1` JSON is byte-size matched to the archive listing at `1,416,530` bytes.

## Archive structure — directly audited

The archive listing contains:

- `18,001` entries;
- `1,157,926,436` uncompressed bytes;
- `17,990` image files;
- `11` COCO annotation JSON files;
- `90` test images;
- five train folds of `2,864` images each;
- five validation folds of `716` images each.

For every fold pair, train + validation therefore contains `3,580` augmented images.

## Augmentation lineage — directly audited

Filename lineage reconstruction shows that each fold pair contains exactly `358` base train tile lineages and exactly `10` variants per base tile:

- `orig`
- `Original`
- `Flip_H`
- `Flip_V`
- `Rotate_90_CW`
- `Rotate_90_CCW`
- `Rotate_180`
- `Grayscale`
- `Color_Jitter`
- `Blur`

This means augmentation occurred before/around the published cross-validation partition rather than being confined to the training side of a source-independent split.

## Source-photo leakage — now canonical, not merely secondary

Source-photo identity can be reconstructed from the filenames by removing the augmentation prefix and Roboflow `_jpg.rf.<hash>` suffix while retaining the camera basename.

Direct analysis of the canonical file listing yields:

- `71` source-photo identities total;
- `47` source-photo identities in published test;
- `70` source-photo identities on the published train side;
- `46 / 47` published test source photos also occur on train (`97.9%`).

Therefore the originally published test split is **not source-photo independent**.

The five train/validation fold pairs are also heavily leaked:

| Fold | Train source photos | Val source photos | Shared source photos | Shared base tile lineages |
| --- | ---: | ---: | ---: | ---: |
| 1 | 70 | 69 | 69 | 329 |
| 2 | 70 | 68 | 68 | 319 |
| 3 | 70 | 70 | 70 | 320 |
| 4 | 70 | 70 | 70 | 322 |
| 5 | 70 | 70 | 70 | 314 |

The original cross-validation metrics therefore cannot be treated as independent held-out evidence for this project.

## Canonical train-fold annotation audit

`train_fold_1/_annotations.coco.json` contains:

- `2,864` images;
- `4,545` object annotations;
- `0` images without an annotation;
- `slag inclusion`: `870`;
- `spatter`: `2,576`;
- `undercut`: `1,099`;
- category `0`, `weld-defect-det`, is an unused placeholder.

All `358` base train tile lineages occur in this fold. Across the observed augmented variants of each lineage, the category multiset is invariant.

Collapsing to one representative per base train tile yields:

- `358` base tiles;
- `568` object annotations;
- `slag inclusion`: `107`;
- `spatter`: `326`;
- `undercut`: `135`.

This directly confirms there are no true negative/background images in the audited train-fold annotation set.

## Secondary audit comparison

The earlier independent public derivative reported `448` unique processed tiles and `717` deduplicated annotations total, with no negative tiles. The direct canonical findings above agree with its lineage/leakage conclusions but no longer rely on that derivative for the source-photo overlap claim.

The project still requires the canonical test annotation JSON before promoting the exact full-dataset annotation totals as project-owned evidence.

## Required project split policy

The project will not use the authors' published split for trustworthy model evaluation.

The project split must:

1. reconstruct source-photo identity from filenames;
2. assign complete source-photo groups to train/validation/test before augmentation;
3. keep all derivatives of a base tile in the same partition;
4. apply/retain augmentation only on the training partition for model fitting;
5. verify zero source-photo and zero base-lineage overlap across partitions;
6. persist the deterministic split manifest;
7. reserve an independent negative/background phone sanity set for no-defect behavior.

## Machine-readable checkpoint

`data/manifests/b1-canonical-listing-audit.json` stores the direct structure, lineage, leakage and `train_fold_1` annotation findings above.

## B1 exit conditions still open

Only two small canonical inputs are now required from the retained local archive before the project can finish the data basis:

1. `test/_annotations.coco.json` — archive listing size `211,785` bytes;
2. SHA-256 of the original downloaded ZIP archive.

After those arrive, the project can:

- calculate exact 448-tile project-owned class/annotation totals;
- freeze the canonical archive identity;
- generate the source-photo-aware zero-leak split manifest;
- close B1 data integrity sufficiently to start bounded B3 training.

B3 remains blocked until those data-basis items are closed. This is a `HUMAN_ACTION`, not a new Human Gate.
