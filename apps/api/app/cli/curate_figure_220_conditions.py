import json

from app.core.paths import (
    CURATED_DATA_DIR,
)

from app.schemas.run_condition import (
    RunConditionRecord,
)


SOURCE_ID = "SRC-NASA-20210011385"

STUDY_ID = "BASSII-CH2.3-THIN-SHEET"


def main():

    common = {
        "source_id": SOURCE_ID,
        "study_id": STUDY_ID,

        "material_name": "PMMA",
        "geometry": "thin_sheet",

        "width_mm": 20.0,

        "gravity_regime": "microgravity",
        "reported_gravity_label": "0g",

        "oxygen_fraction": 0.207,
        "nitrogen_fraction": 0.79,

        "pressure_kpa": 101.325,

        "flow_direction": "opposed",

        "source_page": 49,
        "figure_ref": "2.20",

        "verified": True,
    }

    records = [
        RunConditionRecord(
            **common,

            run_id="BASS-II-B03",
            thickness_um=100,

            panel_label="a",

            evidence_text=(
                "Figure 2.20 identifies "
                "BASS-II B03 as a 100 µm "
                "PMMA sample in ISS 0g."
            ),
        ),

        RunConditionRecord(
            **common,

            run_id="BASS-II-B11",
            thickness_um=200,

            panel_label="b",

            evidence_text=(
                "Figure 2.20 identifies "
                "BASS-II B11 as a 200 µm "
                "PMMA sample in ISS 0g."
            ),
        ),

        RunConditionRecord(
            **common,

            run_id="BASS-II-B4",
            thickness_um=300,

            panel_label="c",

            evidence_text=(
                "Figure 2.20 identifies "
                "BASS-II B4 as a 300 µm "
                "PMMA sample in ISS 0g."
            ),
        ),

        RunConditionRecord(
            **common,

            run_id="BASS-II-B13",
            thickness_um=400,

            panel_label="d",

            evidence_text=(
                "Figure 2.20 identifies "
                "BASS-II B13 as a 400 µm "
                "PMMA sample in ISS 0g."
            ),
        ),
    ]

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
        / "run_conditions.jsonl"
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        for record in records:

            file.write(
                json.dumps(
                    record.model_dump(
                        mode="json"
                    ),
                    ensure_ascii=False,
                )
            )

            file.write("\n")

    print()
    print(
        "FIGURE 2.20 RUN CONDITIONS"
    )
    print(
        "--------------------------"
    )

    for record in records:

        print(
            f"{record.run_id:<13}"
            f" | {record.thickness_um:>3.0f} µm"
            f" | {record.oxygen_fraction:.3f} O2"
            f" | {record.pressure_kpa:.3f} kPa"
        )

    print()
    print(
        f"Saved: {output_path}"
    )


if __name__ == "__main__":
    main()