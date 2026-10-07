import json
import math
from pathlib import Path

from PIL import Image, ImageDraw

from app.core.paths import FIGURES_DATA_DIR


SOURCE_ID = "SRC-NASA-20210011385"
IMAGE_NAME = "page_051_image_01.jpeg"


# ============================================================
# ORIGINAL HUMAN CLICKS
# ============================================================
#
# Important:
#
# - x_left / x_right define the visible x-axis decade endpoints.
# - y_bottom is also the 0.01 mm/s major tick.
# - y_top is the TOP FRAME of the plot.
#   It is NOT the 10 mm/s major tick.
#
# Therefore the y scientific transform must use dedicated
# major-tick reference pixels rather than TOP/BOTTOM directly.
#

CLICKS = {
    "x_left": {
        "x": 187.33,
        "y": 869.08,
    },
    "x_right": {
        "x": 1949.00,
        "y": 873.08,
    },
    "y_top": {
        "x": 188.33,
        "y": 2.08,
    },
    "y_bottom": {
        "x": 187.33,
        "y": 872.08,
    },
}


# ============================================================
# PLOT FRAME
# ============================================================

PLOT_LEFT = 187.33
PLOT_RIGHT = 1949.00
PLOT_TOP = 2.08
PLOT_BOTTOM = 872.08


# ============================================================
# X-AXIS CALIBRATION
# ============================================================
#
# Figure 2.22 x-axis:
#
#   10^1 → 10^5 µm
#
# The visible plot frame endpoints correspond to the
# scientific endpoints of the x-axis.
#

X_MIN = 10.0
X_MAX = 100000.0


# ============================================================
# Y-AXIS CALIBRATION
# ============================================================
#
# Figure 2.22 y-axis is logarithmic.
#
# The visible upper plot frame extends ABOVE the 10 mm/s tick.
# Therefore:
#
#   y ≈ 49.50 px  -> 10 mm/s
#   y = 872.08 px -> 0.01 mm/s
#
# These two major tick references define the y transform.
#
# The plot top at y=2.08 px therefore represents a value
# greater than 10 mm/s (~14.9 mm/s), which is valid.
#

Y_REFERENCE_HIGH_VALUE = 10.0
Y_REFERENCE_HIGH_PIXEL = 49.50

Y_REFERENCE_LOW_VALUE = 0.01
Y_REFERENCE_LOW_PIXEL = 872.08


# ============================================================
# MAJOR DECADE TICKS
# ============================================================

X_MAJOR_TICKS = [
    10.0,
    100.0,
    1000.0,
    10000.0,
    100000.0,
]

Y_MAJOR_TICKS = [
    0.01,
    0.1,
    1.0,
    10.0,
]


# ============================================================
# LOG TRANSFORMS
# ============================================================


def value_to_pixel_x(
    value: float,
) -> float:
    """
    Convert scientific x value in micrometres to image pixel x
    using a base-10 logarithmic transform.
    """

    if value <= 0:
        raise ValueError(
            "X-axis log value must be > 0."
        )

    log_min = math.log10(
        X_MIN
    )

    log_max = math.log10(
        X_MAX
    )

    log_value = math.log10(
        value
    )

    fraction = (
        log_value - log_min
    ) / (
        log_max - log_min
    )

    pixel_x = (
        PLOT_LEFT
        + fraction
        * (
            PLOT_RIGHT
            - PLOT_LEFT
        )
    )

    return pixel_x


def pixel_to_value_x(
    pixel_x: float,
) -> float:
    """
    Convert image pixel x to scientific x value in µm.
    """

    fraction = (
        pixel_x - PLOT_LEFT
    ) / (
        PLOT_RIGHT
        - PLOT_LEFT
    )

    log_min = math.log10(
        X_MIN
    )

    log_max = math.log10(
        X_MAX
    )

    log_value = (
        log_min
        + fraction
        * (
            log_max
            - log_min
        )
    )

    return 10 ** log_value


