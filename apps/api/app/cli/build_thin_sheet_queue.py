import json
from collections import Counter

from app.analysis.family_selector import (
    select_thin_sheet_candidates,
)

from app.core.paths import (
    CURATED_DATA_DIR,
)


SOURCE_ID = "SRC-NASA-20210011385"


def main():
    input_path = (
        CURATED_DATA_DIR
        / "feasibility"
        / f"{SOURCE_ID}_evidence_v2.json"
    )

    data = json.loads(
        input_path.read_text(
            encoding="utf-8"
        )
    )

    selected = (
        select_thin_sheet_candidates(
            data["candidates"]
        )
    )

    lane_counts = Counter(
        item["review_lane"]
        for item in selected
    )

    queue = []

    for index, candidate in enumerate(
        selected,
        start=1,
    ):
        queue.append(
            {
                "review_id": (
                    f"TS-REVIEW-{index:03d}"
                ),
                "study_id": candidate[
                    "study_id"
                ],
                "review_status": "pending",
                "review_lane": candidate[
                    "review_lane"
                ],
                "pages": candidate.get(
                    "pages",
                    [],
                ),
                "evidence_kind": candidate.get(
                    "evidence_kind"
                ),
                "data_form": candidate.get(
                    "data_form"
                ),
                "has_numeric_value": (
                    candidate.get(
                        "has_numeric_value",
                        False,
                    )
                ),
                "context": candidate.get(
                    "context",
                    "",
                ),
            }
        )

    output = {
        "source_id": SOURCE_ID,
        "family": (
            "PMMA-THIN-SHEET-"
            "OPPOSED-FLOW"
        ),
        "candidate_count": len(queue),
        "lane_counts": dict(
            lane_counts
        ),
        "candidates": queue,
    }

    output_path = (
        CURATED_DATA_DIR
        / "feasibility"
        / (
            f"{SOURCE_ID}"
            "_thin_sheet_review.json"
        )
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
        "THIN-SHEET REVIEW QUEUE V2"
    )
    print(
        "--------------------------"
    )

    print(
        f"Candidates: {len(queue)}"
    )

    print()

    print("Review lanes:")

    for key, value in (
        lane_counts.items()
    ):
        print(
            f"  {key:<20}: {value}"
        )

    print()

    for item in queue:
        print(
            item["review_id"],
            "|",
            item["study_id"],
            "|",
            item["review_lane"],
            "| pages:",
            item["pages"],
        )

        print(
            item["context"][:220]
            .replace("\n", " ")
        )

        print()

    print(
        f"Saved to: {output_path}"
    )


if __name__ == "__main__":
    main()