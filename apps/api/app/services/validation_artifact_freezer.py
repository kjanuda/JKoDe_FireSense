import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from app.schemas.validation_candidate import (
    ValidationCandidateEvaluationResponse,
    ValidationCandidateRequest,
)

from app.services.validation_candidate_evaluator import (
    evaluate_validation_candidate,
)


class ValidationArtifactFreezeError(
    RuntimeError
):
    pass


def _canonical_json_bytes(
    value: object,
) -> bytes:
    return (
        json.dumps(
            value,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        )
        + "\n"
    ).encode(
        "utf-8"
    )


def _sha256_bytes(
    value: bytes,
) -> str:
    return hashlib.sha256(
        value
    ).hexdigest()


def _looks_synthetic(
    candidate: ValidationCandidateRequest,
) -> bool:
    # Do not reject legitimate scientific
    # descriptions merely because they contain
    # words such as "test" or "testing".
    #
    # Synthetic software fixtures must use
    # explicit fixture-like identifiers or
    # provenance markers.

    identifiers = [
        candidate.dataset_id,
        candidate.dataset_version,
        candidate.source.source_id,
    ]

    identifier_markers = (
        "TEST-",
        "TEST_",
        "PYTEST",
        "SYNTHETIC",
        "FIXTURE",
        "DUMMY",
        "MOCK",
    )

    for value in identifiers:
        normalized = (
            value
            .strip()
            .upper()
        )

        if any(
            normalized.startswith(
                marker
            )
            for marker
            in identifier_markers
        ):
            return True


    descriptive_context = " ".join(
        [
            candidate.source.source_title,
            candidate.source.provenance_reference,
        ]
    ).upper()

    explicit_fixture_markers = (
        "SYNTHETIC",
        "PYTEST",
        "SOFTWARE FIXTURE",
        "TEST FIXTURE",
        "DUMMY DATA",
        "MOCK DATA",
        "NOT SCIENTIFIC EVIDENCE",
    )

    return any(
        marker in descriptive_context
        for marker
        in explicit_fixture_markers
    )

def freeze_validation_candidate(
    candidate: ValidationCandidateRequest,
    output_directory: Path,
) -> dict:

    if _looks_synthetic(
        candidate
    ):
        raise ValidationArtifactFreezeError(
            "Synthetic/test candidate data "
            "cannot be frozen as scientific "
            "validation evidence."
        )

    result = evaluate_validation_candidate(
        candidate
    )

    if (
        result.direct_validation_gate_passed
        is not True
    ):
        raise ValidationArtifactFreezeError(
            "Candidate cannot be frozen because "
            "the direct-validation compatibility "
            "gate did not pass."
        )

    if (
        result.holdout_evaluation_completed
        is not True
    ):
        raise ValidationArtifactFreezeError(
            "Candidate cannot be frozen because "
            "holdout evaluation is incomplete."
        )

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    candidate_payload = (
        candidate.model_dump(
            mode="json",
        )
    )

    result_payload = (
        result.model_dump(
            mode="json",
        )
    )

    candidate_bytes = (
        _canonical_json_bytes(
            candidate_payload
        )
    )

    result_bytes = (
        _canonical_json_bytes(
            result_payload
        )
    )

    candidate_sha = (
        _sha256_bytes(
            candidate_bytes
        )
    )

    result_sha = (
        _sha256_bytes(
            result_bytes
        )
    )

    candidate_path = (
        output_directory
        / "validation_candidate.json"
    )

    result_path = (
        output_directory
        / "validation_evaluation.json"
    )

    candidate_path.write_bytes(
        candidate_bytes
    )

    result_path.write_bytes(
        result_bytes
    )

    manifest = {
        "manifest_id": (
            "FIRESENSE-FROZEN-"
            "VALIDATION-CANDIDATE-V0"
        ),
        "manifest_version": "v0",

        "scientific_status": (
            "frozen_candidate_pending_"
            "scientific_review"
        ),

        "external_validation_claim_allowed": False,

        "production_ready_claim_allowed": False,

        "certification_claim_allowed": False,

        "dataset_id": (
            candidate.dataset_id
        ),

        "source_id": (
            candidate.source.source_id
        ),

        "frozen_at_utc": (
            datetime.now(
                timezone.utc
            ).isoformat()
        ),

        "candidate_sha256": (
            candidate_sha
        ),

        "evaluation_sha256": (
            result_sha
        ),

        "compatibility_gate_passed": (
            result.direct_validation_gate_passed
        ),

        "holdout_evaluation_completed": (
            result.holdout_evaluation_completed
        ),

        "metrics_role": (
            result.metrics_role
        ),

        "review_requirements": [
            (
                "Verify source independence "
                "against primary provenance."
            ),
            (
                "Verify experimental conditions "
                "against source documentation."
            ),
            (
                "Review MAE, RMSE, bias and "
                "relative-error results."
            ),
            (
                "Review experimental and "
                "digitization uncertainty."
            ),
            (
                "Confirm measurement-definition "
                "matching or cross-calibration."
            ),
            (
                "Approve a pre-registered "
                "performance acceptance basis."
            ),
            (
                "Scientific reviewer sign-off "
                "is required before validation "
                "status can change."
            ),
        ],

        "guardrails": [
            (
                "Freezing a candidate does not "
                "constitute independent external "
                "validation."
            ),
            (
                "Frozen validation evidence "
                "must remain excluded from "
                "model training."
            ),
            (
                "Synthetic/test fixtures are "
                "forbidden from scientific "
                "artifact freezing."
            ),
        ],
    }

    manifest_bytes = (
        _canonical_json_bytes(
            manifest
        )
    )

    manifest_sha = (
        _sha256_bytes(
            manifest_bytes
        )
    )

    manifest_path = (
        output_directory
        / "validation_manifest.json"
    )

    manifest_path.write_bytes(
        manifest_bytes
    )

    sha_path = (
        output_directory
        / "validation_manifest.sha256"
    )

    sha_path.write_text(
        manifest_sha + "\n",
        encoding="utf-8",
    )

    return {
        "candidate_path": str(
            candidate_path
        ),
        "evaluation_path": str(
            result_path
        ),
        "manifest_path": str(
            manifest_path
        ),
        "manifest_sha256_path": str(
            sha_path
        ),
        "candidate_sha256": (
            candidate_sha
        ),
        "evaluation_sha256": (
            result_sha
        ),
        "manifest_sha256": (
            manifest_sha
        ),
        "scientific_status": (
            "frozen_candidate_pending_"
            "scientific_review"
        ),
    }
