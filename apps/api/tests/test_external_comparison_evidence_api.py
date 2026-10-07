import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(
    app,
)

ENDPOINT = (
    "/api/evidence/external-comparison"
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


def test_external_evidence_role_is_comparison_only():
    data = get_data()

    assert (
        data[
            "scientific_role"
        ]
        == (
            "independent_external_"
            "comparison_only"
        )
    )

    assert (
        data[
            "independent_external_source"
        ]
        is True
    )

    assert (
        data[
            "numeric_external_comparison_available"
        ]
        is True
    )

    assert (
        data[
            "independent_external_validation_available"
        ]
        is False
    )

    assert (
        data[
            "direct_external_validation_ready"
        ]
        is False
    )


def test_no_rows_are_training_or_validation_eligible():
    data = get_data()

    assert (
        data[
            "training_eligible_count"
        ]
        == 0
    )

    assert (
        data[
            "independent_validation_eligible_count"
        ]
        == 0
    )

    for record in data[
        "comparisons"
    ]:
        assert (
            record[
                "direct_validation_eligible"
            ]
            is False
        )


def test_two_closest_condition_comparisons_are_exposed():
    data = get_data()

    assert (
        data[
            "comparison_count"
        ]
        == 2
    )

    assert len(
        data[
            "comparisons"
        ]
    ) == 2

    by_gravity = {
        item[
            "gravity_context"
        ]: item
        for item in data[
            "comparisons"
        ]
    }

    mg = by_gravity[
        "microgravity"
    ]

    ng = by_gravity[
        "normal_gravity"
    ]

    assert (
        mg[
            "firesense_v0_rate_mm_s"
        ]
        == pytest.approx(
            1.021222865,
            rel=1e-6,
        )
    )

    assert (
        mg[
            "ries_2024_rate_mm_s"
        ]
        == pytest.approx(
            1.419464,
            rel=1e-6,
        )
    )

    assert (
        mg[
            "relative_gap_vs_model_percent"
        ]
        == pytest.approx(
            39.00,
            abs=0.02,
        )
    )

    assert (
        ng[
            "firesense_v0_rate_mm_s"
        ]
        == pytest.approx(
            1.068433985,
            rel=1e-6,
        )
    )

    assert (
        ng[
            "ries_2024_rate_mm_s"
        ]
        == pytest.approx(
            1.279652,
            rel=1e-6,
        )
    )

    assert (
        ng[
            "relative_gap_vs_model_percent"
        ]
        == pytest.approx(
            19.77,
            abs=0.02,
        )
    )


def test_measurement_definition_is_not_overclaimed():
    data = get_data()

    assert (
        data[
            "measurement_definition_classification"
        ]
        == (
            "conceptually_aligned_"
            "operationally_different"
        )
    )

    assert (
        data[
            "measurement_definition_exact_match"
        ]
        is False
    )


def test_flow_mismatch_is_preserved():
    data = get_data()

    assert (
        data[
            "flow_condition_match"
        ]
        is False
    )

    assert (
        data[
            "flow_correction_allowed"
        ]
        is False
    )


def test_release_status_is_scientifically_guarded():
    data = get_data()

    assert (
        data[
            "release_validation_status"
        ]
        == (
            "independent_external_validation_"
            "not_yet_available"
        )
    )

    assert (
        data[
            "release_comparison_status"
        ]
        == (
            "independent_external_comparison_"
            "available"
        )
    )

    assert (
        data[
            "exact_independent_validation_source_found"
        ]
        is False
    )


def test_all_frozen_artifact_hashes_are_verified():
    data = get_data()

    assert (
        data[
            "artifact_sha256_verified"
        ]
        is True
    )

    assert (
        data[
            "artifact_sha256"
        ][
            "comparison"
        ]
        == (
            "704388a360a592cb304511f29efb046ba"
            "b4c571d013766ae17b33c4e3040036f"
        )
    )

    assert (
        data[
            "artifact_sha256"
        ][
            "compatibility"
        ]
        == (
            "39594b51280db4e8ee8d98b43f601804"
            "e92492663fc447205b7dee7d6aa0cc24"
        )
    )

    assert (
        data[
            "artifact_sha256"
        ][
            "flow_transport"
        ]
        == (
            "bee2baea33fbaf3b59c5c002ef4aa9d8"
            "3027ee84396c23147cc786d8084013a7"
        )
    )
