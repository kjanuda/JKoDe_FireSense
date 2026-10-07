from functools import lru_cache

from fastapi import (
    APIRouter,
    Depends,
)

from app.schemas.evidence_trace import (
    ExplainedPredictionResponse,
)

from app.schemas.prediction import (
    FireBehaviorPredictionRequest,
    FireBehaviorPredictionResponse,
)

from app.services.physics_baseline_predictor import (
    PhysicsBaselinePredictor,
)

from app.services.prediction_explainer import (
    PredictionExplainer,
)


router = APIRouter(
    prefix="/api/predict",
    tags=["Fire Behavior Prediction"],
)


@lru_cache
def get_predictor() -> PhysicsBaselinePredictor:

    return PhysicsBaselinePredictor()


@lru_cache
def get_explainer() -> PredictionExplainer:

    return PredictionExplainer(
        predictor=get_predictor()
    )


@router.post(
    "/fire-behavior",
    response_model=FireBehaviorPredictionResponse,
    summary=(
        "Predict PMMA thin-sheet "
        "flame spread"
    ),
    description=(
        "Exploratory FireSense Physics "
        "Baseline v0. Predicts flame "
        "spread rate only inside the "
        "empirically supported Figure "
        "2.21 domain. Requests outside "
        "the supported scientific scope "
        "return an explicit abstention."
    ),
)
def predict_fire_behavior(
    request: FireBehaviorPredictionRequest,

    predictor: PhysicsBaselinePredictor = (
        Depends(
            get_predictor
        )
    ),
) -> FireBehaviorPredictionResponse:

    return predictor.predict(
        request
    )


@router.post(
    "/fire-behavior/explain",
    response_model=ExplainedPredictionResponse,
    summary=(
        "Predict and return evidence trace"
    ),
    description=(
        "Returns the FireSense prediction "
        "or abstention together with the "
        "frozen dataset identity, artifact "
        "integrity verification, canonical "
        "Figure 2.21 evidence, coefficient "
        "derivation, nearby observations, "
        "provenance policy, and uncertainty "
        "limitations."
    ),
)
def explain_fire_behavior_prediction(
    request: FireBehaviorPredictionRequest,

    explainer: PredictionExplainer = (
        Depends(
            get_explainer
        )
    ),
) -> ExplainedPredictionResponse:

    return explainer.explain(
        request
    )