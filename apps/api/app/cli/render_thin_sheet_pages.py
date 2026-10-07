import fitz

from app.core.paths import (
    FIGURES_DATA_DIR,
    RAW_DATA_DIR,
)


SOURCE_ID = "SRC-NASA-20210011385"


PAGES = (
    29,
    30,
    31,
    32,
    33,
    34,
    35,
    45,
    46,
    47,
    48,
    49,
    50,
    51,
    52,
)


def main():

    pdf_path = (
        RAW_DATA_DIR
        / f"{SOURCE_ID}.pdf"
    )

    output_dir = (
        FIGURES_DATA_DIR
        / SOURCE_ID
        / "pages"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    document = fitz.open(
        pdf_path
    )

    zoom = 2.0

    matrix = fitz.Matrix(
        zoom,
        zoom,
    )

    for page_number in PAGES:

        # PyMuPDF is zero-based.
        page = document[
            page_number - 1
        ]

        pixmap = page.get_pixmap(
            matrix=matrix,
            alpha=False,
        )

        output_path = (
            output_dir
            / (
                f"page_"
                f"{page_number:03d}.png"
            )
        )

        pixmap.save(
            output_path
        )

        print(
            f"Rendered page "
            f"{page_number}: "
            f"{output_path}"
        )

    document.close()

    print()
    print(
        "PAGE RENDER COMPLETE"
    )


if __name__ == "__main__":
    main()