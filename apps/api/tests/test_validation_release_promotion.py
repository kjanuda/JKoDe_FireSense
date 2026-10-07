from types import SimpleNamespace

from fastapi.testclient import (
    TestClient,
)

from app.main import app

from app.services import (
    validation_release_status
    as release_service,
)


client = TestClient(
    app,
)

ENDPOINT = (
    "/api/evidence/"
    "validation-release-status"
)


def approved_review():
    return SimpleNamespace(
        scientific_review_approved=True,

        review_status=(
            "review_approved_pending_"
            "release_promotion"
        ),

        blocking_reasons=[],
    )


def rejected_review():
    return SimpleNamespace(
        scientific_review_approved=False,

        review_status=(
            "pending_scientific_review"
        ),

        blocking_reasons=[
            (
                "Real scientific review "
                "has not passed."
            )
        ],
    )


def configure_paths(
    monkeypatch,
    tmp_path,
):
    manifest = (
        tmp_path
        / "validation_manifest.json"
    )

    approval = (
        tmp_path
        / "scientific_review_approval.json"
    )

    monkeypatch.setattr(
        release_service,
        "MANIFEST_PATH",
        manifest,
    )

    monkeypatch.setattr(
        release_service,
        "APPROVAL_PATH",
        approval,
    )

    return (
        manifest,
        approval,
    )


def test_no_package_remains_not_validated(
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
            "scientific_status"
        ]
        == (
            "independent_external_validation_"
            "not_yet_available"
        )
    )

    assert (
        data[
            "independent_external_validation_available"
        ]
        is False
    )


def test_failed_review_cannot_promote(
    monkeypatch,
    tmp_path,
):
    manifest, _ = configure_paths(
        monkeypatch,
        tmp_path,
    )

    manifest.write_text(
        "{}\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        release_service,
        "get_validation_scientific_review_status",
        rejected_review,
    )

    data = client.get(
        ENDPOINT
    ).json()

    assert (
        data[
            "scientific_status"
        ]
        == (
            "frozen_candidate_pending_"
            "scientific_review"
        )
    )

    assert (
        data[
            "independent_external_validation_available"
        ]
        is False
    )


def test_approved_review_without_pinned_hashes_cannot_promote(
    monkeypatch,
    tmp_path,
):
    manifest, approval = configure_paths(
        monkeypatch,
        tmp_path,
    )

    manifest.write_text(
        "{}\n",
        encoding="utf-8",
    )

    approval.write_text(
        "{}\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        release_service,
        "get_validation_scientific_review_status",
        approved_review,
    )

    monkeypatch.setattr(
        release_service,
        "APPROVED_MANIFEST_SHA256",
        None,
    )

    monkeypatch.setattr(
        release_service,
        "APPROVED_REVIEW_APPROVAL_SHA256",
        None,
    )

    data = client.get(
        ENDPOINT
    ).json()

    assert (
        data[
            "scientific_status"
        ]
        == (
            "review_approved_pending_"
            "release_promotion"
        )
    )

    assert (
        data[
            "approved_artifact_hash_frozen_in_code"
        ]
        is False
    )

    assert (
        data[
            "independent_external_validation_available"
        ]
        is False
    )


def test_hash_mismatch_fails_closed(
    monkeypatch,
    tmp_path,
):
    manifest, approval = configure_paths(
        monkeypatch,
        tmp_path,
    )

    manifest.write_text(
        '{"manifest": true}\n',
        encoding="utf-8",
    )

    approval.write_text(
        '{"approved": true}\n',
        encoding="utf-8",
    )

    monkeypatch.setattr(
        release_service,
        "get_validation_scientific_review_status",
        approved_review,
    )

    monkeypatch.setattr(
        release_service,
        "APPROVED_MANIFEST_SHA256",
        "0" * 64,
    )

    monkeypatch.setattr(
        release_service,
        "APPROVED_REVIEW_APPROVAL_SHA256",
        "1" * 64,
    )

    response = client.get(
        ENDPOINT
    )

    assert response.status_code == 503


def test_only_exact_pinned_reviewed_package_can_promote(
    monkeypatch,
    tmp_path,
):
    manifest, approval = configure_paths(
        monkeypatch,
        tmp_path,
    )

    manifest.write_text(
        '{"manifest": "reviewed"}\n',
        encoding="utf-8",
    )

    approval.write_text(
        '{"approval": "reviewed"}\n',
        encoding="utf-8",
    )

    monkeypatch.setattr(
        release_service,
        "get_validation_scientific_review_status",
        approved_review,
    )

    monkeypatch.setattr(
        release_service,
        "APPROVED_MANIFEST_SHA256",
        release_service._sha256(
            manifest
        ),
    )

    monkeypatch.setattr(
        release_service,
        "APPROVED_REVIEW_APPROVAL_SHA256",
        release_service._sha256(
            approval
        ),
    )

    response = client.get(
        ENDPOINT
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data[
            "scientific_status"
        ]
        == (
            "independent_external_validation_"
            "approved"
        )
    )

    assert (
        data[
            "scientific_review_approved"
        ]
        is True
    )

    assert (
        data[
            "approved_artifact_hash_frozen_in_code"
        ]
        is True
    )

    assert (
        data[
            "independent_external_validation_available"
        ]
        is True
    )

    # Still separate release gates.
    assert (
        data[
            "production_ready_claim_allowed"
        ]
        is False
    )

    assert (
        data[
            "certification_claim_allowed"
        ]
        is False
    )
