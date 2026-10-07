from typing import Literal

from pydantic import BaseModel

from app.schemas.prediction import (
    FireBehaviorPredictionResponse,
    GravityRegime,
)


class EvidenceRecordSummary(BaseModel):
    record_id: str

    source_id: str

    figure_ref: str

    gravity_regime: GravityRegime

    thickness_um: float

    observed_spread_rate_mm_s: float

    digitization_uncertainty_mm_s: float


class DatasetIntegrityInfo(BaseModel):
    dataset_name: str

    dataset_version: str

    expected_sha256: str

    actual_sha256: str

    integrity_verified: bool


class CoefficientDerivationInfo(BaseModel):
    formula: Literal[
        "V = K / tau"
    ]

    coefficient_k: float

    exponent: Literal[
        -1.0
    ] = -1.0

    fit_space: Literal[
        "natural_log"
    ] = "natural_log"

    derivation: str

    contributing_record_count: int

    contributing_record_ids: list[str]


class PredictionEvidenceTrace(BaseModel):
    canonical_source_id: str

    canonical_figure_ref: str

    gravity_regime: GravityRegime

    dataset_integrity: DatasetIntegrityInfo

    coefficient_derivation: CoefficientDerivationInfo

    nearest_evidence_records: list[
        EvidenceRecordSummary
    ]

    contributing_evidence_records: list[
        EvidenceRecordSummary
    ]

    evidence_policy: list[str]

    uncertainty_state: list[str]

    external_validation_status: Literal[
        "not_performed"
    ] = "not_performed"

    production_ready: Literal[
        False
    ] = False


class ExplainedPredictionResponse(BaseModel):
    result: FireBehaviorPredictionResponse

    evidence_trace: PredictionEvidenceTrace