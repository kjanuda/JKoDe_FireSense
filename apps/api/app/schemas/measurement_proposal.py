from typing import Literal

from pydantic import BaseModel, Field


class NumericMention(BaseModel):
    value: float
    unit: str

    normalized_value: float | None = None
    normalized_unit: str | None = None

    matched_text: str | None = None

    start_char: int | None = Field(
        default=None,
        ge=0,
    )

    end_char: int | None = Field(
        default=None,
        ge=0,
    )


class MeasurementProposal(BaseModel):
    proposal_id: str

    source_id: str
    study_id: str

    block_id: str
    pages: list[int] = Field(
        default_factory=list
    )

    evidence_form: Literal[
        "prose",
        "figure_linked",
        "table_linked",
        "mixed",
    ]

    gravity_regime: Literal[
        "microgravity",
        "normal_gravity",
        "mixed",
        "unknown",
    ] = "unknown"

    thickness_mentions: list[NumericMention] = Field(
        default_factory=list
    )

    oxygen_mentions: list[NumericMention] = Field(
        default_factory=list
    )

    pressure_mentions: list[NumericMention] = Field(
        default_factory=list
    )

    flow_mentions: list[NumericMention] = Field(
        default_factory=list
    )

    spread_rate_mentions: list[NumericMention] = Field(
        default_factory=list
    )

    figure_refs: list[str] = Field(
        default_factory=list
    )

    table_refs: list[str] = Field(
        default_factory=list
    )

    needs_figure_digitization: bool = False
    needs_table_extraction: bool = False

    extraction_method: Literal[
        "deterministic_regex",
        "llm",
        "manual",
    ] = "deterministic_regex"

    review_status: Literal[
        "pending",
        "accepted",
        "rejected",
        "needs_figure_digitization",
        "needs_table_extraction",
    ] = "pending"

    warnings: list[str] = Field(
        default_factory=list
    )

    raw_text: str