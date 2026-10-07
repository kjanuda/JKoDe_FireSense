import re
from collections import Counter
from typing import Any


PMMA_TERMS = (
    "pmma",
    "polymethylmethacrylate",
)


KEYWORD_GROUPS = {
    "oxygen": (
        "oxygen",
        "o2",
        "o₂",
    ),
    "pressure": (
        "pressure",
        "kpa",
    ),
    "gravity": (
        "microgravity",
        "reduced gravity",
        "partial gravity",
        "1g",
        "0g",
        "µg",
        "μg",
    ),
    "flow": (
        "flow",
        "velocity",
        "cm/s",
        "opposed",
        "concurrent",
    ),
    "spread": (
        "flame spread",
        "spread rate",
        "flame growth",
    ),
    "extinction": (
        "extinction",
        "extinguished",
        "flammability boundary",
    ),
    "geometry": (
        "sheet",
        "rod",
        "cylinder",
        "sphere",
        "slab",
    ),
    "thickness": (
        "thickness",
        "thin",
        "thick",
        "mm",
        "µm",
        "μm",
    ),
}


NUMERIC_PATTERN = re.compile(
    r"""
    \b\d+(?:\.\d+)?\s*
    (?:
        % |
        kpa |
        mm/s |
        cm/s |
        mm |
        cm |
        µm |
        μm |
        um
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)


def get_text(item: dict[str, Any]) -> str:
    value = item.get("text")

    if isinstance(value, str):
        return value.strip()

    value = item.get("orig")

    if isinstance(value, str):
        return value.strip()

    return ""


def get_pages(item: dict[str, Any]) -> list[int]:
    pages: set[int] = set()

    provenance = item.get("prov", [])

    if not isinstance(provenance, list):
        return []

    for entry in provenance:
        if not isinstance(entry, dict):
            continue

        page_number = entry.get("page_no")

        if isinstance(page_number, int):
            pages.add(page_number)

    return sorted(pages)


def find_keyword_groups(text: str) -> list[str]:
    lowered = text.lower()

    matched = []

    for group, keywords in KEYWORD_GROUPS.items():
        if any(
            keyword.lower() in lowered
            for keyword in keywords
        ):
            matched.append(group)

    return matched


def contains_pmma(text: str) -> bool:
    lowered = text.lower()

    return any(
        term in lowered
        for term in PMMA_TERMS
    )


def looks_numeric(text: str) -> bool:
    return bool(NUMERIC_PATTERN.search(text))


def build_context(
    texts: list[dict[str, Any]],
    index: int,
    window: int = 1,
) -> str:
    start = max(
        0,
        index - window,
    )

    end = min(
        len(texts),
        index + window + 1,
    )

    chunks = []

    for item in texts[start:end]:
        text = get_text(item)

        if text:
            chunks.append(text)

    return "\n".join(chunks)


def audit_docling_document(
    document: dict[str, Any],
    source_id: str,
) -> dict[str, Any]:
    text_items = document.get("texts", [])

    if not isinstance(text_items, list):
        text_items = []

    candidates = []

    category_counts = Counter()

    for index, item in enumerate(text_items):
        if not isinstance(item, dict):
            continue

        text = get_text(item)

        if not text:
            continue

        if not contains_pmma(text):
            continue

        context = build_context(
            text_items,
            index,
            window=1,
        )

        groups = find_keyword_groups(context)

        for group in groups:
            category_counts[group] += 1

        candidates.append(
            {
                "source_id": source_id,
                "text_index": index,
                "label": item.get("label"),
                "pages": get_pages(item),
                "keyword_groups": groups,
                "numeric_candidate": looks_numeric(
                    context
                ),
                "text": text,
                "context": context,
            }
        )

    numeric_candidates = sum(
        1
        for candidate in candidates
        if candidate["numeric_candidate"]
    )

    tables = document.get("tables", [])
    pictures = document.get("pictures", [])

    return {
        "source_id": source_id,
        "summary": {
            "total_text_blocks": len(
                text_items
            ),
            "total_tables": (
                len(tables)
                if isinstance(tables, list)
                else 0
            ),
            "total_pictures": (
                len(pictures)
                if isinstance(pictures, list)
                else 0
            ),
            "pmma_candidate_blocks": len(
                candidates
            ),
            "pmma_numeric_candidates": (
                numeric_candidates
            ),
            "keyword_group_counts": dict(
                category_counts
            ),
        },
        "candidates": candidates,
    }