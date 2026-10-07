from typing import Any, Literal

from pydantic import (
    BaseModel,
    Field,
)

from app.schemas.validation_candidate import (
    ValidationCandidateEvaluationResponse,
)


class ValidationCsvImportRequest(BaseModel):
    dataset_id: str = Field(
        min_length=1,
    )

    dataset_version: str = Field(
        min_length=1,
    )

    source_id: str = Field(
        min_length=1,
    )

    source_title: str = Field(
        min_length=1,
    )

    provenance_reference: str = Field(
        min_length=1,
    )

    csv_text: str = Field(
        min_length=1,
        max_length=2_000_000,
    )

    experimental_data_only: bool

    measurement_quantity: str = (
        "flame_spread_rate"
    )

    measurement_definition_matches: bool

    cross_calibration_available: bool = False

    normal_gravity_transport_equivalence_established: bool = False

    uncertainty_or_variability_metadata_preserved: bool

    digitization_uncertainty_separate: bool = True

    experimental_uncertainty_separate: bool = True

    model_uncertainty_separate: bool = True


class ValidationCsvImportResponse(BaseModel):
    dataset_id: str
    dataset_version: str
    source_id: str

    imported_row_count: int

    import_status: Literal[
        "provenance_review_required",
        "rejected_non_independent_source",
        "comparison_only_source",
        "evaluated_direct_validation_candidate",
    ]

    source_known: bool

    source_independence_status: str

    registry_direct_validation_eligible: bool

    validation_evaluation: (
        ValidationCandidateEvaluationResponse
        | None
    )

    performance_evaluation: (
        dict[str, Any]
        | None
    )

    external_validation_claim_allowed: Literal[
        False
    ]

    production_ready_claim_allowed: Literal[
        False
    ]

    certification_claim_allowed: Literal[
        False
    ]

    guardrails: list[str]
