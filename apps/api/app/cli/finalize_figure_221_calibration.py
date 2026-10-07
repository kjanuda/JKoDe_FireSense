import json

from app.core.paths import FIGURES_DATA_DIR


SOURCE_ID = "SRC-NASA-20210011385"


def main():

    figure_dir = (
        FIGURES_DATA_DIR
        / SOURCE_ID
        / "digitization"
        / "figure_2_21"
    )

    metadata_path = (
        figure_dir
        / "calibration_metadata.json"
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

    metadata["pixel_bounds"] = {
        "left_px": 140,
        "right_px": 1932,
        "top_px": 28,
        "bottom_px": 855,
    }

    metadata["x_axis"] = {
        "label": "Fuel thickness",
        "unit": "µm",
        "scale": "linear",
        "pixel_min": 140,
        "pixel_max": 1932,
        "value_min": 0.0,
        "value_max": 800.0,
    }

    # Pixel coordinates increase downward.
    # Therefore 0 mm/s is at bottom,
    # and 10 mm/s is at top.
    metadata["y_axis"] = {
        "label": "Spread rate",
        "unit": "mm/s",
        "scale": "linear",
        "pixel_min": 855,
        "pixel_max": 28,
        "value_min": 0.0,
        "value_max": 10.0,
    }

    metadata["manual_calibration_clicks"] = {
        "x_left": {
            "x": 140,
            "y": 854,
        },
        "x_right": {
            "x": 1932,
            "y": 835,
        },
        "y_top": {
            "x": 139,
            "y": 28,
        },
        "y_bottom": {
            "x": 139,
            "y": 856,
        },
    }

    metadata["calibration_notes"] = [
        (
            "X-axis uses x coordinates only; "
            "x_right vertical click offset does "
            "not affect x calibration."
        ),
        (
            "Bottom plot boundary standardized "
            "to 855 px from manual clicks at "
            "854 and 856 px."
        ),
    ]

    metadata["status"] = (
        "axis_calibrated"
    )

    metadata_path.write_text(
        json.dumps(
            metadata,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print()
    print(
        "FIGURE 2.21 AXIS CALIBRATION"
    )
    print(
        "----------------------------"
    )

    print(
        "Pixel bounds:"
    )

    print(
        "  left   : 140"
    )

    print(
        "  right  : 1932"
    )

    print(
        "  top    : 28"
    )

    print(
        "  bottom : 855"
    )

    print()

    print(
        "X axis:"
    )

    print(
        "  0 -> 800 µm"
    )

    print()

    print(
        "Y axis:"
    )

    print(
        "  0 -> 10 mm/s"
    )

    print()

    print(
        "Status: axis_calibrated"
    )

    print(
        f"Saved : {metadata_path}"
    )


if __name__ == "__main__":
    main()