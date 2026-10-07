import pytest

from pydantic import ValidationError

from app.schemas.figure_digitization import (
    FigureDigitizationManifest,
    FigurePanel,
    FigureSeries,
    PixelBounds,
)


def test_figure_manifest():

    manifest = FigureDigitizationManifest(
        digitization_id="DIG-TEST",
        source_id="SRC-001",
        source_page=48,
        figure_ref="2.19",
        image_path="figure.jpeg",
        image_sha256="a" * 64,
        image_width_px=2596,
        image_height_px=820,
        figure_role="experimental",

        panels=[
            FigurePanel(
                panel_id="B",
                label=(
                    "Spread rate versus time"
                ),
                pixel_bounds=PixelBounds(
                    left_px=1483,
                    right_px=2563,
                    top_px=27,
                    bottom_px=670,
                ),
                series=[
                    FigureSeries(
                        series_id=(
                            "microgravity"
                        ),
                        label=(
                            "Microgravity"
                        ),
                        gravity_regime=(
                            "microgravity"
                        ),
                    )
                ],
            )
        ],
    )

    assert (
        manifest.figure_ref
        == "2.19"
    )

    assert len(
        manifest.panels
    ) == 1

    assert (
        manifest.panels[0]
        .pixel_bounds.left_px
        == 1483
    )


def test_invalid_pixel_bounds():

    with pytest.raises(
        ValidationError
    ):
        PixelBounds(
            left_px=1000,
            right_px=500,
            top_px=20,
            bottom_px=600,
        )