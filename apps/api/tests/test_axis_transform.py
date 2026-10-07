import pytest

from app.analysis.axis_transform import (
    pixel_to_value,
    value_to_pixel,
)

from app.schemas.figure_digitization import (
    AxisCalibration,
)


def test_panel_b_x_midpoint():

    axis = AxisCalibration(
        axis="x",
        scale="linear",
        pixel_min=1482,
        pixel_max=2570,
        value_min=0,
        value_max=20,
        unit="s",
        label="Time",
    )

    midpoint = (
        1482 + 2570
    ) / 2

    assert (
        pixel_to_value(
            midpoint,
            axis,
        )
        == pytest.approx(10.0)
    )


def test_panel_b_y_bottom_is_zero():

    axis = AxisCalibration(
        axis="y",
        scale="linear",
        pixel_min=674,
        pixel_max=19,
        value_min=0,
        value_max=3,
        unit="mm/s",
        label="Spread rate",
    )

    assert (
        pixel_to_value(
            674,
            axis,
        )
        == pytest.approx(0.0)
    )


def test_panel_b_y_top_is_three():

    axis = AxisCalibration(
        axis="y",
        scale="linear",
        pixel_min=674,
        pixel_max=19,
        value_min=0,
        value_max=3,
        unit="mm/s",
        label="Spread rate",
    )

    assert (
        pixel_to_value(
            19,
            axis,
        )
        == pytest.approx(3.0)
    )


def test_round_trip():

    axis = AxisCalibration(
        axis="y",
        scale="linear",
        pixel_min=674,
        pixel_max=19,
        value_min=0,
        value_max=3,
        unit="mm/s",
        label="Spread rate",
    )

    original_value = 2.2

    pixel = value_to_pixel(
        original_value,
        axis,
    )

    recovered = pixel_to_value(
        pixel,
        axis,
    )

    assert recovered == pytest.approx(
        original_value
    )