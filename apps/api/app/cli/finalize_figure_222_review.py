import json
import math
from pathlib import Path

from PIL import Image, ImageDraw

from app.core.paths import FIGURES_DATA_DIR


SOURCE_ID = "SRC-NASA-20210011385"
IMAGE_NAME = "page_051_image_01.jpeg"


EXPECTED_COUNTS = {
    "mrc": 2,
    "vcf": 5,
    "astra": 1,
    "nasa": 3,
    "bass": 4,
    "ridout": 4,
    "fernandez_pello_williams": 14,
}


SERIES_SHORT_NAMES = {
    "mrc": "MRC",
    "vcf": "VCF",
    "astra": "AST",
    "nasa": "NASA",
    "bass": "BASS",
    "ridout": "RID",
    "fernandez_pello_williams": "FPW",
}


def load_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(
            f"Missing required file: {path}"
        )

    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


def pixel_to_x(
    pixel_x: float,
    metadata: dict,
) -> float:

    axis = metadata["x_axis"]

    pixel_left = float(
        axis["pixel_left"]
    )

    pixel_right = float(
        axis["pixel_right"]
    )

    value_min = float(
        axis["value_min"]
    )

    value_max = float(
        axis["value_max"]
    )

    fraction = (
        pixel_x - pixel_left
    ) / (
        pixel_right - pixel_left
    )

    log_min = math.log10(
        value_min
    )

    log_max = math.log10(
        value_max
    )

    log_value = (
        log_min
        + fraction
        * (
            log_max - log_min
        )
    )

    return 10 ** log_value


def pixel_to_y(
    pixel_y: float,
    metadata: dict,
) -> float:

    axis = metadata["y_axis"]

    high_value = float(
        axis["reference_value_high"]
    )

    high_pixel = float(
        axis["reference_pixel_high"]
    )

    low_value = float(
        axis["reference_value_low"]
    )

    low_pixel = float(
        axis["reference_pixel_low"]
    )

    fraction = (
        pixel_y - high_pixel
    ) / (
        low_pixel - high_pixel
    )

    log_high = math.log10(
        high_value
    )

    log_low = math.log10(
        low_value
    )

    log_value = (
        log_high
        - fraction
        * (
            log_high - log_low
        )
    )

    return 10 ** log_value


