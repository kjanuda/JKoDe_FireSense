import json
import math

import numpy as np
from PIL import Image, ImageDraw

from app.core.paths import FIGURES_DATA_DIR


SOURCE_ID = "SRC-NASA-20210011385"

IMAGE_NAME = "page_050_image_01.jpeg"


# ---------------------------------------------------------
# Calibration helpers
# ---------------------------------------------------------


def pixel_to_value(
    pixel: float,
    axis: dict,
) -> float:

    pixel_range = (
        axis["pixel_max"]
        - axis["pixel_min"]
    )

    if pixel_range == 0:
        raise ValueError(
            "Axis pixel range cannot be zero."
        )

    fraction = (
        pixel
        - axis["pixel_min"]
    ) / pixel_range

    return (
        axis["value_min"]
        + fraction
        * (
            axis["value_max"]
            - axis["value_min"]
        )
    )


# ---------------------------------------------------------
# Connected components
# ---------------------------------------------------------


def connected_components(
    mask: np.ndarray,
) -> list[dict]:

    height, width = mask.shape

    visited = np.zeros(
        mask.shape,
        dtype=bool,
    )

    components: list[dict] = []

    neighbors = (
        (-1, -1),
        (0, -1),
        (1, -1),
        (-1, 0),
        (1, 0),
        (-1, 1),
        (0, 1),
        (1, 1),
    )

    for y in range(height):

        for x in range(width):

            if (
                not mask[y, x]
                or visited[y, x]
            ):
                continue

            stack = [
                (x, y)
            ]

            visited[y, x] = True

            xs: list[int] = []
            ys: list[int] = []

            while stack:

                current_x, current_y = (
                    stack.pop()
                )

                xs.append(
                    current_x
                )

                ys.append(
                    current_y
                )

                for dx, dy in neighbors:

                    nx = (
                        current_x
                        + dx
                    )

                    ny = (
                        current_y
                        + dy
                    )

                    if (
                        nx < 0
                        or nx >= width
                        or ny < 0
                        or ny >= height
                    ):
                        continue

                    if (
                        visited[ny, nx]
                        or not mask[ny, nx]
                    ):
                        continue

                    visited[
                        ny,
                        nx,
                    ] = True

                    stack.append(
                        (
                            nx,
                            ny,
                        )
                    )

            components.append(
                {
                    "size": len(xs),

                    "min_x": min(xs),
                    "max_x": max(xs),

                    "min_y": min(ys),
                    "max_y": max(ys),

                    "center_x": (
                        sum(xs)
                        / len(xs)
                    ),

                    "center_y": (
                        sum(ys)
                        / len(ys)
                    ),
                }
            )

    return components


# ---------------------------------------------------------
# Boolean image shifting
# ---------------------------------------------------------


def sample_shift(
    mask: np.ndarray,
    dx: int,
    dy: int,
) -> np.ndarray:
    """
    Return an array where:

        output[y, x]
        =
        mask[y + dy, x + dx]

    Out-of-image pixels become False.
    """

    height, width = mask.shape

    output = np.zeros_like(
        mask,
        dtype=bool,
    )

    if dy >= 0:

        src_y = slice(
            dy,
            height,
        )

        dst_y = slice(
            0,
            height - dy,
        )

    else:

        src_y = slice(
            0,
            height + dy,
        )

        dst_y = slice(
            -dy,
            height,
        )

    if dx >= 0:

        src_x = slice(
            dx,
            width,
        )

        dst_x = slice(
            0,
            width - dx,
        )

    else:

        src_x = slice(
            0,
            width + dx,
        )

        dst_x = slice(
            -dx,
            width,
        )

    output[
        dst_y,
        dst_x,
    ] = mask[
        src_y,
        src_x,
    ]

    return output


def dilate_mask(
    mask: np.ndarray,
    radius: int = 1,
) -> np.ndarray:

    result = mask.copy()

    for dy in range(
        -radius,
        radius + 1,
    ):

        for dx in range(
            -radius,
            radius + 1,
        ):

            if (
                dx == 0
                and dy == 0
            ):
                continue

            result |= sample_shift(
                mask,
                dx,
                dy,
            )

    return result


