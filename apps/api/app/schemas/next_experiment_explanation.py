from typing import Literal

from pydantic import BaseModel


class DecisionTraceStep(
    BaseModel
):
    order: int

    stage: Literal[
        "evidence",
        "coverage",
        "bayesian",
        "agreement",
        "decision",
    ]

    title: str
    explanation: str


class RatioRangeSummary(
    BaseModel
):
    predicted_ratio: float
    one_sd_factor: float

    descriptive_lower: float
    descriptive_upper: float

    interpretation: str


class RecommendationUncertaintyExplanation(
    BaseModel
):
    microgravity_posterior_sd_log_residual: float
    normal_gravity_posterior_sd_log_residual: float

    matched_pair_joint_sd_log: float

    ratio_range: RatioRangeSummary

    uncertainty_target: str

    interpretation: str

    calibration_status: Literal[
        "not_externally_calibrated"
    ]


class RecommendationEvidenceExplanation(
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

    interpretation: str


class NextExperimentExplanationResponse(
    BaseModel
):
    candidate_id: str

    title: str

    summary: str

    thickness_um: float

    decision_status: Literal[
        "research_priority_candidate"
    ]

    approval_status: Literal[
        "not_approved"
    ]

    production_ready: Literal[False]

    why_this_thickness: list[str]

    decision_trace: list[
        DecisionTraceStep
    ]

    uncertainty: (
        RecommendationUncertaintyExplanation
    )

    evidence: (
        RecommendationEvidenceExplanation
    )

    scientific_caveats: list[str]

    required_before_experiment_approval: (
        list[str]
    )