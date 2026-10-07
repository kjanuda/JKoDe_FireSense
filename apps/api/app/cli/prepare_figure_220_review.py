from PIL import Image

from app.core.paths import FIGURES_DATA_DIR


SOURCE_ID = "SRC-NASA-20210011385"


def main():

    input_path = (
        FIGURES_DATA_DIR
        / SOURCE_ID
        / "embedded"
        / "page_049_image_01.jpeg"
    )

    if not input_path.exists():
        raise FileNotFoundError(
            f"Missing Figure 2.20 image: {input_path}"
        )

    output_dir = (
        FIGURES_DATA_DIR
        / SOURCE_ID
        / "digitization"
        / "figure_2_20"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    image = Image.open(
        input_path
    ).convert("RGB")

    enlarged = image.resize(
        (
            image.width * 2,
            image.height * 2,
        ),
        resample=Image.Resampling.LANCZOS,
    )

    output_path = (
        output_dir
        / "figure_2_20_2x.png"
    )

    enlarged.save(
        output_path
    )

    print()
    print(
        "FIGURE 2.20 REVIEW IMAGE"
    )
    print(
        "------------------------"
    )

    print(
        f"Original : "
        f"{image.width} x {image.height}"
    )

    print(
        f"Enlarged : "
        f"{enlarged.width} x {enlarged.height}"
    )

    print(
        f"Saved    : "
        f"{output_path}"
    )


if __name__ == "__main__":
    main()