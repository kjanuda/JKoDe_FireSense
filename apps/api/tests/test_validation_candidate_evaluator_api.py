import pytest

from fastapi.testclient import (
    TestClient,
)

from app.main import app


client = TestClient(
    app,
)

ENDPOINT = (
    "/api/evidence/"
    "validation-candidate/evaluate"
)


def exact_candidate():
    return {
        "dataset_id": (
            "TEST-SYNTHETIC-"
            "VALIDATION-V0"
        ),
        "dataset_version": "test-v0",
        "source": {
            "source_id": (
                "TEST-SYNTHETIC-SOURCE"
            ),
            "source_title": (
                "Synthetic software test fixture"
            ),
            "provenance_reference": (
                "pytest-only-not-scientific-evidence"
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
                "record_id": "TEST-MG-001",
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
                "provenance_reference": (
                    "synthetic-test-row-001"
                ),
            },
            {
                "record_id": "TEST-MG-002",
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
                "provenance_reference": (
                    "synthetic-test-row-002"
                ),
            },
            {
                "record_id": "TEST-MG-003",
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
                "provenance_reference": (
                    "synthetic-test-row-003"
                ),
            },
        ],
    }


def evaluate(
    payload,
):
    return client.post(
        ENDPOINT,
        json=payload,
    )


def test_exact_candidate_passes_compatibility_gate():
    response = evaluate(
        exact_candidate()
    )

    assert (
        response.status_code
        == 200
    )

    data = response.json()

    assert (
        data[
            "classification"
        ]
        == (
            "compatible_independent_"
            "validation_candidate"
        )
    )

    assert (
        data[
            "direct_validation_gate_passed"
        ]
        is True
    )

    assert (
        data[
            "submitted_point_count"
        ]
        == 3
    )

    assert (
        data[
            "evaluated_point_count"
        ]
        == 3
    )

    assert (
        data[
            "blocked_point_count"
        ]
        == 0
    )


def test_gate_pass_does_not_authorize_validation_claim():
    data = evaluate(
        exact_candidate()
    ).json()

    assert (
        data[
            "external_validation_claim_allowed"
        ]
        is False
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

    assert (
        data[
            "performance_acceptance_status"
        ]
        == "thresholds_not_yet_frozen"
    )


def test_metrics_are_computed_for_holdout():
    data = evaluate(
        exact_candidate()
    ).json()

    metrics = data[
        "metrics"
    ]

    assert metrics is not None

    assert (
        metrics[
            "evaluated_point_count"
        ]
        == 3
    )

    assert (
        metrics[
            "mae_mm_s"
        ]
        >= 0
    )

    assert (
        metrics[
            "rmse_mm_s"
        ]
        >= 0
    )

    assert (
        metrics[
            "max_absolute_error_mm_s"
        ]
        >= 0
    )

    assert (
        data[
            "metrics_role"
        ]
        == "validation_candidate_metrics"
    )


def test_200_um_prediction_uses_frozen_baseline():
    data = evaluate(
        exact_candidate()
    ).json()

    row = next(
        item
        for item
        in data[
            "evaluations"
        ]
        if (
            item[
                "record_id"
            ]
            == "TEST-MG-002"
        )
    )

    assert (
        row[
            "predicted_spread_rate_mm_s"
        ]
        == pytest.approx(
            204.244573
            / 200.0,
            rel=1e-5,
        )
    )


def test_100_mm_s_flow_is_comparison_only():
    payload = exact_candidate()

    for record in payload[
        "records"
    ]:
        record[
            "flow_mm_s"
        ] = 100.0

    data = evaluate(
        payload
    ).json()

    assert (
        data[
            "direct_validation_gate_passed"
        ]
        is False
    )

    assert (
        data[
            "classification"
        ]
        == (
            "independent_external_"
            "comparison_only"
        )
    )

    checks = {
        item[
            "check_id"
        ]: item
        for item
        in data[
            "gate_checks"
        ]
    }

    assert (
        checks[
            "microgravity_transport"
        ][
            "passed"
        ]
        is False
    )


def test_measurement_mismatch_without_cross_calibration_fails():
    payload = exact_candidate()

    payload[
        "source"
    ][
        "measurement_definition_matches"
    ] = False

    payload[
        "source"
    ][
        "cross_calibration_available"
    ] = False

    data = evaluate(
        payload
    ).json()

    assert (
        data[
            "direct_validation_gate_passed"
        ]
        is False
    )

    checks = {
        item[
            "check_id"
        ]: item
        for item
        in data[
            "gate_checks"
        ]
    }

    assert (
        checks[
            "measurement_definition"
        ][
            "passed"
        ]
        is False
    )


def test_cross_calibration_can_satisfy_measurement_gate():
    payload = exact_candidate()

    payload[
        "source"
    ][
        "measurement_definition_matches"
    ] = False

    payload[
        "source"
    ][
        "cross_calibration_available"
    ] = True

    data = evaluate(
        payload
    ).json()

    checks = {
        item[
            "check_id"
        ]: item
        for item
        in data[
            "gate_checks"
        ]
    }

    assert (
        checks[
            "measurement_definition"
        ][
            "passed"
        ]
        is True
    )

    assert (
        data[
            "direct_validation_gate_passed"
        ]
        is True
    )


def test_training_eligible_row_breaks_holdout_gate():
    payload = exact_candidate()

    payload[
        "records"
    ][0][
        "training_eligible"
    ] = True

    data = evaluate(
        payload
    ).json()

    assert (
        data[
            "direct_validation_gate_passed"
        ]
        is False
    )

    checks = {
        item[
            "check_id"
        ]: item
        for item
        in data[
            "gate_checks"
        ]
    }

    assert (
        checks[
            "holdout_integrity"
        ][
            "passed"
        ]
        is False
    )


def test_fewer_than_three_points_is_insufficient_scope():
    payload = exact_candidate()

    payload[
        "records"
    ] = payload[
        "records"
    ][:2]

    data = evaluate(
        payload
    ).json()

    assert (
        data[
            "classification"
        ]
        == "insufficient_validation_scope"
    )

    assert (
        data[
            "direct_validation_gate_passed"
        ]
        is False
    )


def test_outside_model_domain_is_blocked():
    payload = exact_candidate()

    payload[
        "records"
    ][0][
        "thickness_um"
    ] = 50.0

    data = evaluate(
        payload
    ).json()

    assert (
        data[
            "classification"
        ]
        == "outside_firesense_v0_domain"
    )

    assert (
        data[
            "blocked_point_count"
        ]
        == 1
    )

    assert (
        data[
            "direct_validation_gate_passed"
        ]
        is False
    )


def test_non_independent_source_is_rejected():
    payload = exact_candidate()

    payload[
        "source"
    ][
        "independent_experimental_campaign"
    ] = False

    data = evaluate(
        payload
    ).json()

    assert (
        data[
            "classification"
        ]
        == "non_independent_rejected"
    )

    assert (
        data[
            "direct_validation_gate_passed"
        ]
        is False
    )
