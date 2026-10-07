import pytest

from app.services.next_experiment_candidate import (
    NextExperimentCandidateBuilder,
)


def test_candidate_builds():

    result = (
        NextExperimentCandidateBuilder()
        .build()
    )

    assert (
        result.candidate_id
        == "NEXTEXP-COVERAGE-V0-001"
    )


def test_candidate_is_coverage_only():

    result = (
        NextExperimentCandidateBuilder()
        .build()
    )

    assert (
        result.recommendation_status
        == "coverage_candidate_only"
    )

    assert (
        result.approval_status
        == "not_approved"
    )


def test_candidate_is_around_142_um():

    result = (
        NextExperimentCandidateBuilder()
        .build()
    )

    assert (
        result.experiment_condition
        .thickness_um
        == pytest.approx(
            142.557,
            abs=0.2,
        )
    )


def test_pair_is_similar():

    result = (
        NextExperimentCandidateBuilder()
        .build()
    )

    assert (
        result.matched_pair
        .similar_thickness
        is True
    )

    assert (
        result.matched_pair
        .relative_difference
        < 0.02
    )


def test_microgravity_gap():

    result = (
        NextExperimentCandidateBuilder()
        .build()
    )

    micro = next(
        item
        for item
        in result.gravity_candidates
        if (
            item.gravity_regime
            == "microgravity"
        )
    )

    assert (
        100.0
        < micro.gap_left_um
        < 105.0
    )

    assert (
        198.0
        < micro.gap_right_um
        < 205.0
    )


def test_normal_gravity_gap():

    result = (
        NextExperimentCandidateBuilder()
        .build()
    )

    normal = next(
        item
        for item
        in result.gravity_candidates
        if (
            item.gravity_regime
            == "normal_gravity"
        )
    )

    assert (
        99.0
        < normal.gap_left_um
        < 102.0
    )

    assert (
        198.0
        < normal.gap_right_um
        < 203.0
    )


def test_fixed_supported_conditions():

    result = (
        NextExperimentCandidateBuilder()
        .build()
    )

    condition = (
        result.experiment_condition
    )

    assert (
        condition.material
        == "PMMA"
    )

    assert (
        condition.geometry
        == "thin_sheet"
    )

    assert (
        condition.oxygen_fraction
        == pytest.approx(
            0.21
        )
    )

    assert (
        condition.pressure_kpa
        == pytest.approx(
            101.325
        )
    )


def test_not_production_ready():

    result = (
        NextExperimentCandidateBuilder()
        .build()
    )

    assert (
        result.production_ready
        is False
    )