def validate_payload(
    payload: dict,
    calibration: dict,
) -> tuple[list[str], list[str]]:

    errors = []
    warnings = []

    if (
        payload.get("source_id")
        != SOURCE_ID
    ):
        errors.append(
            "Unexpected source_id."
        )

    if (
        payload.get("figure_ref")
        != "2.22"
    ):
        errors.append(
            "Unexpected figure_ref."
        )

    if payload.get(
        "theoretical_curves_included"
    ):
        errors.append(
            "Theoretical curves must not "
            "be included."
        )

    if (
        payload.get(
            "calibration_status"
        )
        != "axis_calibrated_visual_pass"
    ):
        errors.append(
            "Calibration is not marked "
            "axis_calibrated_visual_pass."
        )

    plot = calibration[
        "plot_bounds"
    ]

    left = float(
        plot["left"]
    )

    right = float(
        plot["right"]
    )

    top = float(
        plot["top"]
    )

    bottom = float(
        plot["bottom"]
    )

    series = payload.get(
        "series",
        {},
    )

    for (
        series_id,
        expected_count,
    ) in EXPECTED_COUNTS.items():

        if series_id not in series:
            errors.append(
                f"Missing series: {series_id}"
            )
            continue

        series_data = series[
            series_id
        ]

        points = series_data.get(
            "points",
            [],
        )

        declared_count = (
            series_data.get(
                "point_count"
            )
        )

        if (
            declared_count
            != len(points)
        ):
            errors.append(
                f"{series_id}: point_count "
                "does not match points array."
            )

        if (
            len(points)
            != expected_count
        ):
            errors.append(
                f"{series_id}: expected "
                f"{expected_count} points, "
                f"found {len(points)}."
            )

        previous_thickness = None

        for index, point in enumerate(
            points,
            start=1,
        ):

            pixel_x = float(
                point["pixel_x"]
            )

            pixel_y = float(
                point["pixel_y"]
            )

            if not (
                left <= pixel_x <= right
                and
                top <= pixel_y <= bottom
            ):
                errors.append(
                    f"{series_id} point "
                    f"{index} is outside "
                    "the calibrated plot."
                )

            calculated_x = (
                pixel_to_x(
                    pixel_x,
                    calibration,
                )
            )

            calculated_y = (
                pixel_to_y(
                    pixel_y,
                    calibration,
                )
            )

            stored_x = float(
                point[
                    "thickness_um"
                ]
            )

            stored_y = float(
                point[
                    "spread_rate_mm_s"
                ]
            )

            x_relative_error = (
                abs(
                    calculated_x
                    - stored_x
                )
                / max(
                    calculated_x,
                    1e-12,
                )
            )

            y_relative_error = (
                abs(
                    calculated_y
                    - stored_y
                )
                / max(
                    calculated_y,
                    1e-12,
                )
            )

            if (
                x_relative_error
                > 0.001
            ):
                errors.append(
                    f"{series_id} point "
                    f"{index}: x conversion "
                    "does not match calibration."
                )

            if (
                y_relative_error
                > 0.001
            ):
                errors.append(
                    f"{series_id} point "
                    f"{index}: y conversion "
                    "does not match calibration."
                )

            if stored_x <= 0:
                errors.append(
                    f"{series_id} point "
                    f"{index}: non-positive "
                    "thickness."
                )

            if stored_y <= 0:
                errors.append(
                    f"{series_id} point "
                    f"{index}: non-positive "
                    "spread rate."
                )

            if (
                previous_thickness
                is not None
                and
                stored_x
                <= previous_thickness
            ):
                errors.append(
                    f"{series_id}: points "
                    "are not strictly ordered "
                    "by thickness."
                )

            previous_thickness = (
                stored_x
            )

        # Same-series click duplication check.
        for i in range(
            len(points)
        ):
            for j in range(
                i + 1,
                len(points)
            ):

                dx = (
                    float(
                        points[i][
                            "pixel_x"
                        ]
                    )
                    - float(
                        points[j][
                            "pixel_x"
                        ]
                    )
                )

                dy = (
                    float(
                        points[i][
                            "pixel_y"
                        ]
                    )
                    - float(
                        points[j][
                            "pixel_y"
                        ]
                    )
                )

                distance = math.hypot(
                    dx,
                    dy,
                )

                if distance < 5.0:
                    warnings.append(
                        f"{series_id}: points "
                        f"{i + 1} and "
                        f"{j + 1} are within "
                        "5 px. Review possible "
                        "duplicate."
                    )

    return errors, warnings


