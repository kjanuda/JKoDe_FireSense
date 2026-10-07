from fastapi.testclient import TestClient

from app.main import app


client = TestClient(
    app,
)

ENDPOINT = (
    "/api/evidence/figure-2-22"
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


def test_dataset_identity_and_integrity():
    data = get_data()

    assert (
        data[
            "dataset_name"
        ]
        == "figure_2_22_comparison_dataset_v0"
    )

    assert (
        data[
            "dataset_version"
        ]
        == "v0"
    )

    assert (
        data[
            "figure_ref"
        ]
        == "2.22"
    )

    assert (
        data[
            "dataset_sha256"
        ]
        == (
            "ee7e7d54b57e2bdcbd9dd4eddbcdf8b9"
            "ad88b9924fcee31a4ad7ddac3aff2a9d"
        )
    )

    assert (
        data[
            "dataset_sha256_verified"
        ]
        is True
    )


def test_dataset_is_comparison_only():
    data = get_data()

    assert (
        data[
            "purpose"
        ]
        == "comparison_only"
    )

    assert (
        data[
            "scientific_status"
        ]
        == (
            "comparison_evidence_not_"
            "independent_external_validation"
        )
    )

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


def test_dataset_contains_33_experimental_points():
    data = get_data()

    assert (
        data[
            "experimental_point_count"
        ]
        == 33
    )

    assert len(
        data[
            "records"
        ]
    ) == 33

    assert (
        data[
            "theoretical_curves_included"
        ]
        is False
    )


def test_series_counts_are_frozen():
    data = get_data()

    assert (
        data[
            "series_counts"
        ]
        == {
            "astra": 1,
            "bass": 4,
            "fernandez_pello_williams": 14,
            "mrc": 2,
            "nasa": 3,
            "ridout": 4,
            "vcf": 5,
        }
    )


def test_gravity_context_is_not_overclaimed():
    data = get_data()

    assert (
        data[
            "gravity_context_counts"
        ]
        == {
            "microgravity": 4,
            "normal_gravity": 4,
            "unresolved": 25,
        }
    )


def test_every_row_preserves_scientific_guardrails():
    data = get_data()

    for record in data[
        "records"
    ]:
        assert (
            record[
                "evidence_type"
            ]
            == "experimental"
        )

        assert (
            record[
                "training_eligible"
            ]
            is False
        )

        assert (
            record[
                "independent_validation_eligible"
            ]
            is False
        )

        assert (
            record[
                "evaluation_role"
            ]
            == "comparison_only"
        )


def test_duplicate_linkage_summary():
    data = get_data()

    counts = data[
        "duplicate_linkage_class_counts"
    ]

    assert (
        counts[
            "strong_duplicate_candidate"
        ]
        == 5
    )

    assert (
        counts[
            "moderate_duplicate_candidate"
        ]
        == 2
    )

    assert (
        counts[
            "possible_duplicate_candidate"
        ]
        == 1
    )
