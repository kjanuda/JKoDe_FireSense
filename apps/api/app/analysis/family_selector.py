from typing import Any


THIN_SHEET_STUDIES = (
    {
        "study_id": "BASSII-CH2.2-THIN-SHEET",
        "page_start": 29,
        "page_end": 35,
    },
    {
        "study_id": "BASSII-CH2.3-THIN-SHEET",
        "page_start": 45,
        "page_end": 52,
    },
)


def contains_pmma(text: str) -> bool:
    lowered = text.lower()

    return (
        "pmma" in lowered
        or "polymethylmethacrylate" in lowered
    )


def find_study_for_pages(
    pages: list[int],
) -> str | None:

    for study in THIN_SHEET_STUDIES:
        for page in pages:
            if (
                study["page_start"]
                <= page
                <= study["page_end"]
            ):
                return study["study_id"]

    return None


def classify_review_lane(
    candidate: dict[str, Any],
) -> str:

    evidence_kind = candidate.get(
        "evidence_kind",
        "context",
    )

    has_numeric = candidate.get(
        "has_numeric_value",
        False,
    )

    if evidence_kind == "computational":
        return "simulation_context"

    if evidence_kind == "theoretical":
        return "physics_context"

    if evidence_kind == "setup":
        return "setup_context"

    if has_numeric:
        return "measurement_review"

    return "context_review"


def is_thin_sheet_candidate(
    candidate: dict[str, Any],
) -> bool:

    if candidate.get(
        "evidence_kind"
    ) == "bibliography":
        return False

    pages = candidate.get(
        "pages",
        [],
    )

    study_id = find_study_for_pages(
        pages
    )

    if study_id is None:
        return False

    context = candidate.get(
        "context",
        "",
    )

    if not contains_pmma(context):
        return False

    return True


def select_thin_sheet_candidates(
    candidates: list[dict[str, Any]],
) -> list[dict[str, Any]]:

    selected = []

    for candidate in candidates:

        if not is_thin_sheet_candidate(
            candidate
        ):
            continue

        pages = candidate.get(
            "pages",
            [],
        )

        study_id = find_study_for_pages(
            pages
        )

        selected.append(
            {
                **candidate,
                "study_id": study_id,
                "review_lane": (
                    classify_review_lane(
                        candidate
                    )
                ),
            }
        )

    return selected