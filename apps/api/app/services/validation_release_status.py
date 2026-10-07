import hashlib
from pathlib import Path

from app.schemas.validation_release_status import (
    ValidationReleaseStatusResponse,
)

from app.services.validation_scientific_review import (
    ValidationScientificReviewError,
    get_validation_scientific_review_status,
)


class ValidationReleaseStatusError(
    RuntimeError
):
    pass


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[4]
)


FROZEN_DIRECTORY = (
    PROJECT_ROOT
    / "data"
    / "curated"
    / "external_validation"
    / "approved_v0"
)


MANIFEST_PATH = (
    FROZEN_DIRECTORY
    / "validation_manifest.json"
)


APPROVAL_PATH = (
    FROZEN_DIRECTORY
    / "scientific_review_approval.json"
)


# -------------------------------------------------
# TRUST ANCHORS
# -------------------------------------------------
#
# DO NOT fill these from synthetic/test evidence.
#
# After a real independent validation package:
#
# 1. passes compatibility
# 2. passes frozen performance thresholds
# 3. passes calibrated uncertainty coverage
# 4. passes scientific provenance review
# 5. receives reviewer approval
#
# then manually freeze the reviewed SHA-256 values.
#
APPROVED_MANIFEST_SHA256: (
    str | None
) = None

APPROVED_REVIEW_APPROVAL_SHA256: (
    str | None
) = None


def _sha256(
    path: Path,
) -> str:

    digest = hashlib.sha256()

    with path.open(
        "rb",
    ) as handle:

        for chunk in iter(
            lambda: handle.read(
                1024 * 1024
            ),
            b"",
        ):
            digest.update(
                chunk
            )

    return digest.hexdigest()


def _guardrails() -> list[str]:

    return [
        (
            "A candidate API request can never "
            "directly promote FireSense to "
            "externally validated status."
        ),
        (
            "Promotion requires a real frozen "
            "independent validation package."
        ),
        (
            "Scientific review must independently "
            "pass compatibility, performance, "
            "uncertainty and provenance gates."
        ),
        (
            "Both the validation manifest and "
            "scientific approval artifact must "
            "match SHA-256 trust anchors pinned "
            "in source code."
        ),
        (
            "Synthetic or test artifacts can never "
            "become release trust anchors."
        ),
        (
            "Independent external validation does "
            "not imply certification."
        ),
        (
            "Independent external validation does "
            "not automatically imply production "
            "readiness."
        ),
    ]


def _response(
    *,
    scientific_status: str,
    frozen_candidate_available: bool,
    scientific_review_approved: bool,
    hashes_pinned: bool,
    validation_available: bool,
    blockers: list[str],
) -> ValidationReleaseStatusResponse:

    return ValidationReleaseStatusResponse(
        release_status_id=(
            "FIRESENSE-VALIDATION-"
            "RELEASE-STATUS-V0"
        ),

        version="v0",

        scientific_status=(
            scientific_status
        ),

        frozen_candidate_available=(
            frozen_candidate_available
        ),

        scientific_review_approved=(
            scientific_review_approved
        ),

        approved_artifact_hash_frozen_in_code=(
            hashes_pinned
        ),

        independent_external_validation_available=(
            validation_available
        ),

        production_ready_claim_allowed=False,

        certification_claim_allowed=False,

        blocking_reasons=blockers,

        guardrails=_guardrails(),
    )


def get_validation_release_status(
) -> ValidationReleaseStatusResponse:

    if not MANIFEST_PATH.exists():

        return _response(
            scientific_status=(
                "independent_external_validation_"
                "not_yet_available"
            ),

            frozen_candidate_available=False,

            scientific_review_approved=False,

            hashes_pinned=False,

            validation_available=False,

            blockers=[
                (
                    "No real frozen independent "
                    "validation package is installed."
                ),
                (
                    "Scientific validation release "
                    "promotion cannot begin."
                ),
            ],
        )


    try:
        review = (
            get_validation_scientific_review_status()
        )

    except ValidationScientificReviewError as exc:
        raise ValidationReleaseStatusError(
            "Scientific review verification failed: "
            + str(
                exc
            )
        ) from exc


    if (
        review.scientific_review_approved
        is not True
    ):

        return _response(
            scientific_status=(
                "frozen_candidate_pending_"
                "scientific_review"
            ),

            frozen_candidate_available=True,

            scientific_review_approved=False,

            hashes_pinned=False,

            validation_available=False,

            blockers=list(
                review.blocking_reasons
            ),
        )


    if (
        review.review_status
        != (
            "review_approved_pending_"
            "release_promotion"
        )
    ):
        raise ValidationReleaseStatusError(
            "Scientific review reported an "
            "unexpected promotion state."
        )


    hashes_pinned = all(
        [
            APPROVED_MANIFEST_SHA256
            is not None,

            APPROVED_REVIEW_APPROVAL_SHA256
            is not None,
        ]
    )


    if not hashes_pinned:

        return _response(
            scientific_status=(
                "review_approved_pending_"
                "release_promotion"
            ),

            frozen_candidate_available=True,

            scientific_review_approved=True,

            hashes_pinned=False,

            validation_available=False,

            blockers=[
                (
                    "Scientific review passed, but "
                    "release trust-anchor SHA-256 "
                    "values have not been pinned "
                    "in source code."
                ),
            ],
        )


    if not APPROVAL_PATH.exists():
        raise ValidationReleaseStatusError(
            "Scientific review approval artifact "
            "is missing during promotion."
        )


    actual_manifest_sha = _sha256(
        MANIFEST_PATH
    )

    actual_approval_sha = _sha256(
        APPROVAL_PATH
    )


    if (
        actual_manifest_sha
        != APPROVED_MANIFEST_SHA256
    ):
        raise ValidationReleaseStatusError(
            "Approved validation manifest "
            "SHA-256 verification failed."
        )


    if (
        actual_approval_sha
        != APPROVED_REVIEW_APPROVAL_SHA256
    ):
        raise ValidationReleaseStatusError(
            "Scientific review approval "
            "SHA-256 verification failed."
        )


    # -------------------------------------------------
    # FINAL SCIENTIFIC PROMOTION
    # -------------------------------------------------
    #
    # Reaching this branch means:
    #
    # - real frozen package exists
    # - scientific review gate passed
    # - performance gate passed
    # - calibrated uncertainty coverage passed
    # - provenance review passed
    # - reviewer approval was SHA-bound
    # - release trust anchors match exactly
    #
    return _response(
        scientific_status=(
            "independent_external_validation_"
            "approved"
        ),

        frozen_candidate_available=True,

        scientific_review_approved=True,

        hashes_pinned=True,

        validation_available=True,

        blockers=[
            (
                "Independent external validation "
                "is approved within the declared "
                "FireSense v0 validation domain."
            ),
            (
                "Production engineering and "
                "certification remain separate."
            ),
        ],
    )
