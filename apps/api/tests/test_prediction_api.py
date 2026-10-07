import pytest

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(
    app
)


def test_prediction_endpoint_exists():

    response = client.post(
        "/api/predict/fire-behavior",
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


def test_microgravity_prediction_api():

    response = client.post(
        "/api/predict/fire-behavior",
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

    assert data["decision"] == "predict"

    assert (
        data["prediction"]
        is not None
    )

    assert (
        data["prediction"]["quantity"]
        == "flame_spread_rate"
    )

    assert (
        data["prediction"]["unit"]
        == "mm/s"
    )

    assert (
        data["prediction"]["value"]
        == pytest.approx(
            204.244573 / 200.0,
            rel=1e-5,
        )
    )

    assert (
        data["model"][
            "production_ready"
        ]
        is False
    )

    assert (
        data["model"][
            "external_validation_status"
        ]
        == "not_performed"
    )


def test_normal_gravity_prediction_api():

    response = client.post(
        "/api/predict/fire-behavior",
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

    data = response.json()

    assert data["decision"] == "predict"

    assert (
        data["prediction"]["value"]
        == pytest.approx(
            213.686797 / 100.0,
            rel=1e-5,
        )
    )


def test_out_of_domain_returns_abstention():

    response = client.post(
        "/api/predict/fire-behavior",
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

    assert data["decision"] == "abstain"

    assert data["prediction"] is None

    assert (
        "thickness_below_empirical_domain"
        in data["abstention_reasons"]
    )

    assert (
        data[
            "descriptive_residual_factor"
        ]
        is None
    )


def test_unsupported_conditions_abstain():

    response = client.post(
        "/api/predict/fire-behavior",
        json={
            "material": "wood",
            "geometry": "rod",
            "thickness_um": 200.0,
            "gravity_regime": "microgravity",
            "oxygen_fraction": 0.30,
            "pressure_kpa": 80.0,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["decision"] == "abstain"

    reasons = data[
        "abstention_reasons"
    ]

    assert (
        "unsupported_material"
        in reasons
    )

    assert (
        "unsupported_geometry"
        in reasons
    )

    assert (
        "unsupported_oxygen_fraction"
        in reasons
    )

    assert (
        "unsupported_pressure"
        in reasons
    )


def test_invalid_gravity_regime_returns_422():

    response = client.post(
        "/api/predict/fire-behavior",
        json={
            "material": "PMMA",
            "geometry": "thin_sheet",
            "thickness_um": 200.0,
            "gravity_regime": "mars_gravity",
            "oxygen_fraction": 0.21,
            "pressure_kpa": 101.325,
        },
    )

    assert response.status_code == 422


def test_negative_thickness_returns_422():

    response = client.post(
        "/api/predict/fire-behavior",
        json={
            "material": "PMMA",
            "geometry": "thin_sheet",
            "thickness_um": -10.0,
            "gravity_regime": "microgravity",
            "oxygen_fraction": 0.21,
            "pressure_kpa": 101.325,
        },
    )

    assert response.status_code == 422