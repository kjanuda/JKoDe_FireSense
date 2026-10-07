import json

from app.core.paths import CURATED_DATA_DIR
from app.schemas.evidence_link import EvidenceLink


SOURCE_ID = "SRC-NASA-20210011385"


def main():

    link = EvidenceLink(
        link_id="LINK-F219-0G-B03",

        source_id=SOURCE_ID,

        left_entity_type="experiment_record",
        left_entity_id="TS-F219-0G-001",

        right_entity_type="run_condition",
        right_entity_id="BASS-II-B03",

        relation="possible_same_run",

        # Conservative on purpose.
        status="unresolved",
        confidence=0.55,

        supporting_evidence=[
            (
                "Figure 2.19 microgravity series "
                "uses a 100 µm PMMA sample."
            ),
            (
                "Figure 2.20 identifies BASS-II B03 "
                "as a 100 µm ISS PMMA sample."
            ),
            (
                "Both belong to the same BASS-II "
                "thin-sheet experimental family."
            ),
        ],

        conflicting_or_missing_evidence=[
            (
                "No retrieved source statement explicitly "
                "states that Figure 2.19 uses B03."
            ),
            (
                "Figure 2.19 reports a 3 cm/s "
                "microgravity opposing-flow condition."
            ),
            (
                "Appendix B3/B03 records hardware/display "
                "settings, but these cannot yet be safely "
                "converted into the same physical flow "
                "quantity used in Figure 2.19."
            ),
            (
                "Nominal Figure 2.20 atmosphere and "
                "Appendix measured O2 values are not "
                "identical representations of condition."
            ),
        ],

        safe_for_training_join=False,

        notes=(
            "Do not propagate B03 run-level atmosphere "
            "or Appendix measurements into the Figure "
            "2.19 experiment record until the same-run "
            "identity is independently verified."
        ),
    )

    output_dir = (
        CURATED_DATA_DIR
        / "thin_sheet"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        output_dir
        / "evidence_links.jsonl"
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        file.write(
            json.dumps(
                link.model_dump(
                    mode="json"
                ),
                ensure_ascii=False,
            )
        )

        file.write("\n")

    print()
    print(
        "FIGURE 2.19 RUN LINK AUDIT"
    )
    print(
        "--------------------------"
    )

    print(
        f"Link       : {link.link_id}"
    )

    print(
        f"Figure rec : {link.left_entity_id}"
    )

    print(
        f"Run        : {link.right_entity_id}"
    )

    print(
        f"Relation   : {link.relation}"
    )

    print(
        f"Status     : {link.status}"
    )

    print(
        f"Confidence : {link.confidence:.2f}"
    )

    print(
        f"Training   : "
        f"{'YES' if link.safe_for_training_join else 'NO'}"
    )

    print()
    print(
        "Supporting evidence:"
    )

    for item in link.supporting_evidence:
        print(
            f"  + {item}"
        )

    print()
    print(
        "Missing/conflicting evidence:"
    )

    for item in (
        link.conflicting_or_missing_evidence
    ):
        print(
            f"  - {item}"
        )

    print()
    print(
        f"Saved: {output_path}"
    )


if __name__ == "__main__":
    main()