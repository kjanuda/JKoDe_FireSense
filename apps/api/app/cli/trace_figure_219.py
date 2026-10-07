import json
import statistics

from PIL import Image, ImageDraw

from app.analysis.axis_transform import (
    pixel_to_value,
    value_to_pixel,
)

from app.core.paths import (
    FIGURES_DATA_DIR,
)

from app.schemas.figure_digitization import (
    FigureDigitizationManifest,
)


SOURCE_ID = "SRC-NASA-20210011385"

IMAGE_FILENAME = (
    "page_048_image_02.jpeg"
)


DARK_THRESHOLD = 170

MIN_RUN_PIXELS = 2
MAX_RUN_PIXELS = 18

SOLID_MAX_STEP = 8

DASHED_MAX_DISTANCE = 30
DASHED_SOLID_SEPARATION = 7

TIME_START = 1.0
TIME_END = 18.5

Y_VALUE_MIN = 1.65
Y_VALUE_MAX = 2.45

SAMPLE_INTERVAL_S = 0.25


def group_dark_runs(
    y_values: list[int],
) -> list[float]:

    if not y_values:
        return []

    groups = []

    current = [
        y_values[0]
    ]

    for value in y_values[1:]:

        if value == current[-1] + 1:
            current.append(value)

        else:
            groups.append(current)

            current = [value]

    groups.append(current)

    centers = []

    for group in groups:

        length = len(group)

        if not (
            MIN_RUN_PIXELS
            <= length
            <= MAX_RUN_PIXELS
        ):
            continue

        centers.append(
            statistics.mean(group)
        )

    return centers


def get_candidates(
    pixels,
    x: int,
    y_top: int,
    y_bottom: int,
) -> list[float]:

    dark_y = []

    for y in range(
        y_top,
        y_bottom + 1,
    ):

        value = pixels[
            x,
            y,
        ]

        if value <= DARK_THRESHOLD:
            dark_y.append(y)

    return group_dark_runs(
        dark_y
    )


def trace_solid(
    pixels,
    x_start: int,
    x_end: int,
    y_top: int,
    y_bottom: int,
) -> dict[int, float]:

    trace = {}

    previous_y = None

    for x in range(
        x_start,
        x_end + 1,
    ):

        candidates = get_candidates(
            pixels,
            x,
            y_top,
            y_bottom,
        )

        if not candidates:
            continue

        if previous_y is None:

            # Solid 0g curve is the
            # upper curve at the start.
            selected = min(
                candidates
            )

        else:

            selected = min(
                candidates,
                key=lambda y: abs(
                    y - previous_y
                ),
            )

            if (
                abs(
                    selected
                    - previous_y
                )
                > SOLID_MAX_STEP
            ):
                continue

        trace[x] = selected
        previous_y = selected

    return trace


def nearest_solid_y(
    solid_trace: dict[int, float],
    x: int,
) -> float | None:

    if x in solid_trace:
        return solid_trace[x]

    nearby = []

    for dx in range(
        1,
        6,
    ):

        if x - dx in solid_trace:
            nearby.append(
                solid_trace[x - dx]
            )

        if x + dx in solid_trace:
            nearby.append(
                solid_trace[x + dx]
            )

    if not nearby:
        return None

    return statistics.median(
        nearby
    )


def trace_dashed(
    pixels,
    solid_trace: dict[int, float],
    x_start: int,
    x_end: int,
    y_top: int,
    y_bottom: int,
) -> dict[int, float]:

    trace = {}

    previous_y = None

    for x in range(
        x_start,
        x_end + 1,
    ):

        candidates = get_candidates(
            pixels,
            x,
            y_top,
            y_bottom,
        )

        if not candidates:
            continue

        solid_y = nearest_solid_y(
            solid_trace,
            x,
        )

        if solid_y is not None:

            candidates = [
                y
                for y in candidates
                if (
                    y
                    >= solid_y
                    + DASHED_SOLID_SEPARATION
                )
            ]

        if not candidates:
            continue

        if previous_y is None:

            # 1g dashed curve is lower
            # than the 0g curve.
            selected = max(
                candidates
            )

        else:

            selected = min(
                candidates,
                key=lambda y: abs(
                    y - previous_y
                ),
            )

            if (
                abs(
                    selected
                    - previous_y
                )
                > DASHED_MAX_DISTANCE
            ):
                continue

        trace[x] = selected
        previous_y = selected

    return trace


