from typing import Literal

from pydantic import BaseModel, Field, model_validator


class ThinSheetExperimentRecord(BaseModel):
    # Identity
    record_id: str
    source_id: str
    study_id: str
    run_id: str | None = None

    # Material
    material_name: Literal["PMMA"] = "PMMA"
    geometry: Literal["thin_sheet"] = "thin_sheet"

    thickness_um: float = Field(gt=0)

    width_mm: float | None = Field(
        default=None,
        gt=0,
    )

    length_mm: float | None = Field(
        default=None,
        gt=0,
    )

    # Gravity
    gravity_regime: Literal[
        "microgravity",
        "normal_gravity",
        "partial_gravity",
        "unknown",
    ]

    gravity_g: float | None = Field(
        default=None,
        ge=0,
    )

    reported_gravity_label: str | None = None

    # Atmosphere
    oxygen_fraction: float | None = Field(
        default=None,
        gt=0,
        le=1,
    )

    pressure_kpa: float | None = Field(
        default=None,
        gt=0,
    )

    oxygen_partial_pressure_kpa: float | None = Field(
        default=None,
        gt=0,
    )

    # Flow
    flow_velocity_cm_s: float | None = Field(
        default=None,
        ge=0,
    )

    flow_direction: Literal[
        "opposed",
        "buoyancy_generated_opposed",
        "unknown",
    ] = "unknown"

    # Outcome
    flame_spread_rate_mm_s: float | None = Field(
        default=None,
        ge=0,
    )

    sustained_flame: bool | None = None
    extinguished: bool | None = None

    observation_type: Literal[
        "spread_rate",
        "extinction",
        "spread_and_extinction",
    ]

    # How outcome was obtained
    outcome_summary_method: Literal[
        "source_reported_mean",
        "source_reported_value",
        "digitized_time_series_mean",
        "figure_digitized_point",
    ]

    # Evidence provenance
    value_source: Literal[
        "text",
        "table",
        "figure_digitized",
        "dataset",
        "manual",
    ]

    source_page: int = Field(gt=0)

    figure_ref: str | None = None
    figure_panel: str | None = None

    evidence_text: str

    estimated_from_figure: bool = False

    # Verification
    overlay_verified: bool = False
    human_verified: bool = False

    review_status: Literal[
        "candidate",
        "accepted_evidence",
        "training_ready",
        "rejected",
    ] = "candidate"

    # Keep these separate.
    digitization_uncertainty_mm_s: float | None = Field(
        default=None,
        ge=0,
    )

    experimental_uncertainty_mm_s: float | None = Field(
        default=None,
        ge=0,
    )

    notes: str | None = None

    @model_validator(mode="after")
    def validate_record(self):

        if (
            self.flame_spread_rate_mm_s is None
            and self.extinguished is None
            and self.sustained_flame is None
        ):
            raise ValueError(
                "At least one experimental outcome "
                "is required."
            )

        # Only calculate pO2 when both
        # atmosphere values are known.
        if (
            self.oxygen_partial_pressure_kpa is None
            and self.oxygen_fraction is not None
            and self.pressure_kpa is not None
        ):
            self.oxygen_partial_pressure_kpa = (
                self.oxygen_fraction
                * self.pressure_kpa
            )

        # Do not silently encode ISS microgravity
        # as exact 0.0 g.
        if (
            self.gravity_regime == "microgravity"
            and self.gravity_g == 0.0
        ):
            raise ValueError(
                "Do not encode ISS microgravity as "
                "exact 0.0 g; leave gravity_g null "
                "unless a measured value is available."
            )

        return self