def value_to_pixel_y(
    value: float,
) -> float:
    """
    Convert scientific spread rate in mm/s to image pixel y.

    Uses two known log-decade tick references:

        10 mm/s   -> ~49.50 px
        0.01 mm/s -> 872.08 px

    Image y increases downward.
    """

    if value <= 0:
        raise ValueError(
            "Y-axis log value must be > 0."
        )

    log_high = math.log10(
        Y_REFERENCE_HIGH_VALUE
    )

    log_low = math.log10(
        Y_REFERENCE_LOW_VALUE
    )

    log_value = math.log10(
        value
    )

    fraction = (
        log_high
        - log_value
    ) / (
        log_high
        - log_low
    )

    pixel_y = (
        Y_REFERENCE_HIGH_PIXEL
        + fraction
        * (
            Y_REFERENCE_LOW_PIXEL
            - Y_REFERENCE_HIGH_PIXEL
        )
    )

    return pixel_y


def pixel_to_value_y(
    pixel_y: float,
) -> float:
    """
    Convert image pixel y to scientific spread rate in mm/s.
    """

    fraction = (
        pixel_y
        - Y_REFERENCE_HIGH_PIXEL
    ) / (
        Y_REFERENCE_LOW_PIXEL
        - Y_REFERENCE_HIGH_PIXEL
    )

    log_high = math.log10(
        Y_REFERENCE_HIGH_VALUE
    )

    log_low = math.log10(
        Y_REFERENCE_LOW_VALUE
    )

    log_value = (
        log_high
        - fraction
        * (
            log_high
            - log_low
        )
    )

    return 10 ** log_value


# ============================================================
# MAIN
# ============================================================


