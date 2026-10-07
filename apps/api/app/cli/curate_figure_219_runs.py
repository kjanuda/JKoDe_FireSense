import json

from app.core.paths import (
    CURATED_DATA_DIR,
    FIGURES_DATA_DIR,
)

from app.schemas.thin_sheet import (
    ThinSheetExperimentRecord,
)


SOURCE_ID = "SRC-NASA-20210011385"


def main():

    validation_path = (
        FIGURES_DATA_DIR
        / SOURCE_ID
        / "digitization"
        / "figure_2_19"
        / "trace_validation.json"
    )

    validation = json.loads(
        validation_path.read_text(
            encoding="utf-8"
        )
    )

    zero_g_mean = (
        validation["series"]["0g"][
            "mean_mm_s"
        ]
    )

    one_g_mean = (
        validation["series"]["1g"][
            "mean_mm_s"
        ]
    )

    microgravity_record = (
        ThinSheetExperimentRecord(
            record_id="TS-F219-0G-001",

            source_id=SOURCE_ID,

            study_id=(
                "BASSII-CH2.3-THIN-SHEET"
            ),

            thickness_um=100,

            gravity_regime="microgravity",
            gravity_g=None,
            reported_gravity_label="0g",

            # Verified for this comparison:
            flow_velocity_cm_s=3.0,
            flow_direction="opposed",

            flame_spread_rate_mm_s=(
                zero_g_mean
            ),

            sustained_flame=True,

            observation_type="spread_rate",

            outcome_summary_method=(
                "digitized_time_series_mean"
            ),

            value_source="figure_digitized",

            source_page=48,
            figure_ref="2.19",
            figure_panel="B",

            evidence_text=(
                "Figure 2.19 compares flame "
                "spread over 100 µm PMMA in "
                "microgravity and downward "
                "normal gravity. The source "
                "states that the microgravity "
                "experiment used an opposing "
                "flow velocity of 3 cm/s."
            ),

            estimated_from_figure=True,

            overlay_verified=True,
            human_verified=True,

            review_status=(
                "accepted_evidence"
            ),

            notes=(
                "Mean calculated from the "
                "human-reviewed digitized "
                "Figure 2.19(b) time series. "
                "O2 and pressure intentionally "
                "left null until same-run "
                "condition linkage is verified."
            ),
        )
    )

    normal_gravity_record = (
        ThinSheetExperimentRecord(
            record_id="TS-F219-1G-001",

            source_id=SOURCE_ID,

            study_id=(
                "BASSII-CH2.3-THIN-SHEET"
            ),

            thickness_um=100,

            gravity_regime="normal_gravity",
            gravity_g=1.0,
            reported_gravity_label="1g",

            # Natural convection creates
            # the opposing flow here;
            # no forced velocity is bound
            # to this record.
            flow_velocity_cm_s=None,

            flow_direction=(
                "buoyancy_generated_opposed"
            ),

            flame_spread_rate_mm_s=(
                one_g_mean
            ),

            sustained_flame=True,

            observation_type="spread_rate",

            outcome_summary_method=(
                "digitized_time_series_mean"
            ),

            value_source="figure_digitized",

            source_page=48,
            figure_ref="2.19",
            figure_panel="B",

            evidence_text=(
                "Figure 2.19 compares the "
                "100 µm PMMA microgravity "
                "and downward normal-gravity "
                "spread-rate histories. The "
                "source reports an average "
                "normal-gravity spread rate "
                "of 2.0 mm/s."
            ),

            estimated_from_figure=True,

            overlay_verified=True,
            human_verified=True,

            review_status=(
                "accepted_evidence"
            ),

            notes=(
                "Digitized series mean is "
                "approximately 2.013 mm/s, "
                "consistent with the source-"
                "reported average of 2.0 mm/s. "
                "O2 and pressure intentionally "
                "left null until same-run "
                "condition linkage is verified."
            ),
        )
    )

    records = [
        microgravity_record,
        normal_gravity_record,
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
        / "experiment_evidence.jsonl"
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
        "CURATED FIGURE 2.19 EVIDENCE"
    )
    print(
        "----------------------------"
    )

    for record in records:

        print()

        print(
            f"Record : {record.record_id}"
        )

        print(
            f"Gravity: "
            f"{record.gravity_regime}"
        )

        print(
            f"Spread : "
            f"{record.flame_spread_rate_mm_s:.4f} "
            f"mm/s"
        )

        print(
            f"Flow   : "
            f"{record.flow_velocity_cm_s}"
        )

        print(
            f"Status : "
            f"{record.review_status}"
        )

    print()
    print(
        f"Saved: {output_path}"
    )

    print()
    print(
        "NOTE: accepted_evidence != "
        "training_ready"
    )


if __name__ == "__main__":
    main()