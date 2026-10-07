from typing import Literal

from pydantic import BaseModel


class ExistingObservationSummary(
    BaseModel
):
    thickness_um: float
    absolute_distance_um: float
    log_ratio_distance: float


class GravityRecommendationSummary(
    BaseModel
):
    predicted_spread_rate_mm_s: float
    posterior_sd_log_residual: float

    nearest_existing_observation: (
        ExistingObservationSummary
    )


class AgreementSummary(
    BaseModel
):
    coverage_candidate_um: float
    bayesian_candidate_um: float
    absolute_difference_um: float
    relative_difference_percent: float
    within_one_percent: bool


class JointUncertaintySummary(
    BaseModel
):
    matched_pair_joint_sd_log: float
    one_sd_ratio_uncertainty_factor: float
    predicted_mg_to_ng_spread_ratio: float


class ExperimentFamilySummary(
    BaseModel
):
    material: str
    geometry_family: str
    oxygen_percent: float
    pressure_kpa: float
    matched_variable: str
    gravity_regimes: list[str]


class EvidenceSummary(
    BaseModel
):
    source_id: str
    figure: str
    dataset_version: str
    dataset_sha256: str

    shared_canonical_evidence: bool
    independent_validation: bool

    external_validation: Literal[
        "not_performed"
    ]


class ArtifactIntegritySummary(
    BaseModel
):
    dataset_sha256_verified: bool
    coverage_artifact_sha256_verified: bool
    bayesian_artifact_sha256_verified: bool


class NextExperimentRecommendationResponse(
    BaseModel
):
    candidate_id: str

    decision_status: Literal[
        "research_priority_candidate"
    ]

    recommendation_status: Literal[
        "bayesian_candidate_only"
    ]

    approval_status: Literal[
        "not_approved"
    ]

    production_ready: Literal[False]

    thickness_um: float

    why_selected: str

    experiment_family: (
        ExperimentFamilySummary
    )

    agreement: AgreementSummary

    microgravity: (
        GravityRecommendationSummary
    )

    normal_gravity: (
        GravityRecommendationSummary
    )

    joint_uncertainty: (
        JointUncertaintySummary
    )

    evidence: EvidenceSummary

    integrity: (
        ArtifactIntegritySummary
    )

    scientific_guardrails: list[str]

    required_before_experiment_approval: (
        list[str]
    )