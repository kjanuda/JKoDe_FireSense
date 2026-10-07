import hashlib

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


def sha256_file(path):
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def main():

    pdf_path = (
        RAW_DATA_DIR
        / f"{SOURCE_ID}.pdf"
    )

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF not found: {pdf_path}"
        )

    output_dir = (
        FIGURES_DATA_DIR
        / SOURCE_ID
        / "embedded"
        / "figures_2_21_2_22"
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
        "FIGURE 2.21 / 2.22 EMBEDDED IMAGE EXTRACTION"
    )
    print(
        "-------------------------------------------"
    )

    total = 0

    for page_number in TARGET_PAGES:

        page_index = (
            page_number - 1
        )

        page = document.load_page(
            page_index
        )

        images = page.get_images(
            full=True
        )

        print()
        print(
            f"PDF page {page_number}"
        )

        print(
            f"Images: {len(images)}"
        )

        for image_number, image_info in enumerate(
            images,
            start=1,
        ):

            xref = image_info[0]

            extracted = (
                document.extract_image(
                    xref
                )
            )

            image_bytes = (
                extracted["image"]
            )

            extension = (
                extracted["ext"]
            )

            width = (
                extracted["width"]
            )

            height = (
                extracted["height"]
            )

            output_path = (
                output_dir
                / (
                    f"page_{page_number:03d}"
                    f"_image_{image_number:02d}"
                    f".{extension}"
                )
            )

            output_path.write_bytes(
                image_bytes
            )

            total += 1

            print()
            print(
                f"  image {image_number}"
            )

            print(
                f"    size   : "
                f"{width} x {height}"
            )

            print(
                f"    format : "
                f"{extension}"
            )

            print(
                f"    sha256 : "
                f"{sha256_file(output_path)}"
            )

            print(
                f"    saved  : "
                f"{output_path}"
            )

    document.close()

    print()
    print(
        f"Total extracted: {total}"
    )


if __name__ == "__main__":
    main()