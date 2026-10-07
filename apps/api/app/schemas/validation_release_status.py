from typing import Literal

from pydantic import BaseModel


class ValidationReleaseStatusResponse(BaseModel):
    release_status_id: str

    version: Literal["v0"]

    scientific_status: Literal[
        "independent_external_validation_not_yet_available",
        "frozen_candidate_pending_scientific_review",
        "review_approved_pending_release_promotion",
        "independent_external_validation_approved",
    ]

    frozen_candidate_available: bool

    scientific_review_approved: bool

    approved_artifact_hash_frozen_in_code: bool

    independent_external_validation_available: bool

    production_ready_claim_allowed: Literal[
        False
    ]

    certification_claim_allowed: Literal[
        False
    ]

    blocking_reasons: list[str]

    guardrails: list[str]
