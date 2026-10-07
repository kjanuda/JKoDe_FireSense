import pymupdf

from app.core.paths import (
    FIGURES_DATA_DIR,
    RAW_DATA_DIR,
)


SOURCE_ID = "SRC-NASA-20210011385"

TARGET_PAGES = (
    50,
    51,
)


def render_page(
    document,
    page_number: int,
    output_dir,
):

    page_index = (
        page_number - 1
    )

    if (
        page_index < 0
        or page_index >= len(document)
    ):
        raise ValueError(
            f"PDF page {page_number} "
            f"is outside document range."
        )

    page = document.load_page(
        page_index
    )

    matrix = pymupdf.Matrix(
        3.0,
        3.0,
    )

    pixmap = page.get_pixmap(
        matrix=matrix,
        alpha=False,
    )

    output_path = (
        output_dir
        / f"page_{page_number:03d}_3x.png"
    )

    pixmap.save(
        str(output_path)
    )

    print(
        f"Page {page_number}: "
        f"{pixmap.width} x {pixmap.height}"
    )

    print(
        f"Saved: {output_path}"
    )


def main():

    pdf_path = (
        RAW_DATA_DIR
        / f"{SOURCE_ID}.pdf"
    )

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"NASA PDF not found: "
            f"{pdf_path}"
        )

    output_dir = (
        FIGURES_DATA_DIR
        / SOURCE_ID
        / "digitization"
        / "figures_2_21_2_22"
        / "review"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    document = pymupdf.open(
        pdf_path
    )

    print()
    print(
        "FIGURES 2.21 / 2.22 REVIEW"
    )
    print(
        "--------------------------"
    )

    print(
        f"PDF pages: {len(document)}"
    )

    print()

    for page_number in TARGET_PAGES:

        render_page(
            document=document,
            page_number=page_number,
            output_dir=output_dir,
        )

        print()

    document.close()

    print(
        "Review images ready."
    )


if __name__ == "__main__":
    main()