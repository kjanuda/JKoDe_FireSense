import pytest

from app.schemas.prediction import (
    FireBehaviorPredictionRequest,
)

from app.services.physics_baseline_predictor import (
    PhysicsBaselinePredictor,
)


@pytest.fixture
def predictor():
    return PhysicsBaselinePredictor()


def test_microgravity_valid_prediction(
    predictor,
):

    request = (
        FireBehaviorPredictionRequest(
            material="PMMA",
            geometry="thin_sheet",
            thickness_um=200.0,
            gravity_regime="microgravity",
            oxygen_fraction=0.21,
            pressure_kpa=101.325,
        )
    )

    response = predictor.predict(
        request
    )

    assert (
        response.decision
        == "predict"
    )

    assert (
        response.prediction
        is not None
    )

    assert (
        response.prediction.value
        == pytest.approx(
            204.244573 / 200.0,
            rel=1e-5,
        )
    )

    assert (
        response.model.production_ready
        is False
    )

    assert (
        response.model.external_validation_status
        == "not_performed"
    )


def test_normal_gravity_valid_prediction(
    predictor,
):

    request = (
        FireBehaviorPredictionRequest(
            material="PMMA",
            geometry="thin_sheet",
            thickness_um=100.0,
            gravity_regime="normal_gravity",
            oxygen_fraction=0.21,
            pressure_kpa=101.325,
        )
    )

    response = predictor.predict(
        request
    )

    assert (
        response.decision
        == "predict"
    )

    assert (
        response.prediction
        is not None
    )

    assert (
        response.prediction.value
        == pytest.approx(
            213.686797 / 100.0,
            rel=1e-5,
        )
    )


def test_microgravity_below_domain_abstains(
    predictor,
):

    request = (
        FireBehaviorPredictionRequest(
            material="PMMA",
            geometry="thin_sheet",
            thickness_um=50.0,
            gravity_regime="microgravity",
            oxygen_fraction=0.21,
            pressure_kpa=101.325,
        )
    )

    response = predictor.predict(
        request
    )

    assert (
        response.decision
        == "abstain"
    )

    assert (
        response.prediction
        is None
    )

    assert (
        "thickness_below_empirical_domain"
        in response.abstention_reasons
    )


def test_normal_gravity_above_domain_abstains(
    predictor,
):

    request = (
        FireBehaviorPredictionRequest(
            material="PMMA",
            geometry="thin_sheet",
            thickness_um=800.0,
            gravity_regime="normal_gravity",
            oxygen_fraction=0.21,
            pressure_kpa=101.325,
        )
    )

    response = predictor.predict(
        request
    )

    assert (
        response.decision
        == "abstain"
    )

    assert (
        "thickness_above_empirical_domain"
        in response.abstention_reasons
    )


def test_wrong_material_abstains(
    predictor,
):

    request = (
        FireBehaviorPredictionRequest(
            material="polyethylene",
            geometry="thin_sheet",
            thickness_um=200.0,
            gravity_regime="microgravity",
            oxygen_fraction=0.21,
            pressure_kpa=101.325,
        )
    )

    response = predictor.predict(
        request
    )

    assert (
        response.decision
        == "abstain"
    )

    assert (
        "unsupported_material"
        in response.abstention_reasons
    )


def test_wrong_geometry_abstains(
    predictor,
):

    request = (
        FireBehaviorPredictionRequest(
            material="PMMA",
            geometry="rod",
            thickness_um=200.0,
            gravity_regime="microgravity",
            oxygen_fraction=0.21,
            pressure_kpa=101.325,
        )
    )

    response = predictor.predict(
        request
    )

    assert (
        response.decision
        == "abstain"
    )

    assert (
        "unsupported_geometry"
        in response.abstention_reasons
    )


def test_wrong_oxygen_abstains(
    predictor,
):

    request = (
        FireBehaviorPredictionRequest(
            material="PMMA",
            geometry="thin_sheet",
            thickness_um=200.0,
            gravity_regime="microgravity",
            oxygen_fraction=0.25,
            pressure_kpa=101.325,
        )
    )

    response = predictor.predict(
        request
    )

    assert (
        response.decision
        == "abstain"
    )

    assert (
        "unsupported_oxygen_fraction"
        in response.abstention_reasons
    )


def test_wrong_pressure_abstains(
    predictor,
):

    request = (
        FireBehaviorPredictionRequest(
            material="PMMA",
            geometry="thin_sheet",
            thickness_um=200.0,
            gravity_regime="microgravity",
            oxygen_fraction=0.21,
            pressure_kpa=80.0,
        )
    )

    response = predictor.predict(
        request
    )

    assert (
        response.decision
        == "abstain"
    )

    assert (
        "unsupported_pressure"
        in response.abstention_reasons
    )


def test_multiple_scope_violations_are_reported(
    predictor,
):

    request = (
        FireBehaviorPredictionRequest(
            material="wood",
            geometry="rod",
            thickness_um=900.0,
            gravity_regime="normal_gravity",
            oxygen_fraction=0.30,
            pressure_kpa=70.0,
        )
    )

    response = predictor.predict(
        request
    )

    assert (
        response.decision
        == "abstain"
    )

    assert (
        response.prediction
        is None
    )

    assert (
        "unsupported_material"
        in response.abstention_reasons
    )

    assert (
        "unsupported_geometry"
        in response.abstention_reasons
    )

    assert (
        "unsupported_oxygen_fraction"
        in response.abstention_reasons
    )

    assert (
        "unsupported_pressure"
        in response.abstention_reasons
    )

    assert (
        "thickness_above_empirical_domain"
        in response.abstention_reasons
    )


def test_domain_boundaries_are_allowed(
    predictor,
):

    lower = (
        FireBehaviorPredictionRequest(
            material="PMMA",
            geometry="thin_sheet",
            thickness_um=101.933,
            gravity_regime="microgravity",
            oxygen_fraction=0.21,
            pressure_kpa=101.325,
        )
    )

    upper = (
        FireBehaviorPredictionRequest(
            material="PMMA",
            geometry="thin_sheet",
            thickness_um=400.433,
            gravity_regime="microgravity",
            oxygen_fraction=0.21,
            pressure_kpa=101.325,
        )
    )

    lower_response = (
        predictor.predict(
            lower
        )
    )

    upper_response = (
        predictor.predict(
            upper
        )
    )

    assert (
        lower_response.decision
        == "predict"
    )

    assert (
        upper_response.decision
        == "predict"
    )


def test_residual_factor_is_not_present_when_abstaining(
    predictor,
):

    request = (
        FireBehaviorPredictionRequest(
            material="PMMA",
            geometry="thin_sheet",
            thickness_um=50.0,
            gravity_regime="microgravity",
            oxygen_fraction=0.21,
            pressure_kpa=101.325,
        )
    )

    response = predictor.predict(
        request
    )

    assert (
        response.descriptive_residual_factor
        is None
    )