import pytest

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(
    app
)


ENDPOINT = (
    "/api/predict/"
    "fire-behavior/explain"
)


def test_microgravity_explanation():

    response = client.post(
        ENDPOINT,
        json={
            "material": "PMMA",
            "geometry": "thin_sheet",
            "thickness_um": 200.0,
            "gravity_regime": "microgravity",
            "oxygen_fraction": 0.21,
            "pressure_kpa": 101.325,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["result"]["decision"]
        == "predict"
    )

    trace = data[
        "evidence_trace"
    ]

    assert (
        trace[
            "canonical_figure_ref"
        ]
        == "2.21"
    )

    assert (
        trace[
            "dataset_integrity"
        ][
            "integrity_verified"
        ]
        is True
    )

    assert (
        trace[
            "coefficient_derivation"
        ][
            "contributing_record_count"
        ]
        == 4
    )

    assert (
        trace[
            "coefficient_derivation"
        ][
            "coefficient_k"
        ]
        == pytest.approx(
            204.24457277066125,
            rel=1e-10,
        )
    )


def test_normal_gravity_uses_nine_records():

    response = client.post(
        ENDPOINT,
        json={
            "material": "PMMA",
            "geometry": "thin_sheet",
            "thickness_um": 100.0,
            "gravity_regime": "normal_gravity",
            "oxygen_fraction": 0.21,
            "pressure_kpa": 101.325,
        },
    )

    assert response.status_code == 200

    trace = (
        response.json()[
            "evidence_trace"
        ]
    )

    assert (
        trace[
            "coefficient_derivation"
        ][
            "contributing_record_count"
        ]
        == 9
    )


def test_every_contributing_record_is_figure_221():

    response = client.post(
        ENDPOINT,
        json={
            "material": "PMMA",
            "geometry": "thin_sheet",
            "thickness_um": 200.0,
            "gravity_regime": "microgravity",
            "oxygen_fraction": 0.21,
            "pressure_kpa": 101.325,
        },
    )

    records = (
        response.json()[
            "evidence_trace"
        ][
            "contributing_evidence_records"
        ]
    )

    assert len(records) == 4

    assert all(
        record["figure_ref"]
        == "2.21"
        for record
        in records
    )


def test_nearest_microgravity_record():

    response = client.post(
        ENDPOINT,
        json={
            "material": "PMMA",
            "geometry": "thin_sheet",
            "thickness_um": 200.0,
            "gravity_regime": "microgravity",
            "oxygen_fraction": 0.21,
            "pressure_kpa": 101.325,
        },
    )

    nearest = (
        response.json()[
            "evidence_trace"
        ][
            "nearest_evidence_records"
        ]
    )

    assert len(nearest) == 3

    assert (
        nearest[0][
            "record_id"
        ]
        == "TS-F221-MG-002"
    )


def test_abstention_still_returns_evidence_trace():

    response = client.post(
        ENDPOINT,
        json={
            "material": "PMMA",
            "geometry": "thin_sheet",
            "thickness_um": 50.0,
            "gravity_regime": "microgravity",
            "oxygen_fraction": 0.21,
            "pressure_kpa": 101.325,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["result"][
            "decision"
        ]
        == "abstain"
    )

    assert (
        "thickness_below_empirical_domain"
        in data["result"][
            "abstention_reasons"
        ]
    )

    assert (
        data[
            "evidence_trace"
        ][
            "dataset_integrity"
        ][
            "integrity_verified"
        ]
        is True
    )


def test_explanation_is_not_production_ready():

    response = client.post(
        ENDPOINT,
        json={
            "material": "PMMA",
            "geometry": "thin_sheet",
            "thickness_um": 200.0,
            "gravity_regime": "microgravity",
            "oxygen_fraction": 0.21,
            "pressure_kpa": 101.325,
        },
    )

    trace = (
        response.json()[
            "evidence_trace"
        ]
    )

    assert (
        trace[
            "production_ready"
        ]
        is False
    )

    assert (
        trace[
            "external_validation_status"
        ]
        == "not_performed"
    )