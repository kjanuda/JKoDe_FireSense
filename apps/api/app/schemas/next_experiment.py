from typing import Literal

from pydantic import BaseModel


CandidateBasis = Literal[
    "empirical_coverage_gap"
]

RecommendationStatus = Literal[
    "coverage_candidate_only",
    "bayesian_optimization_pending",
]

ApprovalStatus = Literal[
    "not_approved"
]


class ExperimentCondition(BaseModel):
    material: Literal[
        "PMMA"
    ] = "PMMA"

    geometry: Literal[
        "thin_sheet"
    ] = "thin_sheet"

    thickness_um: float

    oxygen_fraction: float

    pressure_kpa: float


class GravityCandidate(BaseModel):
    gravity_regime: Literal[
        "microgravity",
        "normal_gravity",
    ]

    candidate_thickness_um: float

    gap_left_um: float
    gap_right_um: float

    log_gap_decades: float

    left_record_id: str
    right_record_id: str


class MatchedPairCandidate(BaseModel):
    thickness_um: float

    microgravity_thickness_um: float

    normal_gravity_thickness_um: float

    relative_difference: float

    similar_thickness: bool


class NextExperimentCandidateResponse(BaseModel):
    candidate_id: str

    basis: CandidateBasis

    recommendation_status: (
        RecommendationStatus
    )

    approval_status: ApprovalStatus

    experiment_condition: (
        ExperimentCondition
    )

    matched_pair: (
        MatchedPairCandidate
    )

    gravity_candidates: list[
        GravityCandidate
    ]

    rationale: list[str]

    scientific_guardrails: list[str]

    required_before_bayesian_recommendation: list[str]

    required_before_experiment_approval: list[str]

    production_ready: Literal[
        False
    ] = False