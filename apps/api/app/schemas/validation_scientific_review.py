from typing import Literal

from pydantic import BaseModel


class ScientificReviewArtifactState(
    BaseModel
):
    validation_manifest_present: bool
    validation_evaluation_present: bool
    validation_performance_present: bool
    validation_uncertainty_present: bool
    scientific_review_approval_present: bool


class ValidationScientificReviewStatusResponse(
    BaseModel
):
    review_status_id: str

    version: Literal["v0"]

    review_status: Literal[
        "no_frozen_validation_package",
        "frozen_package_incomplete",
        "pending_scientific_review",
        "review_artifact_not_approved",
        "review_approved_pending_release_promotion",
    ]

    artifacts: ScientificReviewArtifactState

    artifact_integrity_verified: bool

    scientific_review_approved: bool

    performance_gate_passed: bool

    uncertainty_coverage_verified: bool

    external_validation_claim_allowed: Literal[
        False
    ]

    production_ready_claim_allowed: Literal[
        False
    ]

    certification_claim_allowed: Literal[
        False
    ]

    blocking_reasons: list[str]

    guardrails: list[str]
