from fastapi.testclient import (
    TestClient,
)

from app.main import app


client = TestClient(
    app,
)

ENDPOINT = (
    "/api/evidence/"
    "validation-candidate/performance"
)


def candidate():
    return {
        "dataset_id": (
            "TEST-SYNTHETIC-"
            "PERFORMANCE-V0"
        ),
        "dataset_version": "test-v0",

        "source": {
            "source_id": "TEST-SYNTHETIC",
            "source_title": (
                "Synthetic pytest fixture"
            ),
            "provenance_reference": (
                "pytest-only"
            ),
            "independent_publication_or_dataset": True,
            "independent_experimental_campaign": True,
            "not_firesense_training_source": True,
            "not_reused_bass_ii_rows": True,
            "experimental_data_only": True,
            "measurement_quantity": (
                "flame_spread_rate"
            ),
            "measurement_definition_matches": True,
            "cross_calibration_available": False,
            "normal_gravity_transport_equivalence_established": True,
            "uncertainty_or_variability_metadata_preserved": True,
            "digitization_uncertainty_separate": True,
            "experimental_uncertainty_separate": True,
            "model_uncertainty_separate": True,
        },

        "records": [
            {
                "record_id": "TEST-001",
                "material": "PMMA",
                "geometry_family": "thin_sheet",
                "thickness_um": 150.0,
                "oxygen_percent": 21.0,
                "pressure_kpa": 101.325,
                "gravity_regime": "microgravity",
                "transport_configuration": "opposed_flow",
                "flow_mm_s": 50.0,
                "observed_spread_rate_mm_s": 1.36,
                "training_eligible": False,
                "validation_holdout": True,
                "provenance_reference": "pytest",
            },
            {
                "record_id": "TEST-002",
                "material": "PMMA",
                "geometry_family": "thin_sheet",
                "thickness_um": 200.0,
                "oxygen_percent": 21.0,
                "pressure_kpa": 101.325,
                "gravity_regime": "microgravity",
                "transport_configuration": "opposed_flow",
                "flow_mm_s": 50.0,
                "observed_spread_rate_mm_s": 1.02,
                "training_eligible": False,
                "validation_holdout": True,
                "provenance_reference": "pytest",
            },
            {
                "record_id": "TEST-003",
                "material": "PMMA",
                "geometry_family": "thin_sheet",
                "thickness_um": 300.0,
                "oxygen_percent": 21.0,
                "pressure_kpa": 101.325,
                "gravity_regime": "microgravity",
                "transport_configuration": "opposed_flow",
                "flow_mm_s": 50.0,
                "observed_spread_rate_mm_s": 0.68,
                "training_eligible": False,
                "validation_holdout": True,
                "provenance_reference": "pytest",
            },
        ],
    }


def test_performance_endpoint_returns_200():
    response = client.post(
        ENDPOINT,
        json=candidate(),
    )

    assert (
        response.status_code
        == 200
    )


def test_synthetic_good_fit_passes_thresholds():
    data = client.post(
        ENDPOINT,
        json=candidate(),
    ).json()

    assert (
        data[
            "performance_gate_passed"
        ]
        is True
    )

    assert (
        data[
            "status"
        ]
        == "performance_thresholds_passed"
    )


def test_performance_pass_does_not_promote_validation():
    data = client.post(
        ENDPOINT,
        json=candidate(),
    ).json()

    assert (
        data[
            "external_validation_claim_allowed"
        ]
        is False
    )

    assert (
        data[
            "scientific_review_required"
        ]
        is True
    )

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


def test_large_error_fails_thresholds():
    payload = candidate()

    payload[
        "records"
    ][1][
        "observed_spread_rate_mm_s"
    ] = 2.0

    data = client.post(
        ENDPOINT,
        json=payload,
    ).json()

    assert (
        data[
            "performance_gate_passed"
        ]
        is False
    )

    assert (
        data[
            "status"
        ]
        == "performance_thresholds_failed"
    )


def test_100_mm_s_flow_cannot_reach_performance_gate():
    payload = candidate()

    for record in payload[
        "records"
    ]:
        record[
            "flow_mm_s"
        ] = 100.0

    data = client.post(
        ENDPOINT,
        json=payload,
    ).json()

    assert (
        data[
            "performance_gate_passed"
        ]
        is False
    )

    assert (
        data[
            "status"
        ]
        == "compatibility_gate_failed"
    )