def sample_trace(
    trace: dict[int, float],
    x_axis,
    y_axis,
) -> list[dict]:

    results = []

    time_value = TIME_START

    while time_value <= (
        TIME_END + 1e-9
    ):

        target_x = round(
            value_to_pixel(
                time_value,
                x_axis,
            )
        )

        nearby = []

        for x in range(
            target_x - 5,
            target_x + 6,
        ):

            if x in trace:
                nearby.append(
                    (
                        x,
                        trace[x],
                    )
                )

        if nearby:

            pixel_x = round(
                statistics.mean(
                    item[0]
                    for item in nearby
                ),
                2,
            )

            pixel_y = round(
                statistics.median(
                    item[1]
                    for item in nearby
                ),
                2,
            )

            spread_rate = (
                pixel_to_value(
                    pixel_y,
                    y_axis,
                )
            )

            results.append(
                {
                    "time_s": round(
                        time_value,
                        3,
                    ),
                    "spread_rate_mm_s": round(
                        spread_rate,
                        4,
                    ),
                    "pixel_x": pixel_x,
                    "pixel_y": pixel_y,
                    "source_type": (
                        "figure_digitized"
                    ),
                    "human_verified": False,
                }
            )

        time_value += (
            SAMPLE_INTERVAL_S
        )

    return results


def mean_value(
    points: list[dict],
) -> float | None:

    if not points:
        return None

    return statistics.mean(
        point[
            "spread_rate_mm_s"
        ]
        for point in points
    )


