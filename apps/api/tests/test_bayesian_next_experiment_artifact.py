import json
import math

import pytest

from app.core.paths import CURATED_DATA_DIR


ARTIFACT_PATH = (
    CURATED_DATA_DIR
    / "thin_sheet"
    / "models"
    / "bayesian_next_experiment_candidate_v0.json"
)


@pytest.fixture
def artifact():
    assert ARTIFACT_PATH.exists()

    return json.loads(
        ARTIFACT_PATH.read_text(
            encoding="utf-8"
        )
    )


def test_candidate_status_and_guardrails(
    artifact,
):
    assert (
        artifact["status"]
        == "bayesian_next_experiment_candidate_generated"
    )

    assert (
        artifact["recommendation_status"]
        == "bayesian_candidate_only"
    )

    assert (
        artifact["approval_status"]
        == "not_approved"
    )

    assert (
        artifact["production_ready"]
        is False
    )


def test_candidate_uses_frozen_figure_221_evidence(
    artifact,
):
    assert (
        artifact["dataset_version"]
        == "v0"
    )

    assert (
        artifact["canonical_evidence_figure"]
        == "2.21"
    )


def test_acquisition_is_botorch_posterior_sd(
    artifact,
):
    acquisition = artifact[
        "acquisition"
    ]

    assert (
        acquisition["library"]
        == "BoTorch"
    )

    assert (
        acquisition[
            "individual_acquisition"
        ]
        == "PosteriorStandardDeviation"
    )


def test_common_domain_is_intersection(
    artifact,
):
    search = artifact[
        "search_domain"
    ]

    mg_min, mg_max = (
        search[
            "microgravity_domain_um"
        ]
    )

    ng_min, ng_max = (
        search[
            "normal_gravity_domain_um"
        ]
    )

    common_min, common_max = (
        search[
            "common_domain_um"
        ]
    )

    assert common_min == max(
        mg_min,
        ng_min,
    )

    assert common_max == min(
        mg_max,
        ng_max,
    )


def test_candidate_is_inside_common_domain(
    artifact,
):
    candidate = float(
        artifact[
            "candidate"
        ][
            "thickness_um"
        ]
    )

    common_min, common_max = (
        artifact[
            "search_domain"
        ][
            "common_domain_um"
        ]
    )

    assert (
        common_min
        < candidate
        < common_max
    )


def test_candidate_converges_near_143_um(
    artifact,
):
    candidate = float(
        artifact[
            "candidate"
        ][
            "thickness_um"
        ]
    )

    assert (
        140.0
        < candidate
        < 146.0
    )


def test_joint_sd_matches_quadrature(
    artifact,
):
    candidate = artifact[
        "candidate"
    ]

    mg_sd = float(
        candidate[
            "microgravity"
        ][
            "posterior_sd_log_residual"
        ]
    )

    ng_sd = float(
        candidate[
            "normal_gravity"
        ][
            "posterior_sd_log_residual"
        ]
    )

    joint_sd = float(
        candidate[
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


def test_uncertainty_factor_matches_joint_sd(
    artifact,
):
    candidate = artifact[
        "candidate"
    ]

    joint_sd = float(
        candidate[
            "matched_pair_joint_sd_log"
        ]
    )

    factor = float(
        candidate[
            "one_sd_ratio_uncertainty_factor"
        ]
    )

    assert math.isclose(
        factor,
        math.exp(joint_sd),
        rel_tol=1e-10,
        abs_tol=1e-12,
    )


def test_predicted_ratio_is_consistent(
    artifact,
):
    candidate = artifact[
        "candidate"
    ]

    mg_prediction = float(
        candidate[
            "microgravity"
        ][
            "gp_corrected_prediction_mm_s"
        ]
    )

    ng_prediction = float(
        candidate[
            "normal_gravity"
        ][
            "gp_corrected_prediction_mm_s"
        ]
    )

    ratio = float(
        candidate[
            "predicted_mg_to_ng_spread_ratio"
        ]
    )

    assert math.isclose(
        ratio,
        mg_prediction
        / ng_prediction,
        rel_tol=1e-10,
        abs_tol=1e-12,
    )


def test_grid_and_external_validation_state(
    artifact,
):
    grid = artifact[
        "acquisition_grid"
    ]

    assert len(grid) == 1001

    best = max(
        grid,
        key=lambda point: float(
            point[
                "matched_pair_joint_sd_log"
            ]
        ),
    )

    candidate_thickness = float(
        artifact[
            "candidate"
        ][
            "thickness_um"
        ]
    )

    assert math.isclose(
        float(
            best[
                "thickness_um"
            ]
        ),
        candidate_thickness,
        rel_tol=1e-12,
        abs_tol=1e-12,
    )

    assert (
        artifact[
            "external_validation"
        ]
        == "not_performed"
    )