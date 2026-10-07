import json
from pathlib import Path

import pytest

from app.core.paths import (
    CURATED_DATA_DIR,
)


GP_PATH = (
    CURATED_DATA_DIR
    / "thin_sheet"
    / "models"
    / "physics_informed_gp_v0.json"
)


@pytest.fixture
def gp_artifact():

    assert GP_PATH.exists()

    return json.loads(
        GP_PATH.read_text(
            encoding="utf-8"
        )
    )


def test_gp_artifact_status(
    gp_artifact,
):

    assert (
        gp_artifact["status"]
        == "physics_informed_gp_fitted"
    )

    assert (
        gp_artifact[
            "production_ready"
        ]
        is False
    )

    assert (
        gp_artifact[
            "external_validation"
        ]
        == "not_performed"
    )


def test_gp_uses_figure_221_only(
    gp_artifact,
):

    assert (
        gp_artifact[
            "canonical_evidence_figure"
        ]
        == "2.21"
    )


def test_group_counts(
    gp_artifact,
):

    groups = (
        gp_artifact[
            "groups"
        ]
    )

    assert (
        groups[
            "microgravity"
        ][
            "record_count"
        ]
        == 4
    )

    assert (
        groups[
            "normal_gravity"
        ][
            "record_count"
        ]
        == 9
    )


def test_microgravity_peak_inside_domain(
    gp_artifact,
):

    group = (
        gp_artifact[
            "groups"
        ][
            "microgravity"
        ]
    )

    peak = float(
        group[
            "uncertainty_peak"
        ][
            "thickness_um"
        ]
    )

    domain = (
        group[
            "domain"
        ]
    )

    assert (
        domain[
            "thickness_um_min"
        ]
        < peak
        < domain[
            "thickness_um_max"
        ]
    )


def test_normal_gravity_peak_inside_domain(
    gp_artifact,
):

    group = (
        gp_artifact[
            "groups"
        ][
            "normal_gravity"
        ]
    )

    peak = float(
        group[
            "uncertainty_peak"
        ][
            "thickness_um"
        ]
    )

    domain = (
        group[
            "domain"
        ]
    )

    assert (
        domain[
            "thickness_um_min"
        ]
        < peak
        < domain[
            "thickness_um_max"
        ]
    )


def test_microgravity_gp_agrees_with_coverage_region(
    gp_artifact,
):

    peak = float(
        gp_artifact[
            "groups"
        ][
            "microgravity"
        ][
            "uncertainty_peak"
        ][
            "thickness_um"
        ]
    )

    assert (
        135.0
        < peak
        < 150.0
    )


def test_normal_gravity_gp_peak_is_high_thickness(
    gp_artifact,
):

    peak = float(
        gp_artifact[
            "groups"
        ][
            "normal_gravity"
        ][
            "uncertainty_peak"
        ][
            "thickness_um"
        ]
    )

    assert (
        500.0
        < peak
        < 650.0
    )


def test_posterior_grids_have_501_points(
    gp_artifact,
):

    for group_name in (
        "microgravity",
        "normal_gravity",
    ):

        grid = (
            gp_artifact[
                "groups"
            ][
                group_name
            ][
                "posterior_grid"
            ]
        )

        assert (
            len(grid)
            == 501
        )


def test_all_posterior_sd_values_are_nonnegative(
    gp_artifact,
):

    for group_name in (
        "microgravity",
        "normal_gravity",
    ):

        grid = (
            gp_artifact[
                "groups"
            ][
                group_name
            ][
                "posterior_grid"
            ]
        )

        assert all(
            float(
                point[
                    "posterior_sd_log_residual"
                ]
            )
            >= 0.0
            for point
            in grid
        )


def test_no_external_validation_claim(
    gp_artifact,
):

    guardrails = " ".join(
        gp_artifact[
            "scientific_guardrails"
        ]
    ).lower()

    assert (
        "cross-study"
        in guardrails
    )

    assert (
        gp_artifact[
            "external_validation"
        ]
        == "not_performed"
    )