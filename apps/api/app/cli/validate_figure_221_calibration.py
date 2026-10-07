import json

from PIL import Image, ImageDraw

from app.core.paths import FIGURES_DATA_DIR


SOURCE_ID = "SRC-NASA-20210011385"


def value_to_pixel(
    value: float,
    pixel_min: float,
    pixel_max: float,
    value_min: float,
    value_max: float,
) -> float:

    fraction = (
        value - value_min
    ) / (
        value_max - value_min
    )

    return (
        pixel_min
        + fraction
        * (
            pixel_max
            - pixel_min
        )
    )


def main():

    figure_root = (
        FIGURES_DATA_DIR
        / SOURCE_ID
    )

    image_path = (
        figure_root
        / "embedded"
        / "figures_2_21_2_22"
        / "page_050_image_01.jpeg"
    )

    metadata_path = (
        figure_root
        / "digitization"
        / "figure_2_21"
        / "calibration_metadata.json"
    )

    if not image_path.exists():
        raise FileNotFoundError(
            f"Missing image: {image_path}"
        )

    if not metadata_path.exists():
        raise FileNotFoundError(
            f"Missing metadata: {metadata_path}"
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

    bounds = metadata[
        "pixel_bounds"
    ]

    image = Image.open(
        image_path
    ).convert("RGB")

    overlay = image.copy()

    draw = ImageDraw.Draw(
        overlay
    )

    # -------------------------
    # Plot boundary
    # -------------------------

    draw.rectangle(
        (
            bounds["left_px"],
            bounds["top_px"],
            bounds["right_px"],
            bounds["bottom_px"],
        ),
        outline=(0, 180, 0),
        width=3,
    )

    # -------------------------
    # X tick guides
    # -------------------------

    x_ticks = list(
        range(
            0,
            801,
            100,
        )
    )

    x_results = []

    for tick in x_ticks:

        pixel_x = value_to_pixel(
            value=tick,
            pixel_min=x_axis[
                "pixel_min"
            ],
            pixel_max=x_axis[
                "pixel_max"
            ],
            value_min=x_axis[
                "value_min"
            ],
            value_max=x_axis[
                "value_max"
            ],
        )

        x_results.append(
            {
                "value_um": tick,
                "pixel_x": round(
                    pixel_x,
                    2,
                ),
            }
        )

        x = round(
            pixel_x
        )

        draw.line(
            (
                x,
                bounds["top_px"],
                x,
                bounds["bottom_px"],
            ),
            fill=(0, 120, 255),
            width=2,
        )

        draw.text(
            (
                x + 5,
                bounds[
                    "bottom_px"
                ] - 25,
            ),
            str(tick),
            fill=(0, 120, 255),
        )

    # -------------------------
    # Y tick guides
    # -------------------------

    y_ticks = list(
        range(
            0,
            11,
            2,
        )
    )

    y_results = []

    for tick in y_ticks:

        pixel_y = value_to_pixel(
            value=tick,
            pixel_min=y_axis[
                "pixel_min"
            ],
            pixel_max=y_axis[
                "pixel_max"
            ],
            value_min=y_axis[
                "value_min"
            ],
            value_max=y_axis[
                "value_max"
            ],
        )

        y_results.append(
            {
                "value_mm_s": tick,
                "pixel_y": round(
                    pixel_y,
                    2,
                ),
            }
        )

        y = round(
            pixel_y
        )

        draw.line(
            (
                bounds["left_px"],
                y,
                bounds["right_px"],
                y,
            ),
            fill=(255, 140, 0),
            width=2,
        )

        draw.text(
            (
                bounds[
                    "left_px"
                ] + 5,
                y + 5,
            ),
            str(tick),
            fill=(255, 140, 0),
        )

    output_dir = (
        figure_root
        / "digitization"
        / "figure_2_21"
    )

    overlay_path = (
        output_dir
        / "calibration_overlay.png"
    )

    overlay.save(
        overlay_path
    )

    validation_path = (
        output_dir
        / "calibration_validation.json"
    )

    result = {
        "source_id": SOURCE_ID,
        "figure_ref": "2.21",
        "status": (
            "needs_visual_tick_review"
        ),
        "pixel_bounds": bounds,
        "x_ticks": x_results,
        "y_ticks": y_results,
    }

    validation_path.write_text(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print()
    print(
        "FIGURE 2.21 CALIBRATION CHECK"
    )
    print(
        "-----------------------------"
    )

    print()
    print(
        "X ticks:"
    )

    for item in x_results:

        print(
            f"  {item['value_um']:>3} µm "
            f"-> x={item['pixel_x']:.2f}"
        )

    print()
    print(
        "Y ticks:"
    )

    for item in y_results:

        print(
            f"  {item['value_mm_s']:>2} mm/s "
            f"-> y={item['pixel_y']:.2f}"
        )

    print()
    print(
        f"Overlay: "
        f"{overlay_path}"
    )

    print(
        f"JSON   : "
        f"{validation_path}"
    )

    print()
    print(
        "Review the overlay:"
    )

    print(
        "  blue vertical guides should "
        "match x-axis ticks"
    )

    print(
        "  orange horizontal guides should "
        "match y-axis ticks"
    )

    print(
        "  green rectangle should match "
        "the plotting area"
    )


if __name__ == "__main__":
    main()