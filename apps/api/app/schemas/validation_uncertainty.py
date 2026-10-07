from typing import Literal

from pydantic import (
    BaseModel,
    Field,
)

from app.schemas.validation_candidate import (
    ValidationCandidateRequest,
)


class ValidationUncertaintyAssessmentRequest(
    BaseModel
):
    candidate: ValidationCandidateRequest

    experimental_uncertainty_kind: Literal[
        "standard_deviation",
        "standard_error",
        "confidence_interval_half_width",
        "range_half_width",
        "source_reported_unspecified",
        "not_available",
    ]

    experimental_uncertainty_confidence_level_percent: (
        float | None
    ) = Field(
        default=None,
        gt=0,
        le=100,
    )

    digitization_uncertainty_kind: Literal[
        "absolute_bound",
        "method_sensitivity_bound",
        "pixel_calibration_bound",
        "source_reported_unspecified",
        "not_available",
    ]


class ValidationUncertaintyRowDiagnostic(
    BaseModel
):
    record_id: str

    absolute_model_error_mm_s: (
        float | None
    )

    experimental_uncertainty_mm_s: (
        float | None
    )

    digitization_uncertainty_mm_s: (
        float | None
    )

    absolute_error_to_experimental_uncertainty_ratio: (
        float | None
    )

    absolute_error_to_digitization_uncertainty_ratio: (
        float | None
    )


class ValidationUncertaintyAssessmentResponse(
    BaseModel
):
    compatibility_gate_passed: bool

    evaluated_point_count: int

    rows_with_experimental_uncertainty: int

    rows_with_digitization_uncertainty: int

    experimental_uncertainty_completeness_fraction: float

    digitization_uncertainty_completeness_fraction: float

    uncertainty_categories_separate: bool

    calibrated_prediction_interval_available: bool

    uncertainty_readiness_status: Literal[
        "blocked_compatibility_gate",
        "blocked_incomplete_experimental_uncertainty",
        "blocked_experimental_uncertainty_semantics",
        "blocked_no_calibrated_prediction_interval",
    ]

    coverage_verification_passed: bool

    uncertainty_calibration_claim_allowed: bool

    external_validation_claim_allowed: bool

    production_ready_claim_allowed: bool

    certification_claim_allowed: bool

    diagnostics: list[
        ValidationUncertaintyRowDiagnostic
    ]

    guardrails: list[str]
