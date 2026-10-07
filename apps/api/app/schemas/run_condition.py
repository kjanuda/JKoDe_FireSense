from typing import Literal

from pydantic import BaseModel, Field


class RunConditionRecord(BaseModel):
    run_id: str
    source_test_id: str | None = None

    source_id: str
    study_id: str

    material_name: Literal["PMMA"] = "PMMA"
    geometry: Literal["thin_sheet"] = "thin_sheet"

    sample_number: str | None = None

    thickness_um: float = Field(gt=0)

    width_mm: float | None = Field(
        default=None,
        gt=0,
    )

    length_mm: float | None = Field(
        default=None,
        gt=0,
    )

    gravity_regime: Literal[
        "microgravity",
        "normal_gravity",
    ]

    reported_gravity_label: str

    flow_direction: Literal[
        "opposed",
        "buoyancy_generated_opposed",
        "unknown",
    ] = "unknown"

    # Do not confuse hardware/display
    # settings with physical velocity.
    fan_display_sequence: list[str] = []
    air_display_sequence: list[str] = []

    flow_velocity_cm_s: float | None = Field(
        default=None,
        ge=0,
    )

    # Nominal conditions reported
    # in figure/caption context.
    nominal_oxygen_fraction: float | None = Field(
        default=None,
        gt=0,
        le=1,
    )

    nominal_nitrogen_fraction: float | None = Field(
        default=None,
        gt=0,
        le=1,
    )

    nominal_pressure_kpa: float | None = Field(
        default=None,
        gt=0,
    )

    # Appendix measured/calibrated values.
    calibrated_initial_o2_fraction: float | None = Field(
        default=None,
        gt=0,
        le=1,
    )

    calibrated_final_o2_fraction: float | None = Field(
        default=None,
        gt=0,
        le=1,
    )

    measured_initial_o2_fraction: float | None = Field(
        default=None,
        gt=0,
        le=1,
    )

    measured_final_o2_fraction: float | None = Field(
        default=None,
        gt=0,
        le=1,
    )

    initial_co2_fraction: float | None = Field(
        default=None,
        ge=0,
        le=1,
    )

    final_co2_fraction: float | None = Field(
        default=None,
        ge=0,
        le=1,
    )

    initial_co_ppm: float | None = None
    final_co_ppm: float | None = None

    actual_date: str | None = None
    approximate_time: str | None = None
    as_run_test_number: int | None = None

    pdf_page: int = Field(gt=0)
    printed_page: int | None = Field(
        default=None,
        gt=0,
    )

    figure_ref: str | None = None
    appendix_table: str | None = None

    evidence_text: str

    verification_status: Literal[
        "caption_only",
        "appendix_verified",
        "cross_source_verified",
    ]

    notes: str | None = None