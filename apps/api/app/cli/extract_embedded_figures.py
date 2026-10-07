import pymupdf

from app.core.paths import (
    FIGURES_DATA_DIR,
    RAW_DATA_DIR,
)


SOURCE_ID = "SRC-NASA-20210011385"

TARGET_PAGES = (
    31,
    32,
    47,
    48,
    49,
)


def main():
    pdf_path = (
        RAW_DATA_DIR
        / f"{SOURCE_ID}.pdf"
    )

    output_dir = (
        FIGURES_DATA_DIR
        / SOURCE_ID
        / "embedded"
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
        "EMBEDDED FIGURE EXTRACTION"
    )
    print(
        "--------------------------"
    )

    total = 0

    for page_number in TARGET_PAGES:

        page = document[
            page_number - 1
        ]

        blocks = page.get_text(
            "dict"
        ).get(
            "blocks",
            []
        )

        image_number = 0

        print()
        print(
            f"Page {page_number}"
        )

        for block in blocks:

            if block.get(
                "type"
            ) != 1:
                continue

            image_data = block.get(
                "image"
            )

            if not image_data:
                continue

            image_number += 1
            total += 1

            extension = block.get(
                "ext",
                "png",
            )

            bbox = block.get(
                "bbox"
            )

            width = block.get(
                "width"
            )

            height = block.get(
                "height"
            )

            filename = (
                f"page_"
                f"{page_number:03d}"
                f"_image_"
                f"{image_number:02d}"
                f".{extension}"
            )

            output_path = (
                output_dir
                / filename
            )

            output_path.write_bytes(
                image_data
            )

            print(
                f"  {filename}"
            )

            print(
                f"    size: "
                f"{width} x {height}"
            )

            print(
                f"    bbox: {bbox}"
            )

    document.close()

    print()
    print(
        f"Total extracted images: "
        f"{total}"
    )

    print(
        f"Output: {output_dir}"
    )


if __name__ == "__main__":
    main()