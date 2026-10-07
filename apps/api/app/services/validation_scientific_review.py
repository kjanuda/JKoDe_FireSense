import hashlib
import json
from pathlib import Path
from typing import Any

from app.schemas.validation_scientific_review import (
    ScientificReviewArtifactState,
    ValidationScientificReviewStatusResponse,
)


class ValidationScientificReviewError(
    RuntimeError
):
    pass


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[4]
)


PACKAGE_DIRECTORY = (
    PROJECT_ROOT
    / "data"
    / "curated"
    / "external_validation"
    / "approved_v0"
)


MANIFEST_PATH = (
    PACKAGE_DIRECTORY
    / "validation_manifest.json"
)


EVALUATION_PATH = (
    PACKAGE_DIRECTORY
    / "validation_evaluation.json"
)


PERFORMANCE_PATH = (
    PACKAGE_DIRECTORY
    / "validation_performance.json"
)


UNCERTAINTY_PATH = (
    PACKAGE_DIRECTORY
    / "validation_uncertainty.json"
)


APPROVAL_PATH = (
    PACKAGE_DIRECTORY
    / "scientific_review_approval.json"
)


REQUIRED_REVIEW_CHECKS = [
    "source_independence_verified",
    "experimental_conditions_verified",
    "measurement_compatibility_verified",
    "holdout_integrity_verified",
    "performance_thresholds_verified",
    "uncertainty_review_completed",
    "provenance_complete",
]


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


def _load_json(
    path: Path,
) -> dict[str, Any]:

    try:
        value = json.loads(
            path.read_text(
                encoding="utf-8",
            )
        )

    except Exception as exc:
        raise ValidationScientificReviewError(
            f"Could not parse scientific "
            f"review artifact: {path.name}"
        ) from exc


    if not isinstance(
        value,
        dict,
    ):
        raise ValidationScientificReviewError(
            f"Unexpected JSON structure in "
            f"{path.name}."
        )

    return value


def _artifact_state(
) -> ScientificReviewArtifactState:

    return ScientificReviewArtifactState(
        validation_manifest_present=(
            MANIFEST_PATH.exists()
        ),

        validation_evaluation_present=(
            EVALUATION_PATH.exists()
        ),

        validation_performance_present=(
            PERFORMANCE_PATH.exists()
        ),

        validation_uncertainty_present=(
            UNCERTAINTY_PATH.exists()
        ),

        scientific_review_approval_present=(
            APPROVAL_PATH.exists()
        ),
    )


def _guardrails() -> list[str]:

    return [
        (
            "A reviewer approval artifact cannot "
            "override failed compatibility, "
            "performance, uncertainty or "
            "provenance gates."
        ),
        (
            "Scientific review is bound to frozen "
            "artifacts through SHA-256."
        ),
        (
            "A forged or stale approval artifact "
            "fails closed."
        ),
        (
            "External-validation status is not "
            "promoted by this endpoint."
        ),
        (
            "Production readiness and "
            "certification remain separate gates."
        ),
    ]


def _response(
    *,
    status: str,
    artifacts: ScientificReviewArtifactState,
    integrity: bool,
    approved: bool,
    performance: bool,
    uncertainty: bool,
    blockers: list[str],
) -> ValidationScientificReviewStatusResponse:

    return ValidationScientificReviewStatusResponse(
        review_status_id=(
            "FIRESENSE-SCIENTIFIC-"
            "REVIEW-STATUS-V0"
        ),

        version="v0",

        review_status=status,

        artifacts=artifacts,

        artifact_integrity_verified=integrity,

        scientific_review_approved=approved,

        performance_gate_passed=performance,

        uncertainty_coverage_verified=uncertainty,

        # Promotion is a separate Step 198 gate.
        external_validation_claim_allowed=False,

        production_ready_claim_allowed=False,

        certification_claim_allowed=False,

        blocking_reasons=blockers,

        guardrails=_guardrails(),
    )


