import pymupdf

from app.core.paths import (
    FIGURES_DATA_DIR,
    RAW_DATA_DIR,
)


SOURCE_ID = "SRC-NASA-20210011385"


def render_page(
    document,
    page_number_1_based: int,
    output_dir,
):

    page_index = (
        page_number_1_based - 1
    )

    if (
        page_index < 0
        or page_index >= len(document)
    ):
        raise ValueError(
            f"Page {page_number_1_based} "
            f"is outside PDF range."
        )

    page = document.load_page(
        page_index
    )

    # High resolution:
    # 3x scale is enough for table text.
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
        / (
            f"appendix_page_"
            f"{page_number_1_based:03d}"
            f"_3x.png"
        )
    )

    pixmap.save(
        str(output_path)
    )

    print(
        f"Rendered PDF page "
        f"{page_number_1_based}: "
        f"{output_path}"
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
        / "appendix"
        / "test_matrix"
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
        "APPENDIX TEST MATRIX RENDER"
    )
    print(
        "---------------------------"
    )

    print(
        f"PDF pages: {len(document)}"
    )

    print()

    # Docling reported tables on
    # pages 111 and 112.
    for page_number in (
        111,
        112,
    ):
        render_page(
            document=document,
            page_number_1_based=page_number,
            output_dir=output_dir,
        )

    document.close()

    print()
    print(
        "Render complete."
    )


if __name__ == "__main__":
    main()