import json

from app.core.paths import (
    CURATED_DATA_DIR,
    PARSED_DATA_DIR,
)


SOURCE_ID = "SRC-NASA-20210011385"

TARGET_RUNS = (
    "B03",
    "B11",
    "B4",
    "B13",
)


def text_from_table(table: dict) -> str:
    parts = []

    data = table.get("data")

    if isinstance(data, dict):

        grid = data.get(
            "grid",
            [],
        )

        if isinstance(grid, list):

            for row in grid:

                if not isinstance(
                    row,
                    list,
                ):
                    continue

                for cell in row:

                    if not isinstance(
                        cell,
                        dict,
                    ):
                        continue

                    text = cell.get(
                        "text"
                    )

                    if isinstance(
                        text,
                        str,
                    ):
                        parts.append(
                            text.strip()
                        )

    return " | ".join(
        part
        for part in parts
        if part
    )


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

    tables = document.get(
        "tables",
        [],
    )

    print()
    print(
        "BASS-II TEST MATRIX SEARCH"
    )
    print(
        "--------------------------"
    )

    matches = []

    for index, table in enumerate(
        tables
    ):

        if not isinstance(
            table,
            dict,
        ):
            continue

        table_text = (
            text_from_table(
                table
            )
        )

        if not table_text:
            continue

        found_runs = [
            run
            for run in TARGET_RUNS
            if run.lower()
            in table_text.lower()
        ]

        if not found_runs:
            continue

        provenance = table.get(
            "prov",
            [],
        )

        pages = sorted(
            {
                item.get(
                    "page_no"
                )
                for item in provenance
                if isinstance(
                    item,
                    dict,
                )
                and isinstance(
                    item.get(
                        "page_no"
                    ),
                    int,
                )
            }
        )

        record = {
            "table_index": index,
            "pages": pages,
            "found_runs": (
                found_runs
            ),
            "text": table_text,
        }

        matches.append(
            record
        )

        print()
        print(
            f"TABLE {index}"
        )

        print(
            f"Pages: {pages}"
        )

        print(
            "Runs :",
            ", ".join(
                found_runs
            ),
        )

        print()

        print(
            table_text[:5000]
        )

        print()
        print(
            "-" * 70
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
        / "test_matrix_matches.json"
    )

    output_path.write_text(
        json.dumps(
            {
                "source_id": (
                    SOURCE_ID
                ),
                "target_runs": (
                    list(
                        TARGET_RUNS
                    )
                ),
                "match_count": len(
                    matches
                ),
                "matches": matches,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print()
    print(
        f"Matches: {len(matches)}"
    )

    print(
        f"Saved  : {output_path}"
    )


if __name__ == "__main__":
    main()