from app.schemas.figure_digitization import (
    AxisCalibration,
)


def pixel_to_value(
    pixel: float,
    axis: AxisCalibration,
) -> float:

    pixel_range = (
        axis.pixel_max
        - axis.pixel_min
    )

    if pixel_range == 0:
        raise ValueError(
            "Axis pixel range cannot be zero."
        )

    fraction = (
        pixel - axis.pixel_min
    ) / pixel_range

    return (
        axis.value_min
        + fraction
        * (
            axis.value_max
            - axis.value_min
        )
    )


def value_to_pixel(
    value: float,
    axis: AxisCalibration,
) -> float:

    value_range = (
        axis.value_max
        - axis.value_min
    )

    if value_range == 0:
        raise ValueError(
            "Axis value range cannot be zero."
        )

    fraction = (
        value - axis.value_min
    ) / value_range

    return (
        axis.pixel_min
        + fraction
        * (
            axis.pixel_max
            - axis.pixel_min
        )
    )