def main():

    root = (
        FIGURES_DATA_DIR
        / SOURCE_ID
    )

    figure_dir = (
        root
        / "digitization"
        / "figure_2_22"
    )

    image_path = (
        root
        / "embedded"
        / "figures_2_21_2_22"
        / IMAGE_NAME
    )

    manual_path = (
        figure_dir
        / "manual_digitization.json"
    )

    calibration_path = (
        figure_dir
        / "calibration_metadata.json"
    )

    final_json_path = (
        figure_dir
        / "figure_2_22_final_review.json"
    )

    validation_path = (
        figure_dir
        / "figure_2_22_final_validation.json"
    )

    overlay_path = (
        figure_dir
        / "figure_2_22_final_overlay.png"
    )

    payload = load_json(
        manual_path
    )

    calibration = load_json(
        calibration_path
    )

    if not image_path.exists():
        raise FileNotFoundError(
            f"Missing image: {image_path}"
        )

    errors, warnings = (
        validate_payload(
            payload,
            calibration,
        )
    )

    # ---------------------------------------
    # Save final-review JSON
    # ---------------------------------------

    final_payload = dict(
        payload
    )

    final_payload[
        "verification_status"
    ] = (
        "needs_final_overlay_review"
    )

    final_payload[
        "review_notes"
    ] = [
        (
            "Figure 2.22 log-axis "
            "calibration passed visual "
            "review."
        ),
        (
            "Only experimental marker "
            "series are included."
        ),
        (
            "Thermally thin and thermally "
            "thick theoretical curves "
            "remain excluded."
        ),
        (
            "Series provenance and "
            "independence still require "
            "review before modeling."
        ),
    ]

    final_json_path.write_text(
        json.dumps(
            final_payload,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    # ---------------------------------------
    # Build overlay
    # ---------------------------------------

    image = Image.open(
        image_path
    ).convert(
        "RGB"
    )

    overlay = image.copy()

    draw = ImageDraw.Draw(
        overlay
    )

    plot = calibration[
        "plot_bounds"
    ]

    draw.rectangle(
        (
            plot["left"],
            plot["top"],
            plot["right"],
            plot["bottom"],
        ),
        outline=(
            0,
            170,
            0,
        ),
        width=3,
    )

    total_points = 0

    for series_id in EXPECTED_COUNTS:

        series_data = (
            payload[
                "series"
            ][
                series_id
            ]
        )

        short_name = (
            SERIES_SHORT_NAMES[
                series_id
            ]
        )

        for index, point in enumerate(
            series_data["points"],
            start=1,
        ):

            total_points += 1

            x = float(
                point["pixel_x"]
            )

            y = float(
                point["pixel_y"]
            )

            radius = 10

            # Magenta box.
            draw.rectangle(
                (
                    x - radius,
                    y - radius,
                    x + radius,
                    y + radius,
                ),
                outline=(
                    220,
                    0,
                    220,
                ),
                width=3,
            )

            # Small center cross.
            draw.line(
                (
                    x - 4,
                    y,
                    x + 4,
                    y,
                ),
                fill=(
                    0,
                    0,
                    0,
                ),
                width=1,
            )

            draw.line(
                (
                    x,
                    y - 4,
                    x,
                    y + 4,
                ),
                fill=(
                    0,
                    0,
                    0,
                ),
                width=1,
            )

            draw.text(
                (
                    x + 12,
                    y - 10,
                ),
                (
                    f"{short_name}"
                    f"{index}"
                ),
                fill=(
                    0,
                    0,
                    0,
                ),
            )

    overlay.save(
        overlay_path
    )

    # ---------------------------------------
    # Validation file
    # ---------------------------------------

    series_counts = {
        series_id: len(
            payload[
                "series"
            ][
                series_id
            ][
                "points"
            ]
        )
        for series_id in (
            EXPECTED_COUNTS
        )
    }

    validation = {
        "source_id": SOURCE_ID,

        "figure_ref": "2.22",

        "series_counts": (
            series_counts
        ),

        "expected_series_counts": (
            EXPECTED_COUNTS
        ),

        "total_point_count": (
            total_points
        ),

        "errors": errors,

        "warnings": warnings,

        "automatic_validation": (
            "pass"
            if not errors
            else "fail"
        ),

        "visual_overlay_status": (
            "needs_human_review"
        ),

        "final_status": (
            "needs_final_overlay_review"
            if not errors
            else
            "automatic_validation_failed"
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

    # ---------------------------------------
    # Terminal output
    # ---------------------------------------

    print()
    print(
        "FIGURE 2.22 FINAL REVIEW"
    )

    print(
        "------------------------"
    )

    print()

    for (
        series_id,
        expected,
    ) in EXPECTED_COUNTS.items():

        actual = (
            series_counts[
                series_id
            ]
        )

        print(
            f"{series_id:<28}"
            f": "
            f"{actual:>2}"
            f" / "
            f"{expected:>2}"
        )

    print()

    print(
        f"Total experimental points : "
        f"{total_points}"
    )

    print(
        f"Automatic errors          : "
        f"{len(errors)}"
    )

    print(
        f"Warnings                  : "
        f"{len(warnings)}"
    )

    if errors:
        print()
        print("ERRORS")
        print("------")

        for error in errors:
            print(
                f"  - {error}"
            )

    if warnings:
        print()
        print("WARNINGS")
        print("--------")

        for warning in warnings:
            print(
                f"  - {warning}"
            )

    print()

    print(
        "Automatic validation:"
    )

    if errors:
        print(
            "  FAIL"
        )
    else:
        print(
            "  PASS"
        )

    print()

    print(
        "Theoretical curves:"
    )

    print(
        "  EXCLUDED"
    )

    print()

    print(
        "Final JSON:"
    )

    print(
        f"  {final_json_path}"
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

    if errors:
        print(
            "  automatic_validation_failed"
        )
    else:
        print(
            "  needs_final_overlay_review"
        )


if __name__ == "__main__":
    main()