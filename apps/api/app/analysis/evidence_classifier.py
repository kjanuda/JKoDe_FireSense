import re
from typing import Any


NUMERIC_PATTERN = re.compile(
    r"\d+(?:\.\d+)?\s*"
    r"(?:%|kpa|atm|cm/s|mm/s|mm|min|s|µm|μm|um)",
    re.IGNORECASE,
)


BIBLIOGRAPHY_TERMS = (
    "doi:",
    "journal of",
    "proceedings",
    "conference",
    "et al.",
    "nasa/tm-",
)


COMPUTATIONAL_TERMS = (
    "computational",
    "computation",
    "simulation",
    "numerical model",
    "model predicts",
    "calculated",
    "calculations",
)


THEORY_TERMS = (
    "theory",
    "theoretical",
    "de ris",
    "equation",
    "analytical",
)


EXPERIMENTAL_TERMS = (
    "experiment",
    "experiments",
    "experimental",
    "test",
    "tests",
    "tested",
    "measured",
    "observed",
    "obtained",
    "spread rate",
    "extinction",
)


SETUP_TERMS = (
    "experimental setup",
    "apparatus",
    "hardware",
    "igniter",
    "camera",
    "sample dimensions",
)


def contains_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(
        term in text
        for term in terms
    )


def classify_evidence(
    candidate: dict[str, Any],
) -> dict[str, Any]:

    context = candidate.get(
        "context",
        "",
    )

    lowered = context.lower()

    has_numeric = bool(
        NUMERIC_PATTERN.search(context)
    )

    # Evidence type
    if contains_any(
        lowered,
        BIBLIOGRAPHY_TERMS,
    ):
        evidence_kind = "bibliography"

    elif contains_any(
        lowered,
        COMPUTATIONAL_TERMS,
    ):
        evidence_kind = "computational"

    elif contains_any(
        lowered,
        THEORY_TERMS,
    ):
        evidence_kind = "theoretical"

    elif contains_any(
        lowered,
        SETUP_TERMS,
    ):
        evidence_kind = "setup"

    elif contains_any(
        lowered,
        EXPERIMENTAL_TERMS,
    ):
        evidence_kind = "experimental"

    else:
        evidence_kind = "context"

    # Data location
    has_figure = (
        "figure " in lowered
        or "fig. " in lowered
    )

    has_table = (
        "table " in lowered
    )

    if has_figure and has_table:
        data_form = "figure_and_table"

    elif has_figure:
        data_form = "figure_linked"

    elif has_table:
        data_form = "table_linked"

    else:
        data_form = "prose"

    # Important:
    # Figure-linked prose can still contain directly usable numbers.
    direct_numeric_candidate = (
        evidence_kind == "experimental"
        and has_numeric
    )

    return {
        **candidate,
        "evidence_kind": evidence_kind,
        "data_form": data_form,
        "has_numeric_value": has_numeric,
        "direct_numeric_candidate": (
            direct_numeric_candidate
        ),
    }


def classify_all(
    candidates: list[dict[str, Any]],
) -> list[dict[str, Any]]:

    return [
        classify_evidence(candidate)
        for candidate in candidates
    ]