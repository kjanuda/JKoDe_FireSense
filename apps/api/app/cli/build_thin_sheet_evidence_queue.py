import csv
import json
from collections import Counter

from app.analysis.thin_sheet_section import (
    extract_section_blocks,
)

from app.core.paths import (
    CURATED_DATA_DIR,
    PARSED_DATA_DIR,
)


SOURCE_ID = "SRC-NASA-20210011385"


def main():

    source_dir = (
        PARSED_DATA_DIR
        / SOURCE_ID
    )

    json_files = list(
        source_dir.glob("*.json")
    )

    if not json_files:
        raise FileNotFoundError(
            "Docling JSON not found."
        )

    document = json.loads(
        json_files[0].read_text(
            encoding="utf-8"
        )
    )

    blocks = extract_section_blocks(
        document
    )

    tag_counts = Counter()

    for block in blocks:
        tag_counts.update(
            block["tags"]
        )

    measurement_candidates = [
        block
        for block in blocks
        if block[
            "measurement_candidate"
        ]
    ]

    mixed_candidates = [
        block
        for block in blocks
        if block[
            "mixed_evidence"
        ]
    ]

    output_dir = (
        CURATED_DATA_DIR
        / "thin_sheet"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    json_path = (
        output_dir
        / "evidence_queue.json"
    )

    json_path.write_text(
        json.dumps(
            {
                "source_id": SOURCE_ID,
                "total_blocks": len(
                    blocks
                ),
                "tag_counts": dict(
                    tag_counts
                ),
                "measurement_candidate_count": (
                    len(
                        measurement_candidates
                    )
                ),
                "mixed_evidence_count": (
                    len(
                        mixed_candidates
                    )
                ),
                "blocks": blocks,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    csv_path = (
        output_dir
        / "measurement_review.csv"
    )

    with csv_path.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "block_id",
                "study_id",
                "pages",
                "tags",
                "has_numeric",
                "mixed_evidence",
                "text",
                "human_status",
                "human_notes",
            ],
        )

        writer.writeheader()

        for block in (
            measurement_candidates
        ):

            writer.writerow(
                {
                    "block_id": (
                        block["block_id"]
                    ),
                    "study_id": (
                        block["study_id"]
                    ),
                    "pages": ",".join(
                        str(page)
                        for page
                        in block["pages"]
                    ),
                    "tags": ",".join(
                        block["tags"]
                    ),
                    "has_numeric": (
                        block[
                            "has_numeric"
                        ]
                    ),
                    "mixed_evidence": (
                        block[
                            "mixed_evidence"
                        ]
                    ),
                    "text": block[
                        "text"
                    ],
                    "human_status": (
                        "pending"
                    ),
                    "human_notes": "",
                }
            )

    print()
    print(
        "THIN-SHEET EVIDENCE QUEUE"
    )
    print(
        "-------------------------"
    )

    print(
        f"Section blocks       : "
        f"{len(blocks)}"
    )

    print(
        f"Measurement candidates: "
        f"{len(measurement_candidates)}"
    )

    print(
        f"Mixed evidence blocks: "
        f"{len(mixed_candidates)}"
    )

    print()
    print("Tags:")

    for tag, count in (
        tag_counts.items()
    ):
        print(
            f"  {tag:<14}: {count}"
        )

    print()
    print(
        f"JSON: {json_path}"
    )

    print(
        f"CSV : {csv_path}"
    )


if __name__ == "__main__":
    main()