def main():

    root = (
        FIGURES_DATA_DIR
        / SOURCE_ID
    )

    image_path = (
        root
        / "embedded"
        / "figures_2_21_2_22"
        / IMAGE_NAME
    )

    output_dir = (
        root
        / "digitization"
        / "figure_2_22"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    metadata_path = (
        output_dir
        / "calibration_metadata.json"
    )

    validation_path = (
        output_dir
        / "calibration_validation.json"
    )

    overlay_path = (
        output_dir
        / "calibration_overlay.png"
    )

    if not image_path.exists():
        raise FileNotFoundError(
            f"Missing Figure 2.22 image: "
            f"{image_path}"
        )

    image = Image.open(
        image_path
    ).convert(
        "RGB"
    )

    width, height = image.size

    # ========================================================
    # MANUAL CLICK CONSISTENCY
    # ========================================================

    lower_left_repeat_difference = abs(
        CLICKS["x_left"]["y"]
        - CLICKS["y_bottom"]["y"]
    )

    right_baseline_difference = abs(
        CLICKS["x_right"]["y"]
        - CLICKS["y_bottom"]["y"]
    )

    left_axis_alignment_difference = abs(
        CLICKS["y_top"]["x"]
        - CLICKS["y_bottom"]["x"]
    )

    click_consistency_pass = (
        lower_left_repeat_difference
        <= 5.0
        and right_baseline_difference
        <= 5.0
        and left_axis_alignment_difference
        <= 5.0
    )

    # ========================================================
    # X MAJOR TICKS
    # ========================================================

    x_ticks = []

    for value in X_MAJOR_TICKS:

        pixel_x = value_to_pixel_x(
            value
        )

        round_trip_value = (
            pixel_to_value_x(
                pixel_x
            )
        )

        x_ticks.append(
            {
                "value_um": value,

                "pixel_x": round(
                    pixel_x,
                    3,
                ),

                "round_trip_value_um": round(
                    round_trip_value,
                    8,
                ),
            }
        )

    # ========================================================
    # Y MAJOR TICKS
    # ========================================================

    y_ticks = []

    for value in Y_MAJOR_TICKS:

        pixel_y = value_to_pixel_y(
            value
        )

        round_trip_value = (
            pixel_to_value_y(
                pixel_y
            )
        )

        y_ticks.append(
            {
                "value_mm_s": value,

                "pixel_y": round(
                    pixel_y,
                    3,
                ),

                "round_trip_value_mm_s": round(
                    round_trip_value,
                    10,
                ),
            }
        )

    # ========================================================
    # SCIENTIFIC VALUE AT PHYSICAL PLOT TOP
    # ========================================================

    plot_top_scientific_value = (
        pixel_to_value_y(
            PLOT_TOP
        )
    )

    plot_bottom_scientific_value = (
        pixel_to_value_y(
            PLOT_BOTTOM
        )
    )

    # ========================================================
    # TRANSFORM ROUND-TRIP CHECKS
    # ========================================================

    x_round_trip_pass = all(
        math.isclose(
            tick["value_um"],
            tick[
                "round_trip_value_um"
            ],
            rel_tol=1e-8,
            abs_tol=1e-8,
        )
        for tick in x_ticks
    )

    y_round_trip_pass = all(
        math.isclose(
            tick["value_mm_s"],
            tick[
                "round_trip_value_mm_s"
            ],
            rel_tol=1e-8,
            abs_tol=1e-8,
        )
        for tick in y_ticks
    )

    transform_math_pass = (
        x_round_trip_pass
        and y_round_trip_pass
    )

    # ========================================================
    # SAVE CALIBRATION METADATA
    # ========================================================

    metadata = {
        "source_id": SOURCE_ID,

        "figure_ref": "2.22",

        "source_image": (
            IMAGE_NAME
        ),

        "source_image_sha256": (
            "9f131ab1bc34c0bf083fa48d145e80d"
            "204192329bec15aa47f7c6f79e065c7f7"
        ),

        "image_width": width,
        "image_height": height,

        "calibration_method": (
            "manual_frame_clicks_plus_"
            "major_tick_reference"
        ),

        "clicks": CLICKS,

        "plot_bounds": {
            "left": (
                PLOT_LEFT
            ),

            "right": (
                PLOT_RIGHT
            ),

            "top": (
                PLOT_TOP
            ),

            "bottom": (
                PLOT_BOTTOM
            ),
        },

        "x_axis": {
            "label": (
                "Fuel thickness"
            ),

            "unit": "µm",

            "scale": "log10",

            "value_min": (
                X_MIN
            ),

            "value_max": (
                X_MAX
            ),

            "pixel_left": (
                PLOT_LEFT
            ),

            "pixel_right": (
                PLOT_RIGHT
            ),

            "calibration_basis": (
                "visible decade endpoints"
            ),
        },

        "y_axis": {
            "label": (
                "Spread rate"
            ),

            "unit": (
                "mm/s"
            ),

            "scale": (
                "log10"
            ),

            "reference_value_high": (
                Y_REFERENCE_HIGH_VALUE
            ),

            "reference_pixel_high": (
                Y_REFERENCE_HIGH_PIXEL
            ),

            "reference_value_low": (
                Y_REFERENCE_LOW_VALUE
            ),

            "reference_pixel_low": (
                Y_REFERENCE_LOW_PIXEL
            ),

            "plot_pixel_top": (
                PLOT_TOP
            ),

            "plot_pixel_bottom": (
                PLOT_BOTTOM
            ),

            "plot_top_extrapolated_value_mm_s": (
                round(
                    plot_top_scientific_value,
                    6,
                )
            ),

            "plot_bottom_value_mm_s": (
                round(
                    plot_bottom_scientific_value,
                    8,
                )
            ),

            "allows_extrapolation_above_10_mm_s": (
                True
            ),

            "calibration_basis": (
                "major log-decade tick references"
            ),
        },

        "important_notes": [
            (
                "The physical plot top is not the "
                "10 mm/s tick."
            ),

            (
                "The 10 mm/s major tick is located "
                "approximately at pixel y=49.50."
            ),

            (
                "Scientific y values above 10 mm/s "
                "are therefore valid within the "
                "visible plot area."
            ),

            (
                "Theoretical curves must remain "
                "separate from experimental points."
            ),
        ],

        "status": (
            "axis_calibrated_needs_visual_review"
        ),
    }

    metadata_path.write_text(
        json.dumps(
            metadata,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    # ========================================================
    # BUILD VISUAL OVERLAY
    # ========================================================

    overlay = image.copy()

    draw = ImageDraw.Draw(
        overlay
    )

    # --------------------------------------------------------
    # GREEN = physical plot boundary
    # --------------------------------------------------------

    draw.rectangle(
        (
            PLOT_LEFT,
            PLOT_TOP,
            PLOT_RIGHT,
            PLOT_BOTTOM,
        ),
        outline=(
            0,
            180,
            0,
        ),
        width=4,
    )

    # --------------------------------------------------------
    # BLUE = X decade guides
    # --------------------------------------------------------

    for tick in x_ticks:

        pixel_x = tick[
            "pixel_x"
        ]

        draw.line(
            (
                pixel_x,
                PLOT_TOP,
                pixel_x,
                PLOT_BOTTOM,
            ),
            fill=(
                0,
                100,
                255,
            ),
            width=2,
        )

        draw.text(
            (
                pixel_x + 6,
                PLOT_BOTTOM - 22,
            ),
            (
                f"{tick['value_um']:g}"
            ),
            fill=(
                0,
                80,
                220,
            ),
        )

    # --------------------------------------------------------
    # ORANGE = Y decade guides
    # --------------------------------------------------------

    for tick in y_ticks:

        pixel_y = tick[
            "pixel_y"
        ]

        draw.line(
            (
                PLOT_LEFT,
                pixel_y,
                PLOT_RIGHT,
                pixel_y,
            ),
            fill=(
                255,
                140,
                0,
            ),
            width=2,
        )

        draw.text(
            (
                PLOT_LEFT + 8,
                pixel_y + 5,
            ),
            (
                f"{tick['value_mm_s']:g}"
            ),
            fill=(
                210,
                90,
                0,
            ),
        )

    # --------------------------------------------------------
    # PURPLE = original human frame clicks
    # --------------------------------------------------------

    for name, point in (
        CLICKS.items()
    ):

        x = point["x"]
        y = point["y"]

        radius = 10

        draw.ellipse(
            (
                x - radius,
                y - radius,
                x + radius,
                y + radius,
            ),
            outline=(
                180,
                0,
                220,
            ),
            width=3,
        )

        draw.text(
            (
                x + 12,
                y + 4,
            ),
            name,
            fill=(
                140,
                0,
                180,
            ),
        )

    # --------------------------------------------------------
    # Y=10 reference marker
    # --------------------------------------------------------

    draw.ellipse(
        (
            PLOT_LEFT - 8,
            Y_REFERENCE_HIGH_PIXEL - 8,
            PLOT_LEFT + 8,
            Y_REFERENCE_HIGH_PIXEL + 8,
        ),
        outline=(
            255,
            0,
            180,
        ),
        width=3,
    )

    draw.text(
        (
            PLOT_LEFT + 12,
            Y_REFERENCE_HIGH_PIXEL - 18,
        ),
        "10 mm/s reference",
        fill=(
            200,
            0,
            150,
        ),
    )

    overlay.save(
        overlay_path
    )

    # ========================================================
    # VALIDATION JSON
    # ========================================================

    validation = {
        "source_id": (
            SOURCE_ID
        ),

        "figure_ref": (
            "2.22"
        ),

        "manual_click_consistency": {
            "lower_left_repeat_difference_px": (
                round(
                    lower_left_repeat_difference,
                    3,
                )
            ),

            "right_baseline_difference_px": (
                round(
                    right_baseline_difference,
                    3,
                )
            ),

            "left_axis_alignment_difference_px": (
                round(
                    left_axis_alignment_difference,
                    3,
                )
            ),

            "threshold_px": (
                5.0
            ),

            "pass": (
                click_consistency_pass
            ),
        },

        "transform_math": {
            "x_round_trip_pass": (
                x_round_trip_pass
            ),

            "y_round_trip_pass": (
                y_round_trip_pass
            ),

            "pass": (
                transform_math_pass
            ),
        },

        "x_major_ticks": (
            x_ticks
        ),

        "y_major_ticks": (
            y_ticks
        ),

        "plot_top_extrapolated_value_mm_s": (
            round(
                plot_top_scientific_value,
                6,
            )
        ),

        "visual_overlay_status": (
            "needs_human_review"
        ),

        "final_status": (
            "needs_visual_overlay_review"
        ),
    }

    validation_path.write_text(
        json.dumps(
            validation,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    # ========================================================
    # TERMINAL OUTPUT
    # ========================================================

    print()
    print(
        "FIGURE 2.22 CORRECTED LOG CALIBRATION"
    )

    print(
        "-------------------------------------"
    )

    print()
    print(
        f"Image dimensions : "
        f"{width} x {height}"
    )

    print()
    print(
        "Physical plot bounds:"
    )

    print(
        f"  left   = "
        f"{PLOT_LEFT:.2f}"
    )

    print(
        f"  right  = "
        f"{PLOT_RIGHT:.2f}"
    )

    print(
        f"  top    = "
        f"{PLOT_TOP:.2f}"
    )

    print(
        f"  bottom = "
        f"{PLOT_BOTTOM:.2f}"
    )

    print()
    print(
        "Y calibration references:"
    )

    print(
        f"  10 mm/s   -> "
        f"y = "
        f"{Y_REFERENCE_HIGH_PIXEL:.2f}"
    )

    print(
        f"  0.01 mm/s -> "
        f"y = "
        f"{Y_REFERENCE_LOW_PIXEL:.2f}"
    )

    print()
    print(
        "Plot top scientific value:"
    )

    print(
        f"  y={PLOT_TOP:.2f}px"
        f" -> "
        f"{plot_top_scientific_value:.4f} mm/s"
    )

    print()
    print(
        "Click consistency:"
    )

    print(
        f"  lower-left repeat : "
        f"{lower_left_repeat_difference:.2f} px"
    )

    print(
        f"  right baseline    : "
        f"{right_baseline_difference:.2f} px"
    )

    print(
        f"  left-axis align   : "
        f"{left_axis_alignment_difference:.2f} px"
    )

    print(
        f"  automatic check   : "
        f"{'PASS' if click_consistency_pass else 'FAIL'}"
    )

    print()
    print(
        "Transform round-trip:"
    )

    print(
        f"  x transform : "
        f"{'PASS' if x_round_trip_pass else 'FAIL'}"
    )

    print(
        f"  y transform : "
        f"{'PASS' if y_round_trip_pass else 'FAIL'}"
    )

    print()
    print(
        "X major log ticks:"
    )

    for tick in x_ticks:

        print(
            f"  "
            f"{tick['value_um']:>8g} µm"
            f" -> "
            f"x = "
            f"{tick['pixel_x']:.2f}"
        )

    print()
    print(
        "Y major log ticks:"
    )

    for tick in reversed(
        y_ticks
    ):

        print(
            f"  "
            f"{tick['value_mm_s']:>8g} mm/s"
            f" -> "
            f"y = "
            f"{tick['pixel_y']:.2f}"
        )

    print()
    print(
        "Expected corrected Y positions:"
    )

    print(
        "  10      mm/s -> ~49.50 px"
    )

    print(
        "  1       mm/s -> ~323.69 px"
    )

    print(
        "  0.1     mm/s -> ~597.89 px"
    )

    print(
        "  0.01    mm/s -> ~872.08 px"
    )

    print()
    print(
        "Metadata:"
    )

    print(
        f"  {metadata_path}"
    )

    print()
    print(
        "Validation:"
    )

    print(
        f"  {validation_path}"
    )

    print()
    print(
        "Overlay:"
    )

    print(
        f"  {overlay_path}"
    )

    print()
    print(
        "STATUS:"
    )

    print(
        "  needs_visual_overlay_review"
    )

    print()
    print(
        "IMPORTANT:"
    )

    print(
        "  Do NOT digitize Figure 2.22 "
        "experimental points until this "
        "corrected overlay visually passes."
    )


if __name__ == "__main__":
    main()