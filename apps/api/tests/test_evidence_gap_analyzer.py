from app.services.evidence_gap_analyzer import (
    EvidenceGapAnalyzer,
)


def test_gap_map_uses_13_records():

    analyzer = (
        EvidenceGapAnalyzer()
    )

    result = analyzer.build()

    total = sum(
        group[
            "record_count"
        ]
        for group
        in result[
            "groups"
        ].values()
    )

    assert total == 13


def test_group_counts_are_correct():

    result = (
        EvidenceGapAnalyzer()
        .build()
    )

    assert (
        result[
            "groups"
        ][
            "microgravity"
        ][
            "record_count"
        ]
        == 4
    )

    assert (
        result[
            "groups"
        ][
            "normal_gravity"
        ][
            "record_count"
        ]
        == 9
    )


def test_microgravity_candidate_is_internal():

    result = (
        EvidenceGapAnalyzer()
        .build()
    )

    group = (
        result[
            "groups"
        ][
            "microgravity"
        ]
    )

    candidate = float(
        group[
            "coverage_candidate"
        ][
            "thickness_um"
        ]
    )

    assert (
        group[
            "empirical_domain_um"
        ][
            "min"
        ]
        < candidate
        < group[
            "empirical_domain_um"
        ][
            "max"
        ]
    )


def test_normal_gravity_candidate_is_internal():

    result = (
        EvidenceGapAnalyzer()
        .build()
    )

    group = (
        result[
            "groups"
        ][
            "normal_gravity"
        ]
    )

    candidate = float(
        group[
            "coverage_candidate"
        ][
            "thickness_um"
        ]
    )

    assert (
        group[
            "empirical_domain_um"
        ][
            "min"
        ]
        < candidate
        < group[
            "empirical_domain_um"
        ][
            "max"
        ]
    )


def test_microgravity_largest_gap_is_around_100_to_200_um():

    result = (
        EvidenceGapAnalyzer()
        .build()
    )

    gap = (
        result[
            "groups"
        ][
            "microgravity"
        ][
            "largest_internal_gap"
        ]
    )

    assert (
        95.0
        < gap[
            "left_thickness_um"
        ]
        < 110.0
    )

    assert (
        190.0
        < gap[
            "right_thickness_um"
        ]
        < 210.0
    )


def test_normal_gravity_largest_gap_is_around_100_to_200_um():

    result = (
        EvidenceGapAnalyzer()
        .build()
    )

    gap = (
        result[
            "groups"
        ][
            "normal_gravity"
        ][
            "largest_internal_gap"
        ]
    )

    assert (
        95.0
        < gap[
            "left_thickness_um"
        ]
        < 110.0
    )

    assert (
        190.0
        < gap[
            "right_thickness_um"
        ]
        < 210.0
    )


def test_candidates_are_around_140_um():

    result = (
        EvidenceGapAnalyzer()
        .build()
    )

    micro = float(
        result[
            "groups"
        ][
            "microgravity"
        ][
            "coverage_candidate"
        ][
            "thickness_um"
        ]
    )

    normal = float(
        result[
            "groups"
        ][
            "normal_gravity"
        ][
            "coverage_candidate"
        ][
            "thickness_um"
        ]
    )

    assert (
        135.0
        < micro
        < 150.0
    )

    assert (
        135.0
        < normal
        < 150.0
    )


def test_paired_candidate_hint_is_true():

    result = (
        EvidenceGapAnalyzer()
        .build()
    )

    assert (
        result[
            "paired_candidate_hint"
        ][
            "similar_thickness_candidate"
        ]
        is True
    )


def test_gap_map_does_not_use_external_data():

    result = (
        EvidenceGapAnalyzer()
        .build()
    )

    policy = (
        result[
            "scope_policy"
        ]
    )

    assert (
        policy[
            "uses_external_figure_2_22_data"
        ]
        is False
    )

    assert (
        policy[
            "uses_theoretical_curves"
        ]
        is False
    )

    assert (
        policy[
            "uses_model_uncertainty"
        ]
        is False
    )


def test_status():

    result = (
        EvidenceGapAnalyzer()
        .build()
    )

    assert (
        result[
            "status"
        ]
        ==
        "empirical_coverage_gap_map_complete"
    )