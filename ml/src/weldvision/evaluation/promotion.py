from __future__ import annotations

import hashlib
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ClassMetrics:
    precision: float
    recall: float
    ap50: float

    @property
    def f1(self) -> float:
        total = self.precision + self.recall
        if total <= 0:
            return 0.0
        return 2 * self.precision * self.recall / total


@dataclass(frozen=True)
class ThresholdResult:
    threshold: float
    per_class: Mapping[str, ClassMetrics]

    def macro_f1(self, promoted_classes: Iterable[str]) -> float:
        names = tuple(promoted_classes)
        if not names:
            raise ValueError("At least one promoted class is required")
        return sum(self.per_class[name].f1 for name in names) / len(names)

    def macro_precision(self, promoted_classes: Iterable[str]) -> float:
        names = tuple(promoted_classes)
        if not names:
            raise ValueError("At least one promoted class is required")
        return sum(self.per_class[name].precision for name in names) / len(names)


def choose_operating_threshold(
    results: Iterable[ThresholdResult],
    promoted_classes: Iterable[str],
) -> ThresholdResult:
    """Choose one validation-only confidence threshold deterministically.

    Primary objective: highest macro F1 across the promoted classes.
    Tie-breakers: higher macro precision, then higher confidence threshold.
    """

    promoted = tuple(promoted_classes)
    candidates = list(results)
    if not candidates:
        raise ValueError("No threshold candidates were provided")

    missing = [
        (candidate.threshold, name)
        for candidate in candidates
        for name in promoted
        if name not in candidate.per_class
    ]
    if missing:
        raise ValueError(f"Missing class metrics: {missing}")

    return max(
        candidates,
        key=lambda item: (
            item.macro_f1(promoted),
            item.macro_precision(promoted),
            item.threshold,
        ),
    )


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_frozen_manifest(
    manifest: Mapping[str, object],
    *,
    expected_checkpoint_sha256: str,
) -> None:
    """Fail closed before any frozen-test execution."""

    if manifest.get("stage") != "B4_CANDIDATE_FROZEN":
        raise ValueError("Manifest is not frozen for B4 test execution")
    if manifest.get("frozen_test_used") is not False:
        raise ValueError("Manifest does not prove the frozen test is still unused")
    if manifest.get("checkpoint_sha256") != expected_checkpoint_sha256:
        raise ValueError("Checkpoint identity does not match the frozen manifest")

    supported = manifest.get("supported_classes")
    if not isinstance(supported, list) or not supported:
        raise ValueError("At least one supported class is required")

    threshold = manifest.get("confidence_threshold")
    if not isinstance(threshold, (int, float)) or not 0 < float(threshold) < 1:
        raise ValueError("Invalid frozen confidence threshold")

    nms = manifest.get("nms_threshold")
    if not isinstance(nms, (int, float)) or not 0 < float(nms) < 1:
        raise ValueError("Invalid frozen NMS threshold")
