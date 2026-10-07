import hashlib
import json

import pymupdf

from app.core.paths import (
    FIGURES_DATA_DIR,
)

from app.schemas.figure_digitization import (
    AxisCalibration,
    FigureDigitizationManifest,
    FigurePanel,
    FigureSeries,
    PixelBounds,
)


SOURCE_ID = "SRC-NASA-20210011385"

FIGURE_REF = "2.19"

IMAGE_FILENAME = (
    "page_048_image_02.jpeg"
)


def calculate_sha256(path) -> str:

    digest = hashlib.sha256()

    with path.open("rb") as file:

        while chunk := file.read(
            1024 * 1024
        ):
            digest.update(chunk)

    return digest.hexdigest()


def build_series():

    return [
        FigureSeries(
            series_id="microgravity",
            label="Microgravity",
            gravity_regime="microgravity",
        ),
        FigureSeries(
            series_id="downward",
            label=(
                "Downward / normal gravity"
            ),
            gravity_regime="normal_gravity",
        ),
    ]


def main():

    image_path = (
        FIGURES_DATA_DIR
        / SOURCE_ID
        / "embedded"
        / IMAGE_FILENAME
    )

    if not image_path.exists():

        raise FileNotFoundError(
            f"Missing figure image: "
            f"{image_path}"
        )

    pixmap = pymupdf.Pixmap(
        str(image_path)
    )

    sha256 = calculate_sha256(
        image_path
    )

    manifest = (
        FigureDigitizationManifest(
            digitization_id=(
                "DIG-SRC-NASA-"
                "20210011385-FIG-2-19"
            ),
            source_id=SOURCE_ID,
            source_page=48,
            figure_ref=FIGURE_REF,
            image_path=(
                image_path.as_posix()
            ),
            image_sha256=sha256,
            image_width_px=pixmap.width,
            image_height_px=pixmap.height,
            figure_role="experimental",

            panels=[
                FigurePanel(
                    panel_id="A",
                    label=(
                        "Leading edge position "
                        "versus time"
                    ),

                    pixel_bounds=PixelBounds(
                        left_px=175,
                        right_px=1262,
                        top_px=18,
                        bottom_px=674,
                    ),

                    x_axis=AxisCalibration(
                        axis="x",
                        scale="linear",
                        pixel_min=175,
                        pixel_max=1262,
                        value_min=0.0,
                        value_max=20.0,
                        unit="s",
                        label="Time",
                    ),

                    y_axis=AxisCalibration(
                        axis="y",
                        scale="linear",

                        # Pixel Y increases downward,
                        # so scientific value 0 is at
                        # the bottom of the plot.
                        pixel_min=674,
                        pixel_max=18,

                        value_min=0.0,
                        value_max=120.0,

                        unit="mm",
                        label="Leading edge position",
                    ),

                    series=build_series(),
                ),

                FigurePanel(
                    panel_id="B",
                    label=(
                        "Spread rate "
                        "versus time"
                    ),

                    pixel_bounds=PixelBounds(
                        left_px=1482,
                        right_px=2570,
                        top_px=19,
                        bottom_px=674,
                    ),

                    x_axis=AxisCalibration(
                        axis="x",
                        scale="linear",
                        pixel_min=1482,
                        pixel_max=2570,
                        value_min=0.0,
                        value_max=20.0,
                        unit="s",
                        label="Time",
                    ),

                    y_axis=AxisCalibration(
                        axis="y",
                        scale="linear",

                        # Pixel Y increases downward,
                        # so scientific value 0 is at
                        # the bottom of the plot.
                        pixel_min=674,
                        pixel_max=19,

                        value_min=0.0,
                        value_max=3.0,

                        unit="mm/s",
                        label="Flame spread rate",
                    ),

                    series=build_series(),
                ),
            ],

            status="needs_series_mapping",

            extraction_method="hybrid",

            notes=(
                "Pixel plot bounds and linear "
                "scientific axis calibrations "
                "were manually assigned from "
                "the embedded Figure 2.19 raster. "
                "Series mapping remains to be "
                "verified."
            ),
        )
    )

    output_dir = (
        FIGURES_DATA_DIR
        / SOURCE_ID
        / "digitization"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        output_dir
        / "figure_2_19.json"
    )

    output_path.write_text(
        json.dumps(
            manifest.model_dump(
                mode="json"
            ),
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print()
    print(
        "FIGURE 2.19 CALIBRATION"
    )
    print(
        "-----------------------"
    )

    print(
        f"Dimensions: "
        f"{pixmap.width} x "
        f"{pixmap.height}"
    )

    for panel in manifest.panels:

        bounds = (
            panel.pixel_bounds
        )

        print()
        print(
            f"Panel {panel.panel_id}: "
            f"{panel.label}"
        )

        print(
            f"  left   : "
            f"{bounds.left_px}"
        )

        print(
            f"  right  : "
            f"{bounds.right_px}"
        )

        print(
            f"  top    : "
            f"{bounds.top_px}"
        )

        print(
            f"  bottom : "
            f"{bounds.bottom_px}"
        )

        if panel.x_axis is not None:

            print(
                f"  X axis : "
                f"{panel.x_axis.value_min} "
                f"to "
                f"{panel.x_axis.value_max} "
                f"{panel.x_axis.unit}"
            )

        if panel.y_axis is not None:

            print(
                f"  Y axis : "
                f"{panel.y_axis.value_min} "
                f"to "
                f"{panel.y_axis.value_max} "
                f"{panel.y_axis.unit}"
            )

    print()
    print(
        f"Status: {manifest.status}"
    )

    print(
        f"Saved : {output_path}"
    )


if __name__ == "__main__":
    main()