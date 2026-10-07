import json
from collections import Counter

from app.analysis.candidate_triage import (
    triage_candidates,
)
from app.core.paths import (
    CURATED_DATA_DIR,
)


SOURCE_ID = "SRC-NASA-20210011385"


def main():
    feasibility_path = (
        CURATED_DATA_DIR
        / "feasibility"
        / f"{SOURCE_ID}_pmma_audit.json"
    )

    if not feasibility_path.exists():
        raise FileNotFoundError(
            f"Missing feasibility report: "
            f"{feasibility_path}"
        )

    report = json.loads(
        feasibility_path.read_text(
            encoding="utf-8"
        )
    )

    candidates = report[
        "candidates"
    ]

    triaged = triage_candidates(
        candidates
    )

    counts = Counter(
        item["triage_class"]
        for item in triaged
    )

    output = {
        "source_id": SOURCE_ID,
        "counts": dict(counts),
        "candidates": triaged,
    }

    output_path = (
        CURATED_DATA_DIR
        / "feasibility"
        / f"{SOURCE_ID}_pmma_triage.json"
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
        "FIRESENSE PMMA CANDIDATE TRIAGE"
    )
    print(
        "--------------------------------"
    )

    print(
        f"Total candidates : "
        f"{len(triaged)}"
    )

    print(
        f"A likely data     : "
        f"{counts.get('A', 0)}"
    )

    print(
        f"B context         : "
        f"{counts.get('B', 0)}"
    )

    print(
        f"C figure/table    : "
        f"{counts.get('C', 0)}"
    )

    print(
        f"D irrelevant      : "
        f"{counts.get('D', 0)}"
    )

    print()
    print(
        f"Saved to: {output_path}"
    )


if __name__ == "__main__":
    main()