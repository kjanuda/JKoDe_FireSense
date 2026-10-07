from typing import Literal

from pydantic import BaseModel


class ValidationTarget(BaseModel):
    material: str
    geometry_family: str
    thickness_um: float
    oxygen_percent: float
    pressure_kpa: float
    microgravity_configuration: str
    microgravity_flow_mm_s: float
    independent_campaign_required: bool


class MinimumValidationScope(BaseModel):
    independent_source_count: int
    minimum_independent_numeric_points: int
    note: str


class ValidationReadinessResponse(BaseModel):
    readiness_id: str
    version: Literal["v0"]

    validation_protocol_id: str

    scientific_status: Literal[
        "independent_external_validation_not_yet_available"
    ]

    independent_external_validation_available: Literal[False]

    independent_external_comparison_available: Literal[True]

    exact_source_found: Literal[False]

    exact_validation_source_count: Literal[0]

    screened_candidate_count: int

    independent_comparison_source_count: int

    target: ValidationTarget

    minimum_validation_scope: MinimumValidationScope

    ries_2024_classification: str

    ries_2024_direct_validation_eligible: Literal[False]

    ries_2024_blocking_reasons: list[str]

    production_ready_claim_allowed: Literal[False]

    certification_claim_allowed: Literal[False]

    acceptance_criteria_sha256: str
    source_screening_sha256: str

    artifact_sha256_verified: Literal[True]

    guardrails: list[str]
