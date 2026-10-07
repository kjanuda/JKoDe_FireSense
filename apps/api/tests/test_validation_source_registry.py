from fastapi.testclient import (
    TestClient,
)

from app.main import app


client = TestClient(
    app,
)


def test_source_registry_endpoint():
    response = client.get(
        "/api/evidence/"
        "validation-source-registry"
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data[
            "artifact_sha256_verified"
        ]
        is True
    )

    assert (
        len(
            data[
                "sources"
            ]
        )
        >= 6
    )


def test_ries_is_comparison_only():
    response = client.post(
        "/api/evidence/"
        "validation-source-check",
        json={
            "source_id": (
                "RIES-2024-PROCI-105358"
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data[
        "known_source"
    ] is True

    assert (
        data[
            "independence_status"
        ]
        == "independent_external"
    )

    assert (
        data[
            "direct_validation_eligible"
        ]
        is False
    )


def test_bassii_same_campaign_is_rejected():
    data = client.post(
        "/api/evidence/"
        "validation-source-check",
        json={
            "source_id": (
                "BHATTACHARJEE-2016-BASSII"
            )
        },
    ).json()

    assert (
        data[
            "independence_status"
        ]
        == "same_campaign_as_training"
    )

    assert (
        data[
            "direct_validation_eligible"
        ]
        is False
    )


def test_takahashi_remains_unverified_lead():
    data = client.post(
        "/api/evidence/"
        "validation-source-check",
        json={
            "source_id": (
                "TAKAHASHI-GIFU-2002"
            )
        },
    ).json()

    assert (
        data[
            "independence_status"
        ]
        == (
            "requires_primary_source_review"
        )
    )

    assert (
        data[
            "direct_validation_eligible"
        ]
        is False
    )


def test_unknown_source_fails_closed():
    data = client.post(
        "/api/evidence/"
        "validation-source-check",
        json={
            "source_id": (
                "UNKNOWN-NEW-SOURCE"
            )
        },
    ).json()

    assert (
        data[
            "known_source"
        ]
        is False
    )

    assert (
        data[
            "direct_validation_eligible"
        ]
        is False
    )

    assert (
        data[
            "independence_status"
        ]
        == (
            "requires_scientific_"
            "provenance_review"
        )
    )
