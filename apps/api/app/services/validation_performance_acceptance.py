import hashlib
import json
from pathlib import Path
from typing import Any

from app.schemas.validation_candidate import (
    ValidationCandidateEvaluationResponse,
)


class ValidationPerformanceError(
    RuntimeError
):
    pass


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[4]
)


PROTOCOL_PATH = (
    PROJECT_ROOT
    / "data/manifests/"
      "independent_validation_"
      "performance_acceptance_v0.json"
)


EXPECTED_PROTOCOL_SHA256 = (
    "bde2263ea33687d21c4dbbd0f98e567f20ba4c2809697304f11476b5dae37573"
)


def _sha256(
    path: Path,
) -> str:
    digest = hashlib.sha256()

    with path.open(
        "rb",
    ) as handle:
        for chunk in iter(
            lambda: handle.read(
                1024 * 1024
            ),
            b"",
        ):
            digest.update(
                chunk
            )

    return digest.hexdigest()


def _load_protocol() -> dict[str, Any]:
    if not PROTOCOL_PATH.exists():
        raise ValidationPerformanceError(
            "Performance acceptance protocol "
            "is missing."
        )

    actual = _sha256(
        PROTOCOL_PATH
    )

    if (
        actual
        != EXPECTED_PROTOCOL_SHA256
    ):
        raise ValidationPerformanceError(
            "Performance acceptance protocol "
            "integrity verification failed."
        )

    try:
        return json.loads(
            PROTOCOL_PATH.read_text(
                encoding="utf-8",
            )
        )
    except Exception as exc:
        raise ValidationPerformanceError(
            "Could not parse performance "
            "acceptance protocol."
        ) from exc


def evaluate_performance_acceptance(
    evaluation: ValidationCandidateEvaluationResponse,
) -> dict[str, Any]:

    protocol = _load_protocol()

    if (
        evaluation.direct_validation_gate_passed
        is not True
    ):
        return {
            "performance_gate_passed": False,
            "status": (
                "compatibility_gate_failed"
            ),
            "protocol_sha256": (
                EXPECTED_PROTOCOL_SHA256
            ),
            "checks": [],
            "scientific_review_required": True,
            "external_validation_claim_allowed": False,
            "production_ready_claim_allowed": False,
            "certification_claim_allowed": False,
        }

    if evaluation.metrics is None:
        raise ValidationPerformanceError(
            "Compatible validation candidate "
            "has no performance metrics."
        )

    thresholds = protocol[
        "required_thresholds"
    ]

    metrics = evaluation.metrics

    coverage = (
        evaluation.evaluated_point_count
        / evaluation.submitted_point_count
    )

    checks = [
        {
            "metric": "mae_mm_s",
            "value": metrics.mae_mm_s,
            "operator": "<=",
            "threshold": thresholds[
                "mae_mm_s_max"
            ],
            "passed": (
                metrics.mae_mm_s
                <= thresholds[
                    "mae_mm_s_max"
                ]
            ),
        },
        {
            "metric": "rmse_mm_s",
            "value": metrics.rmse_mm_s,
            "operator": "<=",
            "threshold": thresholds[
                "rmse_mm_s_max"
            ],
            "passed": (
                metrics.rmse_mm_s
                <= thresholds[
                    "rmse_mm_s_max"
                ]
            ),
        },
        {
            "metric": "absolute_mean_bias_mm_s",
            "value": abs(
                metrics.mean_bias_mm_s
            ),
            "operator": "<=",
            "threshold": thresholds[
                "absolute_mean_bias_mm_s_max"
            ],
            "passed": (
                abs(
                    metrics.mean_bias_mm_s
                )
                <= thresholds[
                    "absolute_mean_bias_mm_s_max"
                ]
            ),
        },
        {
            "metric": "mape_percent",
            "value": (
                metrics
                .mean_absolute_percentage_error_percent
            ),
            "operator": "<=",
            "threshold": thresholds[
                "mape_percent_max"
            ],
            "passed": (
                metrics
                .mean_absolute_percentage_error_percent
                <= thresholds[
                    "mape_percent_max"
                ]
            ),
        },
        {
            "metric": "max_absolute_error_mm_s",
            "value": (
                metrics.max_absolute_error_mm_s
            ),
            "operator": "<=",
            "threshold": thresholds[
                "max_absolute_error_mm_s_max"
            ],
            "passed": (
                metrics.max_absolute_error_mm_s
                <= thresholds[
                    "max_absolute_error_mm_s_max"
                ]
            ),
        },
        {
            "metric": "prediction_coverage_fraction",
            "value": coverage,
            "operator": ">=",
            "threshold": thresholds[
                "prediction_coverage_fraction_min"
            ],
            "passed": (
                coverage
                >= thresholds[
                    "prediction_coverage_fraction_min"
                ]
            ),
        },
    ]

    gate_passed = all(
        check[
            "passed"
        ]
        for check in checks
    )

    return {
        "performance_gate_passed": (
            gate_passed
        ),
        "status": (
            "performance_thresholds_passed"
            if gate_passed
            else "performance_thresholds_failed"
        ),
        "protocol_id": protocol[
            "protocol_id"
        ],
        "protocol_sha256": (
            EXPECTED_PROTOCOL_SHA256
        ),
        "checks": checks,
        "scientific_review_required": True,

        # Human/source review is still required.
        "external_validation_claim_allowed": False,

        "production_ready_claim_allowed": False,
        "certification_claim_allowed": False,
    }