# ---------------------------------------------------------
# Blue filled-circle detector
# ---------------------------------------------------------


def build_blue_mask(
    array: np.ndarray,
) -> np.ndarray:

    # CRITICAL:
    # convert uint8 -> int16 BEFORE subtraction/addition.
    #
    # Otherwise values can wrap at 255 and cause
    # red/white pixels to be classified as blue.
    rgb = array.astype(
        np.int16
    )

    red = rgb[:, :, 0]
    green = rgb[:, :, 1]
    blue = rgb[:, :, 2]

    return (
        (blue >= 110)
        & ((blue - red) >= 55)
        & ((blue - green) >= 35)
    )


def detect_blue_points(
    array: np.ndarray,
    bounds: dict,
    x_axis: dict,
    y_axis: dict,
) -> list[dict]:

    left = int(
        bounds["left_px"]
    )

    right = int(
        bounds["right_px"]
    )

    top = int(
        bounds["top_px"]
    )

    bottom = int(
        bounds["bottom_px"]
    )

    full_mask = build_blue_mask(
        array
    )

    roi = full_mask[
        top:bottom + 1,
        left:right + 1,
    ]

    components = connected_components(
        roi
    )

    points = []

    for component in components:

        width = (
            component["max_x"]
            - component["min_x"]
            + 1
        )

        height = (
            component["max_y"]
            - component["min_y"]
            + 1
        )

        size = component[
            "size"
        ]

        if not (
            5 <= width <= 42
            and 5 <= height <= 42
            and 15 <= size <= 1400
        ):
            continue

        aspect = (
            width / height
        )

        if not (
            0.55
            <= aspect
            <= 1.8
        ):
            continue

        pixel_x = (
            component["center_x"]
            + left
        )

        pixel_y = (
            component["center_y"]
            + top
        )

        # Ignore Figure legend.
        if (
            pixel_x > 900
            and pixel_y < 220
        ):
            continue

        thickness = pixel_to_value(
            pixel_x,
            x_axis,
        )

        spread_rate = pixel_to_value(
            pixel_y,
            y_axis,
        )

        if not (
            5.0
            <= thickness
            <= 795.0
            and 0.0
            <= spread_rate
            <= 10.0
        ):
            continue

        points.append(
            {
                "pixel_x": round(
                    pixel_x,
                    2,
                ),

                "pixel_y": round(
                    pixel_y,
                    2,
                ),

                "thickness_um": round(
                    thickness,
                    2,
                ),

                "spread_rate_mm_s": round(
                    spread_rate,
                    4,
                ),

                "component_width_px": (
                    width
                ),

                "component_height_px": (
                    height
                ),

                "component_size_px": (
                    size
                ),
            }
        )

    points.sort(
        key=lambda item: (
            item["thickness_um"]
        )
    )

    return points


# ---------------------------------------------------------
# Red mask
# ---------------------------------------------------------


def build_red_mask(
    array: np.ndarray,
) -> np.ndarray:

    rgb = array.astype(
        np.int16
    )

    red = rgb[:, :, 0]
    green = rgb[:, :, 1]
    blue = rgb[:, :, 2]

    return (
        (red >= 150)
        & ((red - green) >= 60)
        & ((red - blue) >= 60)
    )


# ---------------------------------------------------------
# Open-circle detector
#
# Continuous red curve should only intersect a few angular
# directions around a candidate center.
#
# A genuine open circle should cover most directions around
# its centre.
# ---------------------------------------------------------


