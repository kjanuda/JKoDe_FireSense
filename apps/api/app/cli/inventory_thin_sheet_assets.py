import json

from app.analysis.evidence_assets import (
    build_asset_inventory,
)

from app.core.paths import (
    CURATED_DATA_DIR,
    PARSED_DATA_DIR,
)


SOURCE_ID = "SRC-NASA-20210011385"


def main():

    parsed_dir = (
        PARSED_DATA_DIR
        / SOURCE_ID
    )

    json_files = list(
        parsed_dir.glob(
            "*.json"
        )
    )

    if not json_files:
        raise FileNotFoundError(
            "Docling JSON not found."
        )

    document = json.loads(
        json_files[0].read_text(
            encoding="utf-8"
        )
    )

    assets = build_asset_inventory(
        document
    )

    figures = [
        item
        for item in assets
        if item[
            "asset_type"
        ] == "figure"
    ]

    tables = [
        item
        for item in assets
        if item[
            "asset_type"
        ] == "table"
    ]

    digitization = [
        item
        for item in figures
        if item[
            "needs_digitization"
        ]
    ]

    output_dir = (
        CURATED_DATA_DIR
        / "thin_sheet"
    )

    output_path = (
        output_dir
        / "asset_inventory.json"
    )

    output_path.write_text(
        json.dumps(
            {
                "source_id": SOURCE_ID,
                "figure_count": len(
                    figures
                ),
                "table_count": len(
                    tables
                ),
                "digitization_candidates": (
                    len(
                        digitization
                    )
                ),
                "assets": assets,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print()
    print(
        "THIN-SHEET EVIDENCE ASSETS"
    )
    print(
        "--------------------------"
    )

    print(
        f"Figures             : "
        f"{len(figures)}"
    )

    print(
        f"Tables              : "
        f"{len(tables)}"
    )

    print(
        f"Digitization targets: "
        f"{len(digitization)}"
    )

    print()

    print(
        "FIGURE CANDIDATES"
    )

    for item in digitization:

        print()
        print(
            f"Figure "
            f"{item['reference']}"
            f" | pages "
            f"{item['pages']}"
        )

        print(
            item[
                "caption_context"
            ][:300]
            .replace(
                "\n",
                " ",
            )
        )

    print()
    print(
        "TABLES"
    )

    for item in tables:

        print()
        print(
            f"Table "
            f"{item['reference']}"
            f" | pages "
            f"{item['pages']}"
        )

        print(
            item[
                "caption_context"
            ][:250]
            .replace(
                "\n",
                " ",
            )
        )

    print()
    print(
        f"Saved: {output_path}"
    )


if __name__ == "__main__":
    main()