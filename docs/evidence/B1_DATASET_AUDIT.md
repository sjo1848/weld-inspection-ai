# B1 — Dataset Audit and Split Evidence

Status: **PARTIAL — source acquisition unresolved; split defect confirmed**

## Canonical source

Mendeley Data: *Annotated Image Dataset for Shielded Metal Arc Welding (SMAW) Surface Defect Detection*

- Dataset ID: `f7j76vz53p`
- Version: `1`
- DOI: `10.17632/f7j76vz53p.1`
- Contributor: Mubessirul Ummah
- Published: 2026-08-19
- License: CC BY 4.0
- Public record: `https://data.mendeley.com/datasets/f7j76vz53p/1`

The canonical Mendeley description reports 71 original 3456×3456 smartphone photographs, three defect classes, resizing to 640×640, tiling, 448 processed samples and an 80:20 processed-image train/test split.

## Secondary independent conversion/audit evidence

The public dataset card `AI4Manufacturing/217` on Hugging Face documents a provenance-preserving conversion of this Mendeley deposit. It is secondary evidence, not a replacement canonical source.

Its audit reports:

- 448 distinct processed tile records;
- 717 deduplicated object annotations;
- `spatter`: 417 annotations;
- `undercut`: 162 annotations;
- `slag inclusion`: 138 annotations;
- every retained tile contains at least one target defect;
- the Roboflow category `weld-defect-det` is a super-category placeholder with no emitted annotations;
- the 71 original source photographs are not distributed in the deposit; source-photo identity was reconstructed from filenames;
- the authors' processed-image split has severe source-photo leakage: train contains tiles from 70 source photographs, test from 47, with **46 source photographs shared** between train and test;
- the secondary audit's corrected photograph-wise split uses 57 source photographs / 364 tiles for train and 14 source photographs / 84 tiles for test, with zero shared source photographs and all three classes represented in test.

This independently confirms the leakage risk already identified during Design. The original published split must not be treated as reliable held-out generalization evidence for this project.

## Negative/background coverage finding

Because all 448 retained tiles contain at least one target defect, the canonical dataset alone provides no true negative/background weld tiles for measuring defect-presence false positives.

Consequences for the MVP:

1. The detector may still be trained for localization/classification of the three supported defect classes.
2. “No supported anomaly detected” behavior cannot be validated credibly from this dataset alone.
3. B3/B7 must add legitimate negative/background weld photographs or use an independently captured phone-image sanity set containing negative/ambiguous cases.
4. No accuracy claim may silently imply validated defect absence detection.

## Source acquisition status

Repository tooling exists for acquisition, SHA-256 manifests and COCO audits. However, the previously used unauthenticated Mendeley endpoint

`https://data.mendeley.com/public-api/datasets/f7j76vz53p/files?folder_id=root&version=1`

returned HTTP **403** from GitHub Actions on 2026-09-15. This is classified as an external source/API acquisition issue, not a product failure and not a Human Gate.

The Hugging Face converted copy is useful for public audit metadata, but its file access is gated and therefore is not currently accepted as the project's reproducible raw-byte acquisition channel.

## Split policy

The project requires a source-photo-aware split:

1. Recover source photograph identity from filename metadata or an explicit mapping.
2. Assign complete source-photograph groups to train/validation/test before augmentation.
3. Apply augmentation only after group assignment and only to training data.
4. Verify zero source groups shared across partitions.
5. Persist a deterministic split manifest with source identity, tile identity and partition.
6. Preserve the original authors' assignment only as provenance metadata, not as the project's validation split.

The 57/14 photograph-wise split reported by the secondary audit is evidence that a zero-leak grouping is feasible, but this repository must reconstruct and verify its own manifest from acquired source bytes/metadata before promoting it as execution evidence.

## Existing repository tooling

```bash
python ml/scripts/download_dataset.py --list-only
python ml/scripts/download_dataset.py
python ml/scripts/audit_dataset.py <extracted-dataset-root>
```

The downloader validates HTTPS URLs and safe filenames and records SHA-256 integrity metadata. Raw bytes stay outside Git.

## B1 exit conditions still open

- obtain the canonical/traceable dataset bytes through a reproducible accessible channel;
- persist exact file names, sizes and SHA-256 hashes;
- inspect the actual COCO annotation layout;
- reproduce/determine exact class and annotation counts from the acquired bytes;
- reconstruct source-photo grouping from the acquired material;
- generate and verify a deterministic zero-leak train/validation/test manifest;
- document negative/background supplementation for downstream evaluation.

Until these items exist, B1 remains **PARTIAL** and no model-quality metric may be promoted as trustworthy held-out evidence.