def calculate_ring_coverage(
    red_mask: np.ndarray,
) -> np.ndarray:

    # Slight dilation tolerates:
    # JPEG anti-aliasing,
    # broken ring pixels,
    # thin marker outlines.
    tolerant_mask = dilate_mask(
        red_mask,
        radius=1,
    )

    angle_count = 32

    angles = np.linspace(
        0.0,
        2.0 * math.pi,
        angle_count,
        endpoint=False,
    )

    # Red circle marker radius in this
    # extracted Figure 2.21 image.
    #
    # Multiple radii provide tolerance
    # for anti-aliasing and marker size.
    radii = (
        10,
        12,
        14,
        16,
        18,
    )

    coverage = np.zeros(
        red_mask.shape,
        dtype=np.uint8,
    )

    for angle in angles:

        angle_hit = np.zeros(
            red_mask.shape,
            dtype=bool,
        )

        cosine = math.cos(
            angle
        )

        sine = math.sin(
            angle
        )

        for radius in radii:

            dx = int(
                round(
                    cosine
                    * radius
                )
            )

            dy = int(
                round(
                    sine
                    * radius
                )
            )

            angle_hit |= sample_shift(
                tolerant_mask,
                dx,
                dy,
            )

        coverage += (
            angle_hit.astype(
                np.uint8
            )
        )

    return (
        coverage.astype(
            np.float32
        )
        / float(
            angle_count
        )
    )


def non_maximum_suppression(
    candidates: list[dict],
    minimum_distance: float,
) -> list[dict]:

    candidates = sorted(
        candidates,
        key=lambda item: (
            item["score"]
        ),
        reverse=True,
    )

    selected: list[dict] = []

    for candidate in candidates:

        keep = True

        for existing in selected:

            distance = math.hypot(
                candidate["pixel_x"]
                - existing["pixel_x"],

                candidate["pixel_y"]
                - existing["pixel_y"],
            )

            if (
                distance
                < minimum_distance
            ):
                keep = False
                break

        if keep:

            selected.append(
                candidate
            )

    return selected


def detect_red_open_points(
    array: np.ndarray,
    bounds: dict,
    x_axis: dict,
    y_axis: dict,
) -> tuple[
    list[dict],
    np.ndarray,
]:

    left = int(
        bounds["left_px"]
    )

    right = int(
        bounds["right_px"]
    )

    top = int(
        bounds["top_px"]
    )

    bottom = int(
        bounds["bottom_px"]
    )

    red_mask = build_red_mask(
        array
    )

    coverage = calculate_ring_coverage(
        red_mask
    )

    # A continuous line usually covers only a
    # small number of directions.
    #
    # A circular marker has high angular coverage.
    threshold = 0.58

    search = (
        coverage >= threshold
    )

    # Limit search strictly to plot area.
    valid_area = np.zeros_like(
        search,
        dtype=bool,
    )

    margin = 8

    valid_area[
        top + margin:
        bottom - margin + 1,

        left + margin:
        right - margin + 1,
    ] = True

    search &= valid_area

    ys, xs = np.where(
        search
    )

    candidates = []

    for pixel_y, pixel_x in zip(
        ys.tolist(),
        xs.tolist(),
    ):

        # Ignore legend.
        if (
            pixel_x > 900
            and pixel_y < 220
        ):
            continue

        thickness = pixel_to_value(
            pixel_x,
            x_axis,
        )

        spread_rate = pixel_to_value(
            pixel_y,
            y_axis,
        )

        if not (
            5.0
            <= thickness
            <= 795.0
            and 0.02
            <= spread_rate
            <= 9.95
        ):
            continue

        candidates.append(
            {
                "pixel_x": (
                    float(
                        pixel_x
                    )
                ),

                "pixel_y": (
                    float(
                        pixel_y
                    )
                ),

                "score": (
                    float(
                        coverage[
                            pixel_y,
                            pixel_x,
                        ]
                    )
                ),
            }
        )

    selected = (
        non_maximum_suppression(
            candidates,
            minimum_distance=25.0,
        )
    )

    results = []

    for item in selected:

        thickness = pixel_to_value(
            item["pixel_x"],
            x_axis,
        )

        spread_rate = pixel_to_value(
            item["pixel_y"],
            y_axis,
        )

        results.append(
            {
                "pixel_x": round(
                    item["pixel_x"],
                    2,
                ),

                "pixel_y": round(
                    item["pixel_y"],
                    2,
                ),

                "thickness_um": round(
                    thickness,
                    2,
                ),

                "spread_rate_mm_s": round(
                    spread_rate,
                    4,
                ),

                "ring_coverage": round(
                    item["score"],
                    4,
                ),
            }
        )

    results.sort(
        key=lambda item: (
            item["thickness_um"]
        )
    )

    return (
        results,
        coverage,
    )


