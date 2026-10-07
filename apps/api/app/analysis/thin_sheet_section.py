import re
from typing import Any


SECTION_RANGES = {
    "BASSII-CH2.2-THIN-SHEET": (29, 35),
    "BASSII-CH2.3-THIN-SHEET": (45, 52),
}


NUMERIC_PATTERN = re.compile(
    r"\d+(?:\.\d+)?\s*"
    r"(?:%|percent|kpa|atm|cm/s|mm/s|mm|cm|µm|μm|um|min|s)",
    re.IGNORECASE,
)


TAG_PATTERNS = {
    "experimental": (
        "experiment",
        "experimental",
        "measured",
        "observed",
        "obtained",
        "test",
        "spread rate",
        "extinction",
    ),
    "setup": (
        "experimental setup",
        "apparatus",
        "flow duct",
        "camera",
        "igniter",
        "sample",
    ),
    "computational": (
        "computational",
        "simulation",
        "numerical",
        "cfd",
        "model calculates",
        "model predicts",
    ),
    "theory": (
        "de ris",
        "theoretical",
        "thermal limit",
        "equation",
        "analytical",
    ),
    "figure": (
        "figure ",
        "fig. ",
    ),
    "table": (
        "table ",
    ),
}


def get_text(item: dict[str, Any]) -> str:
    value = item.get("text")

    if isinstance(value, str):
        return value.strip()

    value = item.get("orig")

    if isinstance(value, str):
        return value.strip()

    return ""


def get_pages(item: dict[str, Any]) -> list[int]:
    pages = set()

    for prov in item.get("prov", []):
        if not isinstance(prov, dict):
            continue

        page = prov.get("page_no")

        if isinstance(page, int):
            pages.add(page)

    return sorted(pages)


def get_study_id(
    pages: list[int],
) -> str | None:

    for study_id, (
        start_page,
        end_page,
    ) in SECTION_RANGES.items():

        if any(
            start_page <= page <= end_page
            for page in pages
        ):
            return study_id

    return None


def detect_tags(text: str) -> list[str]:
    lowered = text.lower()

    tags = []

    for tag, patterns in TAG_PATTERNS.items():
        if any(
            pattern in lowered
            for pattern in patterns
        ):
            tags.append(tag)

    return tags


def extract_section_blocks(
    document: dict[str, Any],
) -> list[dict[str, Any]]:

    results = []

    text_items = document.get(
        "texts",
        [],
    )

    for index, item in enumerate(
        text_items
    ):
        if not isinstance(item, dict):
            continue

        pages = get_pages(item)

        study_id = get_study_id(
            pages
        )

        if study_id is None:
            continue

        text = get_text(item)

        if not text:
            continue

        tags = detect_tags(text)

        has_numeric = bool(
            NUMERIC_PATTERN.search(text)
        )

        mixed_evidence = (
            "experimental" in tags
            and (
                "computational" in tags
                or "theory" in tags
            )
        )

        measurement_candidate = (
            has_numeric
            and "experimental" in tags
            and "computational" not in tags
        )

        results.append(
            {
                "block_id": (
                    f"BLOCK-{index:05d}"
                ),
                "study_id": study_id,
                "pages": pages,
                "label": item.get(
                    "label"
                ),
                "tags": tags,
                "has_numeric": has_numeric,
                "measurement_candidate": (
                    measurement_candidate
                ),
                "mixed_evidence": (
                    mixed_evidence
                ),
                "text": text,
            }
        )

    return results