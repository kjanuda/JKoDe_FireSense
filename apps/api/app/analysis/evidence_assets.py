import re
from typing import Any


PAGE_RANGES = (
    (29, 35),
    (45, 52),
)


FIGURE_PATTERN = re.compile(
    r"Figure\s+([A-Za-z]?\d+(?:\.\d+)?)",
    re.IGNORECASE,
)

TABLE_PATTERN = re.compile(
    r"Table\s+([A-Za-z]?\d+(?:\.\d+)?)",
    re.IGNORECASE,
)


DIGITIZATION_TERMS = (
    "spread rate",
    "flame spread",
    "extinction",
    "velocity",
    "oxygen",
    "o2",
    "thickness",
)


def get_text(
    item: dict[str, Any],
) -> str:
    value = item.get("text")

    if isinstance(value, str):
        return value.strip()

    value = item.get("orig")

    if isinstance(value, str):
        return value.strip()

    return ""


def get_pages(
    item: dict[str, Any],
) -> list[int]:
    pages = set()

    for entry in item.get(
        "prov",
        [],
    ):
        if not isinstance(
            entry,
            dict,
        ):
            continue

        page = entry.get(
            "page_no"
        )

        if isinstance(
            page,
            int,
        ):
            pages.add(page)

    return sorted(pages)


def relevant_page(
    pages: list[int],
) -> bool:

    for page in pages:
        for start, end in PAGE_RANGES:
            if start <= page <= end:
                return True

    return False


def needs_digitization(
    text: str,
) -> bool:

    lowered = text.lower()

    return any(
        term in lowered
        for term in DIGITIZATION_TERMS
    )


def build_asset_inventory(
    document: dict[str, Any],
) -> list[dict[str, Any]]:

    assets = []

    seen = set()

    for index, item in enumerate(
        document.get(
            "texts",
            [],
        )
    ):
        if not isinstance(
            item,
            dict,
        ):
            continue

        pages = get_pages(item)

        if not relevant_page(
            pages
        ):
            continue

        text = get_text(item)

        if not text:
            continue

        figure_matches = list(
            FIGURE_PATTERN.finditer(
                text
            )
        )

        table_matches = list(
            TABLE_PATTERN.finditer(
                text
            )
        )

        for match in figure_matches:

            ref = match.group(1)

            key = (
                "figure",
                ref,
                tuple(pages),
            )

            if key in seen:
                continue

            seen.add(key)

            assets.append(
                {
                    "asset_type": "figure",
                    "reference": ref,
                    "pages": pages,
                    "text_index": index,
                    "needs_digitization": (
                        needs_digitization(
                            text
                        )
                    ),
                    "caption_context": text,
                }
            )

        for match in table_matches:

            ref = match.group(1)

            key = (
                "table",
                ref,
                tuple(pages),
            )

            if key in seen:
                continue

            seen.add(key)

            assets.append(
                {
                    "asset_type": "table",
                    "reference": ref,
                    "pages": pages,
                    "text_index": index,
                    "needs_digitization": False,
                    "caption_context": text,
                }
            )

    return assets