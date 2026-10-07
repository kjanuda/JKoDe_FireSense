import json

from fastapi.testclient import (
    TestClient,
)

from app.main import app

from app.services import (
    validation_scientific_review
    as review_service,
)


client = TestClient(
    app,
)


ENDPOINT = (
    "/api/evidence/"
    "validation-scientific-review-status"
)


def configure_paths(
    monkeypatch,
    tmp_path,
):
    monkeypatch.setattr(
        review_service,
        "PACKAGE_DIRECTORY",
        tmp_path,
    )

    monkeypatch.setattr(
        review_service,
        "MANIFEST_PATH",
        tmp_path
        / "validation_manifest.json",
    )

    monkeypatch.setattr(
        review_service,
        "EVALUATION_PATH",
        tmp_path
        / "validation_evaluation.json",
    )

    monkeypatch.setattr(
        review_service,
        "PERFORMANCE_PATH",
        tmp_path
        / "validation_performance.json",
    )

    monkeypatch.setattr(
        review_service,
        "UNCERTAINTY_PATH",
        tmp_path
        / "validation_uncertainty.json",
    )

    monkeypatch.setattr(
        review_service,
        "APPROVAL_PATH",
        tmp_path
        / "scientific_review_approval.json",
    )


def write_json(
    path,
    value,
):
    path.write_text(
        json.dumps(
            value,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def test_no_real_package_fails_closed(
    monkeypatch,
    tmp_path,
):
    configure_paths(
        monkeypatch,
        tmp_path,
    )

    response = client.get(
        ENDPOINT
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data[
            "review_status"
        ]
        == "no_frozen_validation_package"
    )

    assert (
        data[
            "scientific_review_approved"
        ]
        is False
    )

    assert (
        data[
            "external_validation_claim_allowed"
        ]
        is False
    )


def test_incomplete_package_is_blocked(
    monkeypatch,
    tmp_path,
):
    configure_paths(
        monkeypatch,
        tmp_path,
    )

    write_json(
        review_service.MANIFEST_PATH,
        {
            "test": True,
        },
    )

    data = client.get(
        ENDPOINT
    ).json()

    assert (
        data[
            "review_status"
        ]
        == "frozen_package_incomplete"
    )


def test_pending_review_still_blocks_validation(
    monkeypatch,
    tmp_path,
):
    configure_paths(
        monkeypatch,
        tmp_path,
    )

    write_json(
        review_service.MANIFEST_PATH,
        {},
    )

    write_json(
        review_service.EVALUATION_PATH,
        {},
    )

    write_json(
        review_service.PERFORMANCE_PATH,
        {
            "performance_gate_passed": True,
        },
    )

    write_json(
        review_service.UNCERTAINTY_PATH,
        {
            "coverage_verification_passed": False,
            "uncertainty_calibration_claim_allowed": False,
        },
    )

    data = client.get(
        ENDPOINT
    ).json()

    assert (
        data[
            "review_status"
        ]
        == "pending_scientific_review"
    )

    assert (
        data[
            "uncertainty_coverage_verified"
        ]
        is False
    )

    assert (
        data[
            "external_validation_claim_allowed"
        ]
        is False
    )


def test_forged_approval_cannot_override_uncertainty_gate(
    monkeypatch,
    tmp_path,
):
    configure_paths(
        monkeypatch,
        tmp_path,
    )

    write_json(
        review_service.MANIFEST_PATH,
        {},
    )

    write_json(
        review_service.EVALUATION_PATH,
        {},
    )

    write_json(
        review_service.PERFORMANCE_PATH,
        {
            "performance_gate_passed": True,
        },
    )

    write_json(
        review_service.UNCERTAINTY_PATH,
        {
            "coverage_verification_passed": False,
            "uncertainty_calibration_claim_allowed": False,
        },
    )

    artifact_hashes = {
        "validation_manifest": (
            review_service._sha256(
                review_service.MANIFEST_PATH
            )
        ),
        "validation_evaluation": (
            review_service._sha256(
                review_service.EVALUATION_PATH
            )
        ),
        "validation_performance": (
            review_service._sha256(
                review_service.PERFORMANCE_PATH
            )
        ),
        "validation_uncertainty": (
            review_service._sha256(
                review_service.UNCERTAINTY_PATH
            )
        ),
    }

    approval = {
        "approval_id": (
            "FIRESENSE-SCIENTIFIC-"
            "REVIEW-APPROVAL-V0"
        ),
        "version": "v0",
        "scientific_review_approved": True,
        "reviewed_artifact_sha256": (
            artifact_hashes
        ),
        "review_checks": {
            "source_independence_verified": True,
            "experimental_conditions_verified": True,
            "measurement_compatibility_verified": True,
            "holdout_integrity_verified": True,
            "performance_thresholds_verified": True,
            "uncertainty_review_completed": True,
            "provenance_complete": True,
        },
    }

    write_json(
        review_service.APPROVAL_PATH,
        approval,
    )

    data = client.get(
        ENDPOINT
    ).json()

    assert (
        data[
            "review_status"
        ]
        == "review_artifact_not_approved"
    )

    assert (
        data[
            "performance_gate_passed"
        ]
        is True
    )

    assert (
        data[
            "uncertainty_coverage_verified"
        ]
        is False
    )

    assert (
        data[
            "scientific_review_approved"
        ]
        is False
    )
