from fastapi.testclient import (
    TestClient,
)

from app.main import app


client = TestClient(
    app,
)

ENDPOINT = (
    "/api/evidence/"
    "validation-candidate/uncertainty"
)


def candidate():
    return {
        "dataset_id": (
            "TEST-UNCERTAINTY-V0"
        ),

        "dataset_version": "test-v0",

        "source": {
            "source_id": (
                "TEST-INDEPENDENT-SOURCE"
            ),

            "source_title": (
                "Synthetic uncertainty fixture"
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
                "record_id": "U-001",
                "material": "PMMA",
                "geometry_family": "thin_sheet",
                "thickness_um": 150.0,
                "oxygen_percent": 21.0,
                "pressure_kpa": 101.325,
                "gravity_regime": "microgravity",
                "transport_configuration": "opposed_flow",
                "flow_mm_s": 50.0,
                "observed_spread_rate_mm_s": 1.36,
                "experimental_uncertainty_mm_s": 0.05,
                "digitization_uncertainty_mm_s": 0.002,
                "training_eligible": False,
                "validation_holdout": True,
                "provenance_reference": "pytest-1",
            },
            {
                "record_id": "U-002",
                "material": "PMMA",
                "geometry_family": "thin_sheet",
                "thickness_um": 200.0,
                "oxygen_percent": 21.0,
                "pressure_kpa": 101.325,
                "gravity_regime": "microgravity",
                "transport_configuration": "opposed_flow",
                "flow_mm_s": 50.0,
                "observed_spread_rate_mm_s": 1.02,
                "experimental_uncertainty_mm_s": 0.05,
                "digitization_uncertainty_mm_s": 0.002,
                "training_eligible": False,
                "validation_holdout": True,
                "provenance_reference": "pytest-2",
            },
            {
                "record_id": "U-003",
                "material": "PMMA",
                "geometry_family": "thin_sheet",
                "thickness_um": 300.0,
                "oxygen_percent": 21.0,
                "pressure_kpa": 101.325,
                "gravity_regime": "microgravity",
                "transport_configuration": "opposed_flow",
                "flow_mm_s": 50.0,
                "observed_spread_rate_mm_s": 0.68,
                "experimental_uncertainty_mm_s": 0.05,
                "digitization_uncertainty_mm_s": 0.002,
                "training_eligible": False,
                "validation_holdout": True,
                "provenance_reference": "pytest-3",
            },
        ],
    }


def request_payload():
    return {
        "candidate": candidate(),

        "experimental_uncertainty_kind": (
            "standard_deviation"
        ),

        "experimental_uncertainty_confidence_level_percent": None,

        "digitization_uncertainty_kind": (
            "absolute_bound"
        ),
    }


def test_uncertainty_endpoint_returns_200():
    response = client.post(
        ENDPOINT,
        json=request_payload(),
    )

    assert response.status_code == 200


def test_uncertainty_categories_remain_separate():
    data = client.post(
        ENDPOINT,
        json=request_payload(),
    ).json()

    assert (
        data[
            "uncertainty_categories_separate"
        ]
        is True
    )

    assert (
        data[
            "rows_with_experimental_uncertainty"
        ]
        == 3
    )

    assert (
        data[
            "rows_with_digitization_uncertainty"
        ]
        == 3
    )


def test_current_model_has_no_calibrated_interval():
    data = client.post(
        ENDPOINT,
        json=request_payload(),
    ).json()

    assert (
        data[
            "calibrated_prediction_interval_available"
        ]
        is False
    )

    assert (
        data[
            "coverage_verification_passed"
        ]
        is False
    )

    assert (
        data[
            "uncertainty_readiness_status"
        ]
        == (
            "blocked_no_calibrated_"
            "prediction_interval"
        )
    )


def test_unspecified_experimental_semantics_blocks_readiness():
    payload = request_payload()

    payload[
        "experimental_uncertainty_kind"
    ] = "source_reported_unspecified"

    data = client.post(
        ENDPOINT,
        json=payload,
    ).json()

    assert (
        data[
            "uncertainty_readiness_status"
        ]
        == (
            "blocked_experimental_"
            "uncertainty_semantics"
        )
    )

    assert (
        data[
            "coverage_verification_passed"
        ]
        is False
    )


def test_missing_experimental_uncertainty_blocks_readiness():
    payload = request_payload()

    payload[
        "candidate"
    ][
        "records"
    ][0][
        "experimental_uncertainty_mm_s"
    ] = None

    data = client.post(
        ENDPOINT,
        json=payload,
    ).json()

    assert (
        data[
            "experimental_uncertainty_completeness_fraction"
        ]
        < 1.0
    )

    assert (
        data[
            "uncertainty_readiness_status"
        ]
        == (
            "blocked_incomplete_"
            "experimental_uncertainty"
        )
    )
