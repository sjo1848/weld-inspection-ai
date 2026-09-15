# B1 — Dataset Audit and Split Evidence

Status: **PARTIAL — source-level file audit pending download**

## Canonical source

Mendeley Data: *Annotated Image Dataset for Shielded Metal Arc Welding (SMAW) Surface Defect Detection*

- Dataset ID: `f7j76vz53p`
- Version: `1`
- DOI: `10.17632/f7j76vz53p.1`
- Contributor: Mubessirul Ummah
- Published: 2026-08-19
- License: CC BY 4.0
- Public record: `https://data.mendeley.com/datasets/f7j76vz53p/1`

## Publisher-reported structure

The Mendeley record reports:

- 71 original high-resolution source images (`3456×3456`).
- Smartphone capture at fixed distance/orientation and controlled lighting.
- Three surface-anomaly classes: `spatter`, `slag inclusion`, `undercut`.
- Polygon/bounding-box annotations produced through Roboflow and reviewed from source images by a certified welding inspector.
- Source images were resized to `640×640` and tiled, producing 448 processed samples with COCO-format annotations.
- Publisher split: 358 train / 90 test processed images.
- The training subset was augmented to 3,580 samples and later used for five-fold cross-validation.

## Provenance cross-check

A public Roboflow Universe project by the same contributor, `preprocessing-skripsi-dataset-weld-defect`, reports 71 images, the same three classes, object-detection task type, and CC BY 4.0 licensing:

`https://universe.roboflow.com/mubessirul-ummah/preprocessing-skripsi-dataset-weld-defect`

This is useful provenance evidence, but it is **not independent validation** of the Mendeley dataset. The overlapping contributor, class set and 71-image count are consistent with common lineage.

## Material validity risk: source-image leakage

The 448 processed samples are derived from only 71 original images through resizing/tiling. A random tile-level train/test split can place visually adjacent crops from the same source specimen in both partitions, making measured generalization materially optimistic.

Therefore the project does **not** accept the publisher's 80:20 processed-image split as sufficient evidence until file-level provenance is audited.

Required split policy:

1. Reconstruct original source/specimen identity from filenames or an explicit mapping when available.
2. Group train/validation/test by original source before augmentation.
3. Apply augmentation only to training data after the group split.
4. If grouping cannot be reconstructed, label internal metrics as potentially optimistic and supplement them with independently captured phone images.

## Negative/background coverage

Publisher metadata does not establish how many processed images contain no target annotations. This is a required B1 audit item because a detector evaluated only on positive defect crops can have poorly measured false-positive behavior.

The repository's `audit_dataset.py` reports the number of COCO images with zero annotations once the source archive is downloaded.

## Reproducible acquisition/audit path

```bash
python -m pip install -e '.[dev]'
python ml/scripts/download_dataset.py --list-only
python ml/scripts/download_dataset.py
# extract source archives while preserving the raw download manifest
python ml/scripts/audit_dataset.py <extracted-dataset-root>
```

Raw files are intentionally excluded from Git. Download integrity metadata is written to `data/manifests/mendeley-download.json` and is intended to be versioned after execution.

## B1 exit conditions still open

- exact root file names/sizes/hashes from the Mendeley public API;
- exact COCO annotation file layout;
- annotation instance count per class;
- number of background/negative images;
- filename/source-image grouping feasibility;
- durable group-aware split manifest;
- explicit leakage statement based on downloaded files.

Until those items exist, B1 remains **PARTIAL** and no model-quality metric may be promoted as reliable evidence.
