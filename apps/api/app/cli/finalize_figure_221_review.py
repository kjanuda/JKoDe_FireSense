import json

from PIL import Image, ImageDraw, ImageFont

from app.core.paths import FIGURES_DATA_DIR


SOURCE_ID = "SRC-NASA-20210011385"
IMAGE_NAME = "page_050_image_01.jpeg"


# Human-reviewed marker centres.
#
# Values are intentionally stored as pixels first.
# Scientific values are recomputed from the locked
# Figure 2.21 calibration at runtime.
MICROGRAVITY_PIXELS = [
    (368.33, 664.24),
    (590.77, 760.26),
    (815.88, 788.49),
    (1036.97, 827.68),
]


DOWNWARD_PIXELS = [
    (196.33, 114.00),
    (241.33, 316.00),
    (256.33, 365.00),
    (312.33, 534.00),
    (365.00, 685.00),
    (589.00, 782.00),
    (816.00, 807.00),
    (1041.00, 819.00),
    (1817.33, 840.00),
]


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


def build_points(
    pixels: list[tuple[float, float]],
    x_axis: dict,
    y_axis: dict,
) -> list[dict]:

    points = []

    for pixel_x, pixel_y in pixels:

        thickness_um = pixel_to_value(
            pixel_x,
            x_axis,
        )

        spread_rate_mm_s = pixel_to_value(
            pixel_y,
            y_axis,
        )

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
                    thickness_um,
                    3,
                ),
                "spread_rate_mm_s": round(
                    spread_rate_mm_s,
                    4,
                ),
            }
        )

    points.sort(
        key=lambda item: (
            item["thickness_um"]
        )
    )

    return points


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

    figure_dir = (
        root
        / "digitization"
        / "figure_2_21"
    )

    metadata_path = (
        figure_dir
        / "calibration_metadata.json"
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

    x_axis = metadata[
        "x_axis"
    ]

    y_axis = metadata[
        "y_axis"
    ]

    microgravity_points = build_points(
        MICROGRAVITY_PIXELS,
        x_axis,
        y_axis,
    )

    downward_points = build_points(
        DOWNWARD_PIXELS,
        x_axis,
        y_axis,
    )

    result = {
        "source_id": SOURCE_ID,

        "figure_ref": "2.21",

        "source_image": IMAGE_NAME,

        "source_image_sha256": (
            "39b56d57117cd3d03a1cce2414f122a"
            "910c738a28e6a6f308c3231313cc52b30"
        ),

        "extraction_method": (
            "human_reviewed_figure_digitization"
        ),

        "calibration_status": (
            "axis_calibrated_visual_pass"
        ),

        "verification_status": (
            "needs_final_overlay_review"
        ),

        "theoretical_curve_included": False,

        "series": {
            "microgravity": {
                "gravity_regime": (
                    "microgravity"
                ),

                "evidence_type": (
                    "experimental"
                ),

                "marker": (
                    "blue filled circle"
                ),

                "point_count": len(
                    microgravity_points
                ),

                "points": (
                    microgravity_points
                ),
            },

            "downward": {
                "gravity_regime": (
                    "normal_gravity"
                ),

                "evidence_type": (
                    "experimental"
                ),

                "marker": (
                    "red open circle"
                ),

                "point_count": len(
                    downward_points
                ),

                "points": (
                    downward_points
                ),
            },

            "thin_behavior_curve": {
                "evidence_type": (
                    "theoretical"
                ),

                "included_in_experimental_data": (
                    False
                ),
            },
        },

        "source_reported_context": {
            "note": (
                "The report also explicitly states "
                "an experimental thin-fuel value of "
                "2.2 mm/s for tau = 50 µm. Keep that "
                "source-reported evidence separate from "
                "the Figure 2.21 digitized values."
            )
        },

        "review_notes": [
            (
                "Figure calibration was visually "
                "validated before point extraction."
            ),
            (
                "Microgravity markers were recovered "
                "from blue filled-circle pixel regions."
            ),
            (
                "Downward points are red open-circle "
                "experimental markers."
            ),
            (
                "The continuous red theoretical curve "
                "is explicitly excluded."
            ),
        ],
    }

    json_path = (
        figure_dir
        / "figure_2_21_final_review.json"
    )

    json_path.write_text(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    # --------------------------------------------------
    # Overlay
    # --------------------------------------------------

    image = Image.open(
        image_path
    ).convert("RGB")

    overlay = image.copy()

    draw = ImageDraw.Draw(
        overlay
    )

    # Green circle = reviewed microgravity point.
    for index, point in enumerate(
        microgravity_points,
        start=1,
    ):

        x = point["pixel_x"]
        y = point["pixel_y"]

        radius = 14

        draw.ellipse(
            (
                x - radius,
                y - radius,
                x + radius,
                y + radius,
            ),
            outline=(0, 180, 0),
            width=4,
        )

        draw.text(
            (
                x + 16,
                y - 18,
            ),
            f"M{index}",
            fill=(0, 130, 0),
        )

    # Purple square = reviewed downward point.
    for index, point in enumerate(
        downward_points,
        start=1,
    ):

        x = point["pixel_x"]
        y = point["pixel_y"]

        radius = 14

        draw.rectangle(
            (
                x - radius,
                y - radius,
                x + radius,
                y + radius,
            ),
            outline=(150, 0, 255),
            width=4,
        )

        draw.text(
            (
                x + 16,
                y + 3,
            ),
            f"D{index}",
            fill=(130, 0, 220),
        )

    overlay_path = (
        figure_dir
        / "figure_2_21_final_overlay.png"
    )

    overlay.save(
        overlay_path
    )

    print()
    print(
        "FIGURE 2.21 FINAL REVIEW"
    )
    print(
        "------------------------"
    )

    print()
    print(
        "MICROGRAVITY"
    )

    print(
        f"Points: "
        f"{len(microgravity_points)}"
    )

    for point in microgravity_points:

        print(
            f"  "
            f"{point['thickness_um']:>8.3f} µm"
            f" -> "
            f"{point['spread_rate_mm_s']:.4f} mm/s"
        )

    print()
    print(
        "DOWNWARD"
    )

    print(
        f"Points: "
        f"{len(downward_points)}"
    )

    for point in downward_points:

        print(
            f"  "
            f"{point['thickness_um']:>8.3f} µm"
            f" -> "
            f"{point['spread_rate_mm_s']:.4f} mm/s"
        )

    print()
    print(
        "Theoretical curve:"
    )

    print(
        "  EXCLUDED"
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
        "STATUS:"
    )

    print(
        "  needs_final_overlay_review"
    )


if __name__ == "__main__":
    main()