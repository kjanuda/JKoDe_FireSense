import math

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def get_response():
    response = client.get(
        "/api/recommendations/next-experiment"
    )

    assert response.status_code == 200

    return response.json()


def test_next_experiment_endpoint_returns_200():
    response = client.get(
        "/api/recommendations/next-experiment"
    )

    assert response.status_code == 200


def test_candidate_identity_and_status():
    data = get_response()

    assert (
        data["candidate_id"]
        == "NEXTEXP-BAYES-V0-001"
    )

    assert (
        data["decision_status"]
        == "research_priority_candidate"
    )

    assert (
        data["recommendation_status"]
        == "bayesian_candidate_only"
    )

    assert (
        data["approval_status"]
        == "not_approved"
    )

    assert (
        data["production_ready"]
        is False
    )


def test_selected_thickness_is_expected():
    data = get_response()

    assert math.isclose(
        data["thickness_um"],
        143.3092934322342,
        rel_tol=1e-10,
        abs_tol=1e-10,
    )


def test_coverage_bayesian_agreement():
    data = get_response()

    agreement = data[
        "agreement"
    ]

    assert (
        agreement[
            "within_one_percent"
        ]
        is True
    )

    assert (
        agreement[
            "relative_difference_percent"
        ]
        < 1.0
    )

    expected_difference = abs(
        agreement[
            "bayesian_candidate_um"
        ]
        -
        agreement[
            "coverage_candidate_um"
        ]
    )

    assert math.isclose(
        agreement[
            "absolute_difference_um"
        ],
        expected_difference,
        rel_tol=1e-12,
        abs_tol=1e-12,
    )


def test_experiment_family_is_supported_scope():
    data = get_response()

    family = data[
        "experiment_family"
    ]

    assert (
        family["material"]
        == "PMMA"
    )

    assert (
        family["geometry_family"]
        == "thin_sheet"
    )

    assert math.isclose(
        family["oxygen_percent"],
        21.0,
    )

    assert math.isclose(
        family["pressure_kpa"],
        101.325,
    )

    assert (
        family["gravity_regimes"]
        == [
            "microgravity",
            "normal_gravity",
        ]
    )


def test_predicted_spread_rates_are_positive():
    data = get_response()

    assert (
        data[
            "microgravity"
        ][
            "predicted_spread_rate_mm_s"
        ]
        > 0.0
    )

    assert (
        data[
            "normal_gravity"
        ][
            "predicted_spread_rate_mm_s"
        ]
        > 0.0
    )


def test_joint_uncertainty_is_consistent():
    data = get_response()

    mg_sd = float(
        data[
            "microgravity"
        ][
            "posterior_sd_log_residual"
        ]
    )

    ng_sd = float(
        data[
            "normal_gravity"
        ][
            "posterior_sd_log_residual"
        ]
    )

    joint_sd = float(
        data[
            "joint_uncertainty"
        ][
            "matched_pair_joint_sd_log"
        ]
    )

    expected = math.sqrt(
        mg_sd**2
        + ng_sd**2
    )

    assert math.isclose(
        joint_sd,
        expected,
        rel_tol=1e-10,
        abs_tol=1e-12,
    )


def test_uncertainty_factor_is_consistent():
    data = get_response()

    joint = data[
        "joint_uncertainty"
    ]

    expected = math.exp(
        joint[
            "matched_pair_joint_sd_log"
        ]
    )

    assert math.isclose(
        joint[
            "one_sd_ratio_uncertainty_factor"
        ],
        expected,
        rel_tol=1e-10,
        abs_tol=1e-12,
    )


def test_evidence_and_integrity_state():
    data = get_response()

    evidence = data[
        "evidence"
    ]

    assert (
        evidence["source_id"]
        == "SRC-NASA-20210011385"
    )

    assert (
        evidence["figure"]
        == "2.21"
    )

    assert (
        evidence["dataset_version"]
        == "v0"
    )

    assert (
        evidence[
            "shared_canonical_evidence"
        ]
        is True
    )

    assert (
        evidence[
            "independent_validation"
        ]
        is False
    )

    assert (
        evidence[
            "external_validation"
        ]
        == "not_performed"
    )

    integrity = data[
        "integrity"
    ]

    assert (
        integrity[
            "dataset_sha256_verified"
        ]
        is True
    )

    assert (
        integrity[
            "coverage_artifact_sha256_verified"
        ]
        is True
    )

    assert (
        integrity[
            "bayesian_artifact_sha256_verified"
        ]
        is True
    )


def test_scientific_guardrails_are_exposed():
    data = get_response()

    guardrails = " ".join(
        data[
            "scientific_guardrails"
        ]
    ).lower()

    assert (
        "not an approved experiment"
        in guardrails
    )

    assert (
        "not an external validation"
        in guardrails
    )

    assert (
        "figure 2.21"
        in guardrails
    )

    assert (
        "not externally calibrated"
        in guardrails
    )

    assert (
        len(
            data[
                "required_before_experiment_approval"
            ]
        )
        >= 4
    )
def test_recommendation_text_has_no_spacing_regressions():
    data = get_response()

    why_selected = data["why_selected"]

    assert (
        "shared empirical thickness domain"
        in why_selected
    )

    assert (
        "sharedempirical"
        not in why_selected
    )

    guardrails = " ".join(
        data["scientific_guardrails"]
    )

    assert (
        "Digitization uncertainty and "
        "experimental uncertainty"
        in guardrails
    )

    assert (
        "Digitizationuncertainty"
        not in guardrails
    )
