from typing import Literal

from pydantic import (
    BaseModel,
    Field,
)


class ValidationCandidateSource(BaseModel):
    source_id: str = Field(
        min_length=1,
    )

    source_title: str = Field(
        min_length=1,
    )

    provenance_reference: str = Field(
        min_length=1,
    )

    independent_publication_or_dataset: bool
    independent_experimental_campaign: bool

    not_firesense_training_source: bool
    not_reused_bass_ii_rows: bool

    experimental_data_only: bool

    measurement_quantity: str

    measurement_definition_matches: bool
    cross_calibration_available: bool

    normal_gravity_transport_equivalence_established: bool

    uncertainty_or_variability_metadata_preserved: bool

    digitization_uncertainty_separate: bool
    experimental_uncertainty_separate: bool
    model_uncertainty_separate: bool


class ValidationCandidateRecord(BaseModel):
    record_id: str = Field(
        min_length=1,
    )

    material: str = Field(
        min_length=1,
    )

    geometry_family: str = Field(
        min_length=1,
    )

    thickness_um: float = Field(
        gt=0,
    )

    oxygen_percent: float = Field(
        gt=0,
        le=100,
    )

    pressure_kpa: float = Field(
        gt=0,
    )

    gravity_regime: Literal[
        "microgravity",
        "normal_gravity",
    ]

    transport_configuration: str = Field(
        min_length=1,
    )

    flow_mm_s: float | None = Field(
        default=None,
        ge=0,
    )

    observed_spread_rate_mm_s: float = Field(
        gt=0,
    )

    digitization_uncertainty_mm_s: float | None = Field(
        default=None,
        ge=0,
    )

    experimental_uncertainty_mm_s: float | None = Field(
        default=None,
        ge=0,
    )

    training_eligible: bool = False

    validation_holdout: bool = True

    provenance_reference: str = Field(
        min_length=1,
    )


class ValidationCandidateRequest(BaseModel):
    dataset_id: str = Field(
        min_length=1,
    )

    dataset_version: str = Field(
        min_length=1,
    )

    source: ValidationCandidateSource

    records: list[
        ValidationCandidateRecord
    ] = Field(
        min_length=1,
    )


class ValidationGateCheck(BaseModel):
    check_id: str

    passed: bool

    detail: str


class ValidationEvaluationRecord(BaseModel):
    record_id: str

    gravity_regime: Literal[
        "microgravity",
        "normal_gravity",
    ]

    thickness_um: float

    observed_spread_rate_mm_s: float

    predicted_spread_rate_mm_s: float | None

    prediction_decision: Literal[
        "predict",
        "abstain",
    ]

    prediction_minus_observed_mm_s: float | None

    absolute_error_mm_s: float | None

    relative_error_vs_observed_percent: float | None

    abstention_reasons: list[str]


class ValidationMetrics(BaseModel):
    evaluated_point_count: int

    mae_mm_s: float

    rmse_mm_s: float

    mean_bias_mm_s: float

    mean_absolute_percentage_error_percent: float

    max_absolute_error_mm_s: float


class ValidationCandidateEvaluationResponse(BaseModel):
    dataset_id: str

    dataset_version: str

    source_id: str

    classification: Literal[
        "compatible_independent_validation_candidate",
        "independent_external_comparison_only",
        "insufficient_validation_scope",
        "non_independent_rejected",
        "outside_firesense_v0_domain",
    ]

    direct_validation_gate_passed: bool

    holdout_evaluation_completed: bool

    external_validation_claim_allowed: Literal[
        False
    ]

    production_ready_claim_allowed: Literal[
        False
    ]

    certification_claim_allowed: Literal[
        False
    ]

    performance_acceptance_status: Literal[
        "thresholds_not_yet_frozen",
        "not_applicable_gate_failed",
    ]

    submitted_point_count: int

    evaluated_point_count: int

    blocked_point_count: int

    gate_checks: list[
        ValidationGateCheck
    ]

    metrics_role: Literal[
        "validation_candidate_metrics",
        "comparison_only_metrics",
        "not_available",
    ]

    metrics: ValidationMetrics | None

    evaluations: list[
        ValidationEvaluationRecord
    ]

    guardrails: list[str]
