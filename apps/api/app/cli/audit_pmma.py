import json

from app.analysis.feasibility import (
    audit_docling_document,
)
from app.core.paths import (
    CURATED_DATA_DIR,
    PARSED_DATA_DIR,
)


SOURCE_ID = "SRC-NASA-20210011385"


def main():
    source_directory = (
        PARSED_DATA_DIR / SOURCE_ID
    )

    json_files = list(
        source_directory.glob("*.json")
    )

    if not json_files:
        raise FileNotFoundError(
            f"No Docling JSON found in "
            f"{source_directory}"
        )

    input_path = json_files[0]

    print(
        f"Reading: {input_path}"
    )

    with input_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        document = json.load(file)

    result = audit_docling_document(
        document=document,
        source_id=SOURCE_ID,
    )

    output_directory = (
        CURATED_DATA_DIR
        / "feasibility"
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        output_directory
        / f"{SOURCE_ID}_pmma_audit.json"
    )

    output_path.write_text(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    summary = result["summary"]

    print()
    print("FIRESENSE PMMA FEASIBILITY AUDIT")
    print("--------------------------------")

    print(
        f"Text blocks       : "
        f"{summary['total_text_blocks']}"
    )

    print(
        f"Tables            : "
        f"{summary['total_tables']}"
    )

    print(
        f"Pictures          : "
        f"{summary['total_pictures']}"
    )

    print(
        f"PMMA blocks       : "
        f"{summary['pmma_candidate_blocks']}"
    )

    print(
        f"Numeric candidates: "
        f"{summary['pmma_numeric_candidates']}"
    )

    print()
    print("Keyword coverage:")

    for key, value in (
        summary[
            "keyword_group_counts"
        ].items()
    ):
        print(
            f"  {key:<12}: {value}"
        )

    print()
    print(
        f"Report saved to: {output_path}"
    )


if __name__ == "__main__":
    main()