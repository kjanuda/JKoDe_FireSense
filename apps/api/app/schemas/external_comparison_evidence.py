from typing import Literal

from pydantic import BaseModel


class ExternalComparisonRecord(BaseModel):
    gravity_context: Literal[
        "microgravity",
        "normal_gravity",
    ]

    external_record_id: str

    thickness_um: float

    firesense_v0_rate_mm_s: float
    ries_2024_rate_mm_s: float

    external_minus_model_mm_s: float
    relative_gap_vs_model_percent: float
    relative_gap_vs_external_percent: float

    comparison_status: str

    direct_validation_eligible: Literal[False]


class ExternalComparisonEvidenceResponse(BaseModel):
    evidence_id: str
    evidence_version: Literal["v0"]

    source_name: str
    source_doi: str
    figure_ref: Literal["4"]

    scientific_role: Literal[
        "independent_external_comparison_only"
    ]

    independent_external_source: Literal[True]

    numeric_external_comparison_available: Literal[True]

    independent_external_validation_available: Literal[False]

    direct_external_validation_ready: Literal[False]

    training_eligible_count: Literal[0]

    independent_validation_eligible_count: Literal[0]

    comparison_count: int

    measurement_definition_classification: str

    measurement_definition_exact_match: Literal[False]

    flow_condition_match: Literal[False]

    flow_correction_allowed: Literal[False]

    exact_independent_validation_source_found: Literal[False]

    release_validation_status: str
    release_comparison_status: str

    blocking_reasons: list[str]

    artifact_sha256: dict[str, str]

    artifact_sha256_verified: Literal[True]

    guardrails: list[str]

    comparisons: list[
        ExternalComparisonRecord
    ]
