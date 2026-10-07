import json
import re

from app.core.paths import (
    CURATED_DATA_DIR,
    PARSED_DATA_DIR,
)


SOURCE_ID = "SRC-NASA-20210011385"

TARGET_TABLES = {
    13,
    14,
}

TARGET_TOKENS = (
    "B03",
    "B3",
    "B4",
    "B11",
    "B13",
)


def normalize_text(
    value: object,
) -> str:

    if not isinstance(
        value,
        str,
    ):
        return ""

    return " ".join(
        value
        .replace("\n", " ")
        .replace("\r", " ")
        .split()
    )


def token_present(
    text: str,
    token: str,
) -> bool:

    pattern = (
        rf"(?<![A-Za-z0-9])"
        rf"{re.escape(token)}"
        rf"(?![A-Za-z0-9])"
    )

    return (
        re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )
        is not None
    )


def contains_target(
    text: str,
) -> bool:

    return any(
        token_present(
            text,
            token,
        )
        for token in TARGET_TOKENS
    )


def get_docling_json():

    parsed_dir = (
        PARSED_DATA_DIR
        / SOURCE_ID
    )

    json_files = sorted(
        parsed_dir.glob(
            "*.json"
        )
    )

    if not json_files:
        raise FileNotFoundError(
            f"No Docling JSON found in "
            f"{parsed_dir}"
        )

    return json_files[0]


def safe_int(
    value: object,
) -> int | None:

    if isinstance(
        value,
        int,
    ):
        return value

    return None


def extract_bbox(
    cell: dict,
) -> dict | None:

    bbox = cell.get(
        "bbox"
    )

    if isinstance(
        bbox,
        dict,
    ):
        return bbox

    return None


def simplify_cell(
    cell: dict,
    cell_index: int,
) -> dict:

    return {
        "cell_index": (
            cell_index
        ),

        "text": normalize_text(
            cell.get(
                "text",
                "",
            )
        ),

        "start_row": safe_int(
            cell.get(
                "start_row_offset_idx"
            )
        ),

        "end_row": safe_int(
            cell.get(
                "end_row_offset_idx"
            )
        ),

        "start_col": safe_int(
            cell.get(
                "start_col_offset_idx"
            )
        ),

        "end_col": safe_int(
            cell.get(
                "end_col_offset_idx"
            )
        ),

        "row_span": safe_int(
            cell.get(
                "row_span"
            )
        ),

        "col_span": safe_int(
            cell.get(
                "col_span"
            )
        ),

        "column_header": (
            cell.get(
                "column_header"
            )
        ),

        "row_header": (
            cell.get(
                "row_header"
            )
        ),

        "row_section": (
            cell.get(
                "row_section"
            )
        ),

        "bbox": extract_bbox(
            cell
        ),
    }


def main():

    document_path = (
        get_docling_json()
    )

    document = json.loads(
        document_path.read_text(
            encoding="utf-8"
        )
    )

    tables = document.get(
        "tables",
        [],
    )

    if not isinstance(
        tables,
        list,
    ):
        raise ValueError(
            "'tables' is not a list."
        )

    output = {
        "source_id": SOURCE_ID,
        "document": str(
            document_path
        ),
        "tables": [],
    }

    print()
    print(
        "DOCLING RAW TABLE CELL INSPECTOR"
    )
    print(
        "--------------------------------"
    )

    for (
        table_index,
        table,
    ) in enumerate(
        tables
    ):

        if (
            table_index
            not in TARGET_TABLES
        ):
            continue

        if not isinstance(
            table,
            dict,
        ):
            continue

        data = table.get(
            "data",
            {},
        )

        if not isinstance(
            data,
            dict,
        ):
            continue

        print()
        print(
            f"TABLE {table_index}"
        )

        print(
            f"Data keys: "
            f"{sorted(data.keys())}"
        )

        grid = data.get(
            "grid",
            [],
        )

        if isinstance(
            grid,
            list,
        ):
            print(
                f"Grid rows : "
                f"{len(grid)}"
            )

            if grid:
                max_columns = max(
                    (
                        len(row)
                        for row in grid
                        if isinstance(
                            row,
                            list,
                        )
                    ),
                    default=0,
                )

                print(
                    f"Grid cols : "
                    f"{max_columns}"
                )

        raw_cells = data.get(
            "table_cells",
            [],
        )

        if not isinstance(
            raw_cells,
            list,
        ):
            raw_cells = []

        print(
            f"Raw cells : "
            f"{len(raw_cells)}"
        )

        table_result = {
            "table_index": (
                table_index
            ),
            "data_keys": sorted(
                data.keys()
            ),
            "raw_cell_count": len(
                raw_cells
            ),
            "target_cells": [],
            "all_cells": [],
        }

        simplified = []

        for (
            cell_index,
            cell,
        ) in enumerate(
            raw_cells
        ):

            if not isinstance(
                cell,
                dict,
            ):
                continue

            simple = simplify_cell(
                cell,
                cell_index,
            )

            simplified.append(
                simple
            )

        # Sort by original table location
        simplified.sort(
            key=lambda cell: (
                cell["start_row"]
                if cell["start_row"]
                is not None
                else 999999,

                cell["start_col"]
                if cell["start_col"]
                is not None
                else 999999,

                cell["cell_index"],
            )
        )

        table_result[
            "all_cells"
        ] = simplified

        target_cells = [
            cell
            for cell in simplified
            if contains_target(
                cell["text"]
            )
        ]

        table_result[
            "target_cells"
        ] = target_cells

        print()
        print(
            "TARGET CELLS"
        )
        print(
            "------------"
        )

        if not target_cells:
            print(
                "No individual target cells "
                "found."
            )

        for cell in target_cells:

            print()

            print(
                f"cell      : "
                f"{cell['cell_index']}"
            )

            print(
                f"row       : "
                f"{cell['start_row']} "
                f"→ {cell['end_row']}"
            )

            print(
                f"column    : "
                f"{cell['start_col']} "
                f"→ {cell['end_col']}"
            )

            print(
                f"row span  : "
                f"{cell['row_span']}"
            )

            print(
                f"col span  : "
                f"{cell['col_span']}"
            )

            print(
                f"text      : "
                f"{cell['text']}"
            )

            print(
                f"bbox      : "
                f"{cell['bbox']}"
            )

        output[
            "tables"
        ].append(
            table_result
        )

        print()
        print(
            "=" * 70
        )

    output_dir = (
        CURATED_DATA_DIR
        / "thin_sheet"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        output_dir
        / "docling_raw_table_cells.json"
    )

    output_path.write_text(
        json.dumps(
            output,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print()
    print(
        "RAW TABLE INSPECTION COMPLETE"
    )
    print(
        "-----------------------------"
    )

    print(
        f"Saved: {output_path}"
    )


if __name__ == "__main__":
    main()