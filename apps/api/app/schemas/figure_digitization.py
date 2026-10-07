from typing import Literal

from pydantic import (
    BaseModel,
    Field,
    model_validator,
)


class PixelPoint(BaseModel):
    x: float = Field(ge=0)
    y: float = Field(ge=0)


class PixelBounds(BaseModel):
    left_px: float = Field(ge=0)
    right_px: float = Field(ge=0)
    top_px: float = Field(ge=0)
    bottom_px: float = Field(ge=0)

    @model_validator(mode="after")
    def validate_bounds(self):

        if self.right_px <= self.left_px:
            raise ValueError(
                "right_px must be greater "
                "than left_px"
            )

        if self.bottom_px <= self.top_px:
            raise ValueError(
                "bottom_px must be greater "
                "than top_px"
            )

        return self


class AxisCalibration(BaseModel):
    axis: Literal["x", "y"]

    scale: Literal[
        "linear",
        "log",
    ] = "linear"

    pixel_min: float = Field(ge=0)
    pixel_max: float = Field(ge=0)

    value_min: float
    value_max: float

    unit: str
    label: str


class DigitizedPoint(BaseModel):
    point_id: str
    series_id: str

    pixel: PixelPoint

    x_value: float
    y_value: float

    human_verified: bool = False

    uncertainty_x: float | None = Field(
        default=None,
        ge=0,
    )

    uncertainty_y: float | None = Field(
        default=None,
        ge=0,
    )


class FigureSeries(BaseModel):
    series_id: str
    label: str

    interpretation: str | None = None

    gravity_regime: Literal[
        "microgravity",
        "normal_gravity",
        "unknown",
    ] = "unknown"

    points: list[DigitizedPoint] = Field(
        default_factory=list
    )


class FigurePanel(BaseModel):
    panel_id: str
    label: str

    pixel_bounds: PixelBounds

    x_axis: AxisCalibration | None = None
    y_axis: AxisCalibration | None = None

    series: list[FigureSeries] = Field(
        default_factory=list
    )


class FigureDigitizationManifest(BaseModel):
    digitization_id: str

    source_id: str
    source_page: int = Field(gt=0)

    figure_ref: str

    image_path: str
    image_sha256: str

    image_width_px: int = Field(gt=0)
    image_height_px: int = Field(gt=0)

    figure_role: Literal[
        "experimental",
        "computational",
        "mixed",
        "method",
    ]

    panels: list[FigurePanel] = Field(
        default_factory=list
    )

    status: Literal[
        "needs_axis_calibration",
        "needs_series_mapping",
        "digitizing",
        "needs_overlay_review",
        "verified",
        "rejected",
    ] = "needs_axis_calibration"

    extraction_method: Literal[
        "manual",
        "computer_vision",
        "vlm",
        "hybrid",
    ] = "hybrid"

    notes: str | None = None