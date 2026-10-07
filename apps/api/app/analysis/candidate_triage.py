import re
from typing import Any


BIBLIOGRAPHY_PATTERNS = (
    "doi:",
    "vol.",
    "journal",
    "conference",
    "proceedings",
    "et al.",
    "nasa/tm",
    "nasa technical memorandum",
    "aiaa",
)

FIGURE_PATTERNS = (
    "figure ",
    "fig. ",
    "fig ",
)

TABLE_PATTERNS = (
    "table ",
)

EXPERIMENT_PATTERNS = (
    "experiment",
    "test ",
    "sample",
    "flame spread",
    "spread rate",
    "extinction",
    "oxygen",
    "flow velocity",
    "pmma",
)

NUMERIC_SCIENCE_PATTERN = re.compile(
    r"\d+(?:\.\d+)?\s*(?:%|kpa|cm/s|mm/s|mm|cm|µm|μm|um)",
    re.IGNORECASE,
)


def classify_candidate(
    candidate: dict[str, Any],
) -> dict[str, Any]:
    context = candidate.get(
        "context",
        "",
    ).lower()

    reasons = []

    bibliography_score = sum(
        1
        for pattern in BIBLIOGRAPHY_PATTERNS
        if pattern in context
    )

    figure_score = sum(
        1
        for pattern in FIGURE_PATTERNS
        if pattern in context
    )

    table_score = sum(
        1
        for pattern in TABLE_PATTERNS
        if pattern in context
    )

    experiment_score = sum(
        1
        for pattern in EXPERIMENT_PATTERNS
        if pattern in context
    )

    has_numeric_science = bool(
        NUMERIC_SCIENCE_PATTERN.search(
            context
        )
    )

    groups = set(
        candidate.get(
            "keyword_groups",
            [],
        )
    )

    if bibliography_score >= 2:
        classification = "D"
        reasons.append(
            "bibliography-like content"
        )

    elif (
        figure_score > 0
        and has_numeric_science
    ):
        classification = "C"
        reasons.append(
            "figure-linked numeric content"
        )

    elif (
        table_score > 0
        and has_numeric_science
    ):
        classification = "A"
        reasons.append(
            "table-linked numeric content"
        )

    elif (
        has_numeric_science
        and experiment_score >= 2
        and (
            "spread" in groups
            or "extinction" in groups
            or "oxygen" in groups
            or "flow" in groups
        )
    ):
        classification = "A"
        reasons.append(
            "numeric experimental context"
        )

    elif experiment_score >= 2:
        classification = "B"
        reasons.append(
            "scientific context without enough numeric evidence"
        )

    else:
        classification = "D"
        reasons.append(
            "low experimental relevance"
        )

    return {
        **candidate,
        "triage_class": classification,
        "triage_reasons": reasons,
    }


def triage_candidates(
    candidates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return [
        classify_candidate(candidate)
        for candidate in candidates
    ]