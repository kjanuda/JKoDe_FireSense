import json
import re

from app.core.paths import (
    CURATED_DATA_DIR,
    PARSED_DATA_DIR,
)


SOURCE_ID = "SRC-NASA-20210011385"

# Use tuples instead of sets so the structure
# is naturally JSON serializable.
TARGET_TESTS = {
    "B03": ("B03", "B3"),
    "B11": ("B11",),
    "B4": ("B4",),
    "B13": ("B13",),
}


def normalize_text(
    value: object,
) -> str:
    """
    Normalize text extracted from Docling table cells.
    """

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


def cell_text(
    cell: object,
) -> str:
    """
    Safely obtain normalized text
    from a Docling table cell.
    """

    if not isinstance(
        cell,
        dict,
    ):
        return ""

    return normalize_text(
        cell.get(
            "text",
            "",
        )
    )


def token_present(
    text: str,
    token: str,
) -> bool:
    """
    Detect tokens such as B3 / B03 / B11
    without accidentally matching B13, B30, etc.
    """

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


def detect_targets(
    row_text: str,
) -> list[str]:
    """
    Return canonical test IDs found
    in a table row.
    """

    found: list[str] = []

    for (
        canonical,
        aliases,
    ) in TARGET_TESTS.items():

        for alias in aliases:

            if token_present(
                row_text,
                alias,
            ):
                found.append(
                    canonical
                )
                break

    return found


def get_pages(
    table: dict,
) -> list[int]:
    """
    Extract unique page numbers
    from Docling provenance.
    """

    pages: set[int] = set()

    provenance = table.get(
        "prov",
        [],
    )

    if not isinstance(
        provenance,
        list,
    ):
        return []

    for item in provenance:

        if not isinstance(
            item,
            dict,
        ):
            continue

        page = item.get(
            "page_no"
        )

        if isinstance(
            page,
            int,
        ):
            pages.add(
                page
            )

    return sorted(
        pages
    )


def get_document_json_path():

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
            "Docling JSON not found in: "
            f"{parsed_dir}"
        )

    return json_files[0]


def main():

    document_path = (
        get_document_json_path()
    )

    print()
    print(
        "Using Docling JSON:"
    )
    print(
        document_path
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
            "Invalid Docling JSON: "
            "'tables' is not a list."
        )

    matches: list[dict] = []

    print()
    print(
        "TARGET BASS-II TEST ROWS"
    )
    print(
        "------------------------"
    )

    for (
        table_index,
        table,
    ) in enumerate(
        tables
    ):

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

        grid = data.get(
            "grid",
            [],
        )

        if not isinstance(
            grid,
            list,
        ):
            continue

        pages = get_pages(
            table
        )

        for (
            row_index,
            row,
        ) in enumerate(
            grid
        ):

            if not isinstance(
                row,
                list,
            ):
                continue

            cells = [
                cell_text(
                    cell
                )
                for cell in row
            ]

            non_empty_cells = [
                value
                for value in cells
                if value
            ]

            if not non_empty_cells:
                continue

            row_text = " | ".join(
                non_empty_cells
            )

            targets = detect_targets(
                row_text
            )

            if not targets:
                continue

            record = {
                "table_index": (
                    table_index
                ),
                "pages": pages,
                "row_index": (
                    row_index
                ),
                "targets": targets,
                "cells": cells,
                "row_text": row_text,
            }

            matches.append(
                record
            )

            print()
            print(
                f"TABLE {table_index}"
                f" | ROW {row_index}"
                f" | PAGES {pages}"
            )

            print(
                "Targets:",
                ", ".join(
                    targets
                ),
            )

            print(
                "-" * 60
            )

            for (
                column_index,
                value,
            ) in enumerate(
                cells
            ):

                if not value:
                    continue

                print(
                    f"[{column_index:02d}] "
                    f"{value}"
                )

            print(
                "=" * 60
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
        / "target_test_rows.json"
    )

    result = {
        "source_id": (
            SOURCE_ID
        ),

        # Explicit conversion to lists
        # keeps JSON serialization safe.
        "target_aliases": {
            canonical: list(
                aliases
            )
            for (
                canonical,
                aliases,
            ) in TARGET_TESTS.items()
        },

        "match_count": len(
            matches
        ),

        "matches": matches,
    }

    output_path.write_text(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print()
    print(
        "TARGET ROW SEARCH COMPLETE"
    )
    print(
        "--------------------------"
    )

    print(
        f"Matches: {len(matches)}"
    )

    print(
        f"Saved  : {output_path}"
    )


if __name__ == "__main__":
    main()