def main():

    root = (
        FIGURES_DATA_DIR
        / SOURCE_ID
    )

    image_path = (
        root
        / "embedded"
        / IMAGE_FILENAME
    )

    manifest_path = (
        root
        / "digitization"
        / "figure_2_19.json"
    )

    manifest = (
        FigureDigitizationManifest
        .model_validate_json(
            manifest_path.read_text(
                encoding="utf-8"
            )
        )
    )

    panel = next(
        item
        for item in manifest.panels
        if item.panel_id == "B"
    )

    if (
        panel.x_axis is None
        or panel.y_axis is None
    ):
        raise ValueError(
            "Panel B axis calibration "
            "is missing."
        )

    image = Image.open(
        image_path
    ).convert(
        "RGB"
    )

    gray = image.convert(
        "L"
    )

    pixels = gray.load()

    x_start = round(
        value_to_pixel(
            TIME_START,
            panel.x_axis,
        )
    )

    x_end = round(
        value_to_pixel(
            TIME_END,
            panel.x_axis,
        )
    )

    y_for_max = round(
        value_to_pixel(
            Y_VALUE_MAX,
            panel.y_axis,
        )
    )

    y_for_min = round(
        value_to_pixel(
            Y_VALUE_MIN,
            panel.y_axis,
        )
    )

    y_top = min(
        y_for_max,
        y_for_min,
    )

    y_bottom = max(
        y_for_max,
        y_for_min,
    )

    solid_trace = trace_solid(
        pixels=pixels,
        x_start=x_start,
        x_end=x_end,
        y_top=y_top,
        y_bottom=y_bottom,
    )

    dashed_trace = trace_dashed(
        pixels=pixels,
        solid_trace=solid_trace,
        x_start=x_start,
        x_end=x_end,
        y_top=y_top,
        y_bottom=y_bottom,
    )

    zero_g_points = sample_trace(
        trace=solid_trace,
        x_axis=panel.x_axis,
        y_axis=panel.y_axis,
    )

    one_g_points = sample_trace(
        trace=dashed_trace,
        x_axis=panel.x_axis,
        y_axis=panel.y_axis,
    )

    output_dir = (
        root
        / "digitization"
        / "figure_2_19"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_json = (
        output_dir
        / "trace_preview.json"
    )

    result = {
        "source_id": SOURCE_ID,
        "figure_ref": "2.19",
        "panel_id": "B",

        "status": (
            "needs_overlay_review"
        ),

        "calibration": {
            "time_s": [
                0.0,
                20.0,
            ],
            "spread_rate_mm_s": [
                0.0,
                3.0,
            ],
        },

        "trace_settings": {
            "dark_threshold": (
                DARK_THRESHOLD
            ),
            "time_window_s": [
                TIME_START,
                TIME_END,
            ],
            "spread_window_mm_s": [
                Y_VALUE_MIN,
                Y_VALUE_MAX,
            ],
            "sample_interval_s": (
                SAMPLE_INTERVAL_S
            ),
        },

        "series": {
            "0g": {
                "gravity_regime": (
                    "microgravity"
                ),
                "point_count": len(
                    zero_g_points
                ),
                "mean_spread_rate_mm_s": (
                    mean_value(
                        zero_g_points
                    )
                ),
                "points": (
                    zero_g_points
                ),
            },

            "1g": {
                "gravity_regime": (
                    "normal_gravity"
                ),
                "point_count": len(
                    one_g_points
                ),
                "mean_spread_rate_mm_s": (
                    mean_value(
                        one_g_points
                    )
                ),
                "points": (
                    one_g_points
                ),
            },
        },
    }

    output_json.write_text(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    # -------------------------
    # Overlay
    # -------------------------

    overlay = image.copy()

    draw = ImageDraw.Draw(
        overlay
    )

    # Panel-B scientific plot box
    bounds = panel.pixel_bounds

    draw.rectangle(
        (
            bounds.left_px,
            bounds.top_px,
            bounds.right_px,
            bounds.bottom_px,
        ),
        outline=(
            70,
            70,
            70,
        ),
        width=2,
    )

    # Use different overlay colours
    # ONLY for human review.
    for index, point in enumerate(
        zero_g_points
    ):

        if index % 2 != 0:
            continue

        x = point["pixel_x"]
        y = point["pixel_y"]

        radius = 4

        draw.ellipse(
            (
                x - radius,
                y - radius,
                x + radius,
                y + radius,
            ),
            outline=(
                255,
                0,
                0,
            ),
            width=2,
        )

    for index, point in enumerate(
        one_g_points
    ):

        if index % 2 != 0:
            continue

        x = point["pixel_x"]
        y = point["pixel_y"]

        radius = 4

        draw.rectangle(
            (
                x - radius,
                y - radius,
                x + radius,
                y + radius,
            ),
            outline=(
                0,
                80,
                255,
            ),
            width=2,
        )

    overlay_path = (
        output_dir
        / "trace_overlay.png"
    )

    overlay.save(
        overlay_path
    )

    print()
    print(
        "FIGURE 2.19 CURVE TRACE"
    )
    print(
        "-----------------------"
    )

    print(
        f"0g points : "
        f"{len(zero_g_points)}"
    )

    print(
        f"1g points : "
        f"{len(one_g_points)}"
    )

    zero_mean = mean_value(
        zero_g_points
    )

    one_mean = mean_value(
        one_g_points
    )

    if zero_mean is not None:
        print(
            f"0g mean   : "
            f"{zero_mean:.3f} mm/s"
        )

    if one_mean is not None:
        print(
            f"1g mean   : "
            f"{one_mean:.3f} mm/s"
        )

    print()
    print(
        f"JSON    : {output_json}"
    )

    print(
        f"Overlay : {overlay_path}"
    )

    print()
    print(
        "IMPORTANT: These points are "
        "NOT accepted training data yet."
    )

    print(
        "Review the overlay before "
        "marking them verified."
    )


if __name__ == "__main__":
    main()