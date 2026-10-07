from typing import Literal

from pydantic import BaseModel, Field


GravityRegime = Literal[
    "microgravity",
    "normal_gravity",
]

PredictionDecision = Literal[
    "predict",
    "abstain",
]


class FireBehaviorPredictionRequest(BaseModel):
    material: str = Field(
        min_length=1,
        examples=["PMMA"],
    )

    geometry: str = Field(
        min_length=1,
        examples=["thin_sheet"],
    )

    thickness_um: float = Field(
        gt=0,
        examples=[200.0],
    )

    gravity_regime: GravityRegime

    oxygen_fraction: float = Field(
        gt=0,
        le=1,
        examples=[0.21],
    )

    pressure_kpa: float = Field(
        gt=0,
        examples=[101.325],
    )


class SupportedDomain(BaseModel):
    material: str
    geometry: str

    gravity_regime: GravityRegime

    thickness_um_min: float
    thickness_um_max: float

    oxygen_fraction: float
    pressure_kpa: float


class PredictionValue(BaseModel):
    quantity: Literal[
        "flame_spread_rate"
    ] = "flame_spread_rate"

    value: float

    unit: Literal[
        "mm/s"
    ] = "mm/s"


class PredictionModelInfo(BaseModel):
    model_name: str
    model_version: str

    formula: str

    coefficient_k: float

    canonical_evidence_figure: str

    external_validation_status: Literal[
        "not_performed"
    ] = "not_performed"

    production_ready: Literal[
        False
    ] = False


class FireBehaviorPredictionResponse(BaseModel):
    decision: PredictionDecision

    prediction: (
        PredictionValue
        | None
    ) = None

    abstention_reasons: list[str] = []

    supported_domain: (
        SupportedDomain
        | None
    ) = None

    model: PredictionModelInfo

    descriptive_residual_factor: (
        float
        | None
    ) = None

    uncertainty_note: str

    warnings: list[str] = []