# ---------------------------------------------------------
# Debug images
# ---------------------------------------------------------


def save_debug_masks(
    output_dir,
    blue_mask: np.ndarray,
    red_coverage: np.ndarray,
):

    blue_image = Image.fromarray(
        (
            blue_mask.astype(
                np.uint8
            )
            * 255
        )
    )

    blue_image.save(
        output_dir
        / "debug_blue_mask.png"
    )

    coverage_image = Image.fromarray(
        np.clip(
            red_coverage
            * 255.0,
            0,
            255,
        ).astype(
            np.uint8
        )
    )

    coverage_image.save(
        output_dir
        / "debug_red_ring_score.png"
    )


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------


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

    metadata_path = (
        root
        / "digitization"
        / "figure_2_21"
        / "calibration_metadata.json"
    )

    output_dir = (
        root
        / "digitization"
        / "figure_2_21"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not image_path.exists():

        raise FileNotFoundError(
            f"Missing Figure 2.21 image: "
            f"{image_path}"
        )

    if not metadata_path.exists():

        raise FileNotFoundError(
            f"Missing calibration metadata: "
            f"{metadata_path}"
        )

    metadata = json.loads(
        metadata_path.read_text(
            encoding="utf-8"
        )
    )

    bounds = metadata[
        "pixel_bounds"
    ]

    x_axis = metadata[
        "x_axis"
    ]

    y_axis = metadata[
        "y_axis"
    ]

    image = Image.open(
        image_path
    ).convert(
        "RGB"
    )

    array = np.asarray(
        image
    )

    blue_mask = build_blue_mask(
        array
    )

    blue_points = detect_blue_points(
        array=array,
        bounds=bounds,
        x_axis=x_axis,
        y_axis=y_axis,
    )

    (
        red_points,
        red_coverage,
    ) = detect_red_open_points(
        array=array,
        bounds=bounds,
        x_axis=x_axis,
        y_axis=y_axis,
    )

    save_debug_masks(
        output_dir=output_dir,
        blue_mask=blue_mask,
        red_coverage=red_coverage,
    )

    warnings = []

    # These are visual sanity ranges,
    # NOT scientific acceptance criteria.
    if not (
        3
        <= len(blue_points)
        <= 6
    ):
        warnings.append(
            "Blue experimental marker count "
            "is outside the visually expected "
            "review range of 3-6."
        )

    if not (
        7
        <= len(red_points)
        <= 12
    ):
        warnings.append(
            "Red open-circle count is outside "
            "the visually expected review range "
            "of 7-12."
        )

    result = {
        "source_id": SOURCE_ID,

        "figure_ref": "2.21",

        "detector_version": "2.0",

        "status": (
            "needs_overlay_review"
        ),

        "important_note": (
            "Detected points remain preview "
            "evidence until human overlay "
            "verification passes."
        ),

        "calibration": {
            "pixel_bounds": (
                bounds
            ),

            "x_axis": (
                x_axis
            ),

            "y_axis": (
                y_axis
            ),
        },

        "series": {
            "microgravity": {
                "evidence_type": (
                    "experimental"
                ),

                "training_eligible": (
                    False
                ),

                "marker": (
                    "blue filled circle"
                ),

                "point_count": len(
                    blue_points
                ),

                "points": (
                    blue_points
                ),
            },

            "downward": {
                "evidence_type": (
                    "experimental"
                ),

                "training_eligible": (
                    False
                ),

                "marker": (
                    "red open circle"
                ),

                "point_count": len(
                    red_points
                ),

                "points": (
                    red_points
                ),
            },

            "thin_behavior_curve": {
                "evidence_type": (
                    "theoretical"
                ),

                "training_eligible": (
                    False
                ),

                "digitized": (
                    False
                ),

                "reason": (
                    "Continuous theoretical curve "
                    "must remain separate from "
                    "experimental markers."
                ),
            },
        },

        "review_warnings": (
            warnings
        ),
    }

    json_path = (
        output_dir
        / "point_detection_preview.json"
    )

    json_path.write_text(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    # -----------------------------------------------------
    # Overlay
    # -----------------------------------------------------

    overlay = image.copy()

    draw = ImageDraw.Draw(
        overlay
    )

    # Blue experimental detections:
    # green circle around marker.
    for index, point in enumerate(
        blue_points,
        start=1,
    ):

        x = point[
            "pixel_x"
        ]

        y = point[
            "pixel_y"
        ]

        radius = 13

        draw.ellipse(
            (
                x - radius,
                y - radius,
                x + radius,
                y + radius,
            ),

            outline=(
                0,
                170,
                0,
            ),

            width=3,
        )

        draw.text(
            (
                x + 15,
                y - 12,
            ),
            f"B{index}",
            fill=(
                0,
                130,
                0,
            ),
        )

    # Red open-circle detections:
    # purple square around marker.
    for index, point in enumerate(
        red_points,
        start=1,
    ):

        x = point[
            "pixel_x"
        ]

        y = point[
            "pixel_y"
        ]

        radius = 14

        draw.rectangle(
            (
                x - radius,
                y - radius,
                x + radius,
                y + radius,
            ),

            outline=(
                150,
                0,
                255,
            ),

            width=3,
        )

        draw.text(
            (
                x + 16,
                y + 4,
            ),
            f"R{index}",
            fill=(
                130,
                0,
                220,
            ),
        )

    overlay_path = (
        output_dir
        / "point_detection_overlay.png"
    )

    overlay.save(
        overlay_path
    )

    # -----------------------------------------------------
    # Terminal summary
    # -----------------------------------------------------

    print()
    print(
        "FIGURE 2.21 POINT DETECTION V2"
    )

    print(
        "------------------------------"
    )

    print()
    print(
        "MICROGRAVITY"
    )

    print(
        f"Detected: "
        f"{len(blue_points)}"
    )

    for point in blue_points:

        print(
            f"  "
            f"{point['thickness_um']:>7.2f} µm"
            f" -> "
            f"{point['spread_rate_mm_s']:.4f} mm/s"
        )

    print()
    print(
        "DOWNWARD"
    )

    print(
        f"Detected: "
        f"{len(red_points)}"
    )

    for point in red_points:

        print(
            f"  "
            f"{point['thickness_um']:>7.2f} µm"
            f" -> "
            f"{point['spread_rate_mm_s']:.4f} mm/s"
            f" "
            f"(coverage="
            f"{point['ring_coverage']:.3f})"
        )

    print()
    print(
        "THEORETICAL CURVE"
    )

    print(
        "  excluded"
    )

    if warnings:

        print()
        print(
            "REVIEW WARNINGS"
        )

        for warning in warnings:

            print(
                f"  - {warning}"
            )

    print()
    print(
        f"JSON:"
    )

    print(
        f"  {json_path}"
    )

    print()
    print(
        f"Overlay:"
    )

    print(
        f"  {overlay_path}"
    )

    print()
    print(
        "Debug:"
    )

    print(
        f"  "
        f"{output_dir / 'debug_blue_mask.png'}"
    )

    print(
        f"  "
        f"{output_dir / 'debug_red_ring_score.png'}"
    )

    print()
    print(
        "IMPORTANT:"
    )

    print(
        "Do not promote these points to "
        "training data until overlay review."
    )


if __name__ == "__main__":
    main()