def get_validation_scientific_review_status(
) -> ValidationScientificReviewStatusResponse:

    artifacts = _artifact_state()


    if (
        not artifacts
        .validation_manifest_present
    ):
        return _response(
            status=(
                "no_frozen_validation_package"
            ),

            artifacts=artifacts,

            integrity=False,

            approved=False,

            performance=False,

            uncertainty=False,

            blockers=[
                (
                    "No real frozen independent "
                    "validation package is "
                    "installed."
                ),
            ],
        )


    required_package_files = [
        EVALUATION_PATH,
        PERFORMANCE_PATH,
        UNCERTAINTY_PATH,
    ]

    missing = [
        path.name
        for path
        in required_package_files
        if not path.exists()
    ]


    if missing:
        return _response(
            status=(
                "frozen_package_incomplete"
            ),

            artifacts=artifacts,

            integrity=False,

            approved=False,

            performance=False,

            uncertainty=False,

            blockers=[
                (
                    "Frozen validation package "
                    "is incomplete: "
                    + ", ".join(
                        missing
                    )
                ),
            ],
        )


    performance = _load_json(
        PERFORMANCE_PATH
    )

    uncertainty = _load_json(
        UNCERTAINTY_PATH
    )


    performance_passed = (
        performance.get(
            "performance_gate_passed"
        )
        is True
    )

    uncertainty_passed = all(
        [
            uncertainty.get(
                "coverage_verification_passed"
            )
            is True,

            uncertainty.get(
                "uncertainty_calibration_claim_allowed"
            )
            is True,
        ]
    )


    if not APPROVAL_PATH.exists():

        blockers = [
            (
                "Scientific review approval "
                "artifact has not been created."
            )
        ]

        if not performance_passed:
            blockers.append(
                "Performance gate has not passed."
            )

        if not uncertainty_passed:
            blockers.append(
                (
                    "Calibrated uncertainty "
                    "coverage has not been verified."
                )
            )


        return _response(
            status=(
                "pending_scientific_review"
            ),

            artifacts=artifacts,

            integrity=False,

            approved=False,

            performance=performance_passed,

            uncertainty=uncertainty_passed,

            blockers=blockers,
        )


    approval = _load_json(
        APPROVAL_PATH
    )


    if (
        approval.get(
            "approval_id"
        )
        != (
            "FIRESENSE-SCIENTIFIC-"
            "REVIEW-APPROVAL-V0"
        )
    ):
        raise ValidationScientificReviewError(
            "Unexpected scientific review "
            "approval identity."
        )


    if (
        approval.get(
            "version"
        )
        != "v0"
    ):
        raise ValidationScientificReviewError(
            "Unexpected scientific review "
            "approval version."
        )


    if (
        approval.get(
            "scientific_review_approved"
        )
        is not True
    ):
        return _response(
            status=(
                "review_artifact_not_approved"
            ),

            artifacts=artifacts,

            integrity=False,

            approved=False,

            performance=performance_passed,

            uncertainty=uncertainty_passed,

            blockers=[
                (
                    "Scientific reviewer has "
                    "not approved the validation "
                    "package."
                ),
            ],
        )


    checks = approval.get(
        "review_checks",
        {},
    )

    failed_checks = [
        check
        for check
        in REQUIRED_REVIEW_CHECKS
        if (
            checks.get(
                check
            )
            is not True
        )
    ]


    if failed_checks:
        raise ValidationScientificReviewError(
            "Scientific review approval is "
            "internally inconsistent; required "
            "checks are false or missing: "
            + ", ".join(
                failed_checks
            )
        )


    expected_hashes = approval.get(
        "reviewed_artifact_sha256",
        {},
    )


    artifacts_to_verify = {
        "validation_manifest": (
            MANIFEST_PATH
        ),

        "validation_evaluation": (
            EVALUATION_PATH
        ),

        "validation_performance": (
            PERFORMANCE_PATH
        ),

        "validation_uncertainty": (
            UNCERTAINTY_PATH
        ),
    }


    for (
        artifact_name,
        path,
    ) in artifacts_to_verify.items():

        expected = expected_hashes.get(
            artifact_name
        )

        actual = _sha256(
            path
        )

        if (
            not expected
            or expected != actual
        ):
            raise ValidationScientificReviewError(
                (
                    "Scientific review artifact "
                    "hash mismatch for "
                    f"{artifact_name}."
                )
            )


    if not performance_passed:

        return _response(
            status=(
                "review_artifact_not_approved"
            ),

            artifacts=artifacts,

            integrity=True,

            approved=False,

            performance=False,

            uncertainty=uncertainty_passed,

            blockers=[
                (
                    "Reviewer approval cannot "
                    "override a failed "
                    "performance gate."
                ),
            ],
        )


    if not uncertainty_passed:

        return _response(
            status=(
                "review_artifact_not_approved"
            ),

            artifacts=artifacts,

            integrity=True,

            approved=False,

            performance=True,

            uncertainty=False,

            blockers=[
                (
                    "Reviewer approval cannot "
                    "override missing calibrated "
                    "uncertainty coverage."
                ),
            ],
        )


    return _response(
        status=(
            "review_approved_pending_"
            "release_promotion"
        ),

        artifacts=artifacts,

        integrity=True,

        approved=True,

        performance=True,

        uncertainty=True,

        blockers=[
            (
                "Scientific review has passed, "
                "but release-state promotion "
                "must still pass Step 198."
            ),
        ],
    )
