from PIL import Image

from app.core.paths import FIGURES_DATA_DIR


SOURCE_ID = "SRC-NASA-20210011385"


def main():

    input_path = (
        FIGURES_DATA_DIR
        / SOURCE_ID
        / "embedded"
        / "page_048_image_02.jpeg"
    )

    if not input_path.exists():
        raise FileNotFoundError(
            f"Missing Figure 2.19 image: {input_path}"
        )

    output_dir = (
        FIGURES_DATA_DIR
        / SOURCE_ID
        / "digitization"
        / "figure_2_19"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    image = Image.open(
        input_path
    ).convert("RGB")

    print(
        f"Source dimensions: "
        f"{image.width} x {image.height}"
    )

    # Keep margins around the graph so
    # axis numbers and titles are visible.
    panel_a_box = (
        0,
        0,
        1370,
        820,
    )

    panel_b_box = (
        1370,
        0,
        2596,
        820,
    )

    panels = {
        "A": panel_a_box,
        "B": panel_b_box,
    }

    for panel_id, box in panels.items():

        crop = image.crop(
            box
        )

        enlarged = crop.resize(
            (
                crop.width * 2,
                crop.height * 2,
            ),
            resample=Image.Resampling.LANCZOS,
        )

        output_path = (
            output_dir
            / f"panel_{panel_id}_2x.png"
        )

        enlarged.save(
            output_path
        )

        print(
            f"Panel {panel_id}: "
            f"{output_path}"
        )

    print()
    print(
        "FIGURE 2.19 PANEL CROPS COMPLETE"
    )


if __name__ == "__main__":
    main()