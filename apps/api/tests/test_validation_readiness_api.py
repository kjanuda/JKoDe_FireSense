from fastapi.testclient import TestClient

from app.main import app


client = TestClient(
    app,
)

ENDPOINT = (
    "/api/evidence/validation-readiness"
)


def get_data():
    response = client.get(
        ENDPOINT,
    )

    assert (
        response.status_code
        == 200
    )

    return response.json()


def test_endpoint_returns_200():
    response = client.get(
        ENDPOINT,
    )

    assert (
        response.status_code
        == 200
    )


def test_validation_protocol_identity():
    data = get_data()

    assert (
        data[
            "readiness_id"
        ]
        == (
            "FIRESENSE-VALIDATION-"
            "READINESS-V0"
        )
    )

    assert (
        data[
            "validation_protocol_id"
        ]
        == (
            "FIRESENSE-INDEPENDENT-"
            "VALIDATION-ACCEPTANCE-V0"
        )
    )

    assert (
        data[
            "version"
        ]
        == "v0"
    )


def test_validation_target_is_frozen():
    data = get_data()

    target = data[
        "target"
    ]

    assert (
        target[
            "material"
        ]
        == "PMMA"
    )

    assert (
        target[
            "geometry_family"
        ]
        == "thin_sheet"
    )

    assert (
        target[
            "thickness_um"
        ]
        == 200.0
    )

    assert (
        target[
            "oxygen_percent"
        ]
        == 21.0
    )

    assert (
        target[
            "pressure_kpa"
        ]
        == 101.325
    )

    assert (
        target[
            "microgravity_configuration"
        ]
        == "opposed_flow"
    )

    assert (
        target[
            "microgravity_flow_mm_s"
        ]
        == 50.0
    )

    assert (
        target[
            "independent_campaign_required"
        ]
        is True
    )


def test_minimum_validation_scope_is_frozen():
    data = get_data()

    scope = data[
        "minimum_validation_scope"
    ]

    assert (
        scope[
            "independent_source_count"
        ]
        == 1
    )

    assert (
        scope[
            "minimum_independent_numeric_points"
        ]
        == 3
    )


def test_current_validation_state_is_not_overclaimed():
    data = get_data()

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

    assert (
        data[
            "independent_external_comparison_available"
        ]
        is True
    )

    assert (
        data[
            "exact_source_found"
        ]
        is False
    )

    assert (
        data[
            "exact_validation_source_count"
        ]
        == 0
    )


def test_screening_summary_is_preserved():
    data = get_data()

    assert (
        data[
            "screened_candidate_count"
        ]
        == 5
    )

    assert (
        data[
            "independent_comparison_source_count"
        ]
        == 4
    )


def test_ries_remains_comparison_only():
    data = get_data()

    assert (
        data[
            "ries_2024_classification"
        ]
        == "independent_external_comparison"
    )

    assert (
        data[
            "ries_2024_direct_validation_eligible"
        ]
        is False
    )

    assert len(
        data[
            "ries_2024_blocking_reasons"
        ]
    ) == 3


def test_production_and_certification_claims_are_blocked():
    data = get_data()

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


def test_frozen_artifacts_are_verified():
    data = get_data()

    assert (
        data[
            "artifact_sha256_verified"
        ]
        is True
    )

    assert (
        data[
            "acceptance_criteria_sha256"
        ]
        == (
            "a3c7a88c3ad52efbb2a3170fd67d5d9219bb25ac7325f3950954dd8962c9e783"
        )
    )

    assert (
        data[
            "source_screening_sha256"
        ]
        == (
            "96ba875285756f03df3a582cd89e16d77695baf9b9eae8553762e8a449d8b484"
        )
    )
