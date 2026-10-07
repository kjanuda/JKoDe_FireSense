from typing import Literal

from pydantic import BaseModel, Field


class EvidenceLink(BaseModel):
    link_id: str

    source_id: str

    left_entity_type: Literal[
        "figure_series",
        "experiment_record",
        "run_condition",
    ]

    left_entity_id: str

    right_entity_type: Literal[
        "figure_series",
        "experiment_record",
        "run_condition",
    ]

    right_entity_id: str

    relation: Literal[
        "same_run",
        "possible_same_run",
        "same_condition_family",
        "derived_from",
    ]

    status: Literal[
        "confirmed",
        "probable",
        "unresolved",
        "contradicted",
    ]

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    supporting_evidence: list[str]

    conflicting_or_missing_evidence: list[str]

    safe_for_training_join: bool = False

    notes: str | None = None