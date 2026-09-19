from weldvision.evaluation.promotion import (
    ClassMetrics,
    ThresholdResult,
    choose_operating_threshold,
    validate_frozen_manifest,
)


def test_choose_operating_threshold_prefers_macro_f1() -> None:
    results = [
        ThresholdResult(
            threshold=0.05,
            per_class={
                "spatter": ClassMetrics(precision=0.50, recall=0.90, ap50=0.70),
                "slag inclusion": ClassMetrics(precision=0.40, recall=0.80, ap50=0.60),
            },
        ),
        ThresholdResult(
            threshold=0.20,
            per_class={
                "spatter": ClassMetrics(precision=0.80, recall=0.70, ap50=0.72),
                "slag inclusion": ClassMetrics(precision=0.70, recall=0.65, ap50=0.62),
            },
        ),
    ]

    chosen = choose_operating_threshold(results, ("spatter", "slag inclusion"))

    assert chosen.threshold == 0.20


def test_choose_operating_threshold_tiebreaks_on_higher_threshold() -> None:
    metrics = {
        "spatter": ClassMetrics(precision=0.75, recall=0.75, ap50=0.7),
        "slag inclusion": ClassMetrics(precision=0.65, recall=0.65, ap50=0.6),
    }
    chosen = choose_operating_threshold(
        [
            ThresholdResult(threshold=0.10, per_class=metrics),
            ThresholdResult(threshold=0.20, per_class=metrics),
        ],
        ("spatter", "slag inclusion"),
    )

    assert chosen.threshold == 0.20


def test_frozen_manifest_rejects_wrong_checkpoint() -> None:
    manifest = {
        "stage": "B4_CANDIDATE_FROZEN",
        "frozen_test_used": False,
        "checkpoint_sha256": "expected",
        "supported_classes": ["spatter", "slag inclusion"],
        "confidence_threshold": 0.2,
        "nms_threshold": 0.65,
    }

    try:
        validate_frozen_manifest(manifest, expected_checkpoint_sha256="wrong")
    except ValueError as exc:
        assert "Checkpoint identity" in str(exc)
    else:
        raise AssertionError("Expected checkpoint mismatch to fail closed")


def test_frozen_manifest_accepts_valid_candidate() -> None:
    manifest = {
        "stage": "B4_CANDIDATE_FROZEN",
        "frozen_test_used": False,
        "checkpoint_sha256": "expected",
        "supported_classes": ["spatter", "slag inclusion"],
        "confidence_threshold": 0.2,
        "nms_threshold": 0.65,
    }

    validate_frozen_manifest(manifest, expected_checkpoint_sha256="expected")
