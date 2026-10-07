from app.analysis.family_selector import (
    is_thin_sheet_candidate,
    select_thin_sheet_candidates,
)


def test_page_48_pmma_is_selected():
    candidate = {
        "pages": [48],
        "context": (
            "Microgravity flame spread over "
            "100 µm PMMA sheet at 20.7 percent O2."
        ),
        "evidence_kind": "experimental",
        "has_numeric_value": True,
    }

    assert is_thin_sheet_candidate(
        candidate
    )


def test_bibliography_is_rejected():
    candidate = {
        "pages": [139],
        "context": (
            "PMMA sheet flame spread conference reference."
        ),
        "evidence_kind": "bibliography",
        "has_numeric_value": True,
    }

    assert not is_thin_sheet_candidate(
        candidate
    )


def test_candidate_gets_study_and_lane():
    candidate = {
        "pages": [49],
        "context": (
            "100 µm PMMA sheet spread rate "
            "was 2.2 mm/s in microgravity."
        ),
        "evidence_kind": "experimental",
        "has_numeric_value": True,
    }

    result = select_thin_sheet_candidates(
        [candidate]
    )

    assert len(result) == 1

    assert (
        result[0]["study_id"]
        == "BASSII-CH2.3-THIN-SHEET"
    )

    assert (
        result[0]["review_lane"]
        == "measurement_review"
    )