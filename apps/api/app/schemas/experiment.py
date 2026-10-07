from typing import Literal

from pydantic import BaseModel, Field, model_validator


class ExperimentRecord(BaseModel):
    # Identity
    record_id: str
    study_id: str
    source_id: str

    # Material
    material_name: str
    geometry: str | None = None
    thickness_mm: float | None = Field(default=None, gt=0)

    # Environment
    gravity_g: float = Field(ge=0)
    oxygen_fraction: float = Field(gt=0, le=1)
    pressure_kpa: float = Field(gt=0)
    oxygen_partial_pressure_kpa: float | None = Field(default=None, gt=0)

    # Flow
    flow_velocity_cm_s: float | None = Field(default=None, ge=0)
    flow_direction: Literal[
        "opposed",
        "concurrent",
        "crossflow",
        "quiescent",
        "unknown",
    ] | None = None

    # Outcomes
    sustained_flame: bool | None = None
    extinguished: bool | None = None
    flame_spread_rate_mm_s: float | None = Field(default=None, ge=0)

    # Provenance
    value_source: Literal[
        "table",
        "text",
        "figure_digitized",
        "dataset",
        "manual",
    ]

    source_page: int = Field(gt=0)
    evidence_text: str

    estimated_from_figure: bool = False

    # Verification state
    verified: bool = False
    flagged: bool = False

    @model_validator(mode="after")
    def validate_physics(self):
        expected_partial_pressure = (
            self.oxygen_fraction * self.pressure_kpa
        )

        # If ppO2 was not provided, calculate it automatically.
        if self.oxygen_partial_pressure_kpa is None:
            self.oxygen_partial_pressure_kpa = expected_partial_pressure
            return self

        # Allow a little tolerance for rounded values in papers.
        tolerance = max(
            0.25,
            expected_partial_pressure * 0.03,
        )

        difference = abs(
            self.oxygen_partial_pressure_kpa
            - expected_partial_pressure
        )

        if difference > tolerance:
            raise ValueError(
                "oxygen_partial_pressure_kpa is inconsistent with "
                "oxygen_fraction × pressure_kpa"
            )

        return self