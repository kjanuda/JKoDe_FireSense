from functools import lru_cache

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from app.schemas.next_experiment_explanation import (
    NextExperimentExplanationResponse,
)

from app.schemas.next_experiment_recommendation import (
    NextExperimentRecommendationResponse,
)

from app.services.next_experiment_explainer import (
    NextExperimentExplainer,
)

from app.services.next_experiment_recommendation import (
    NextExperimentRecommendationService,
    RecommendationIntegrityError,
)


router = APIRouter(
    prefix="/api/recommendations",
    tags=["Experiment Recommendation"],
)


@lru_cache
def get_recommendation_service(
) -> NextExperimentRecommendationService:

    return (
        NextExperimentRecommendationService()
    )


def get_explainer(
    service: (
        NextExperimentRecommendationService
    ) = Depends(
        get_recommendation_service
    ),
) -> NextExperimentExplainer:

    return NextExperimentExplainer(
        recommendation_service=service
    )


@router.get(
    "/next-experiment",
    response_model=(
        NextExperimentRecommendationResponse
    ),
    summary=(
        "Return the current next-experiment "
        "research candidate"
    ),
    description=(
        "Returns the frozen FireSense v0 "
        "research-priority matched-pair "
        "experiment candidate together with "
        "the coverage/Bayesian agreement, "
        "posterior uncertainty, evidence "
        "provenance, integrity verification, "
        "and scientific guardrails. "
        "This endpoint does not approve an "
        "experiment and does not refit the "
        "Bayesian model at request time."
    ),
)
def get_next_experiment(
    service: (
        NextExperimentRecommendationService
    ) = Depends(
        get_recommendation_service
    ),
) -> NextExperimentRecommendationResponse:

    try:
        return (
            service.get_recommendation()
        )

    except RecommendationIntegrityError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Recommendation artifact "
                f"integrity failure: {exc}"
            ),
        ) from exc


@router.get(
    "/next-experiment/explain",
    response_model=(
        NextExperimentExplanationResponse
    ),
    summary=(
        "Explain why the next experiment "
        "is prioritized"
    ),
    description=(
        "Provides a human-readable scientific "
        "explanation of the frozen FireSense "
        "next-experiment decision, including "
        "the evidence chain, coverage/Bayesian "
        "agreement, posterior uncertainty, "
        "model limitations, and approval "
        "guardrails. No model is refitted at "
        "request time."
    ),
)
def explain_next_experiment(
    explainer: (
        NextExperimentExplainer
    ) = Depends(
        get_explainer
    ),
) -> NextExperimentExplanationResponse:

    try:
        return (
            explainer.explain()
        )

    except RecommendationIntegrityError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Recommendation artifact "
                f"integrity failure: {exc}"
            ),
        ) from exc
