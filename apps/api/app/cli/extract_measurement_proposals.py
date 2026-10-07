import csv
import json

from app.analysis.numeric_extractor import (
    build_measurement_proposal,
)

from app.core.paths import (
    CURATED_DATA_DIR,
)


SOURCE_ID = "SRC-NASA-20210011385"


def format_mentions(
    mentions,
) -> str:

    return "; ".join(
        (
            f"{item.value} {item.unit}"
            for item in mentions
        )
    )


def main():

    input_path = (
        CURATED_DATA_DIR
        / "thin_sheet"
        / "evidence_queue.json"
    )

    data = json.loads(
        input_path.read_text(
            encoding="utf-8"
        )
    )

    blocks = [
        block
        for block in data["blocks"]
        if block[
            "measurement_candidate"
        ]
    ]

    proposals = []

    for index, block in enumerate(
        blocks,
        start=1,
    ):
        proposal = (
            build_measurement_proposal(
                block=block,
                proposal_id=(
                    f"MEAS-{index:03d}"
                ),
                source_id=SOURCE_ID,
            )
        )

        proposals.append(
            proposal
        )

    output_dir = (
        CURATED_DATA_DIR
        / "thin_sheet"
    )

    json_path = (
        output_dir
        / "measurement_proposals.json"
    )

    json_path.write_text(
        json.dumps(
            {
                "source_id": SOURCE_ID,
                "proposal_count": len(
                    proposals
                ),
                "proposals": [
                    item.model_dump(
                        mode="json"
                    )
                    for item in proposals
                ],
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    csv_path = (
        output_dir
        / "measurement_proposals.csv"
    )

    with csv_path.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.writer(file)

        writer.writerow(
            [
                "proposal_id",
                "study_id",
                "pages",
                "evidence_form",
                "gravity_regime",
                "thickness",
                "oxygen",
                "pressure",
                "flow",
                "spread_rate",
                "figure_refs",
                "table_refs",
                "review_status",
                "warnings",
                "raw_text",
            ]
        )

        for item in proposals:

            writer.writerow(
                [
                    item.proposal_id,
                    item.study_id,
                    ",".join(
                        str(page)
                        for page
                        in item.pages
                    ),
                    item.evidence_form,
                    item.gravity_regime,
                    format_mentions(
                        item.thickness_mentions
                    ),
                    format_mentions(
                        item.oxygen_mentions
                    ),
                    format_mentions(
                        item.pressure_mentions
                    ),
                    format_mentions(
                        item.flow_mentions
                    ),
                    format_mentions(
                        item.spread_rate_mentions
                    ),
                    ",".join(
                        item.figure_refs
                    ),
                    ",".join(
                        item.table_refs
                    ),
                    item.review_status,
                    " | ".join(
                        item.warnings
                    ),
                    item.raw_text,
                ]
            )

    print()
    print(
        "FIRESENSE MEASUREMENT PROPOSALS"
    )
    print(
        "-------------------------------"
    )

    print(
        f"Proposals: {len(proposals)}"
    )

    print()

    for item in proposals:

        print(
            item.proposal_id,
            "| pages:",
            item.pages,
            "|",
            item.gravity_regime,
            "|",
            item.evidence_form,
        )

        print(
            "  thickness:",
            format_mentions(
                item.thickness_mentions
            ),
        )

        print(
            "  O2       :",
            format_mentions(
                item.oxygen_mentions
            ),
        )

        print(
            "  pressure :",
            format_mentions(
                item.pressure_mentions
            ),
        )

        print(
            "  flow     :",
            format_mentions(
                item.flow_mentions
            ),
        )

        print(
            "  spread   :",
            format_mentions(
                item.spread_rate_mentions
            ),
        )

        print(
            "  review   :",
            item.review_status,
        )

        if item.warnings:
            print(
                "  warnings :",
                "; ".join(
                    item.warnings
                ),
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