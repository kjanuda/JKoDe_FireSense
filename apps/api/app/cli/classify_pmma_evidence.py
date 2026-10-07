import json
from collections import Counter

from app.analysis.deduplication import (
    deduplicate_candidates,
)

from app.analysis.evidence_classifier import (
    classify_all,
)

from app.core.paths import (
    CURATED_DATA_DIR,
)


SOURCE_ID = "SRC-NASA-20210011385"


def main():

    input_path = (
        CURATED_DATA_DIR
        / "feasibility"
        / f"{SOURCE_ID}_pmma_audit.json"
    )

    data = json.loads(
        input_path.read_text(
            encoding="utf-8"
        )
    )

    candidates = data[
        "candidates"
    ]

    deduplicated = (
        deduplicate_candidates(
            candidates
        )
    )

    classified = classify_all(
        deduplicated
    )

    evidence_counts = Counter(
        item["evidence_kind"]
        for item in classified
    )

    form_counts = Counter(
        item["data_form"]
        for item in classified
    )

    direct_numeric = [
        item
        for item in classified
        if item[
            "direct_numeric_candidate"
        ]
    ]

    output = {
        "source_id": SOURCE_ID,
        "original_candidates": len(
            candidates
        ),
        "unique_candidates": len(
            deduplicated
        ),
        "evidence_counts": dict(
            evidence_counts
        ),
        "data_form_counts": dict(
            form_counts
        ),
        "direct_numeric_count": len(
            direct_numeric
        ),
        "candidates": classified,
    }

    output_path = (
        CURATED_DATA_DIR
        / "feasibility"
        / f"{SOURCE_ID}_evidence_v2.json"
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
        "FIRESENSE EVIDENCE CLASSIFICATION V2"
    )

    print(
        "-----------------------------------"
    )

    print(
        f"Original candidates : "
        f"{len(candidates)}"
    )

    print(
        f"Unique candidates   : "
        f"{len(deduplicated)}"
    )

    print()

    print("Evidence types:")

    for key, value in (
        evidence_counts.items()
    ):
        print(
            f"  {key:<15}: {value}"
        )

    print()

    print("Data forms:")

    for key, value in (
        form_counts.items()
    ):
        print(
            f"  {key:<15}: {value}"
        )

    print()

    print(
        "Direct experimental numeric "
        f"candidates: {len(direct_numeric)}"
    )

    print()

    print(
        f"Saved to: {output_path}"
    )


if __name__ == "__main__":
    main()