import json

from app.core.paths import CURATED_DATA_DIR
from app.schemas.run_condition import RunConditionRecord


SOURCE_ID = "SRC-NASA-20210011385"
STUDY_ID = "BASSII-CH2.3-THIN-SHEET"


def pct(value: float) -> float:
    return value / 100.0


def main():

    common = {
        "source_id": SOURCE_ID,
        "study_id": STUDY_ID,
        "material_name": "PMMA",
        "geometry": "thin_sheet",
        "gravity_regime": "microgravity",
        "reported_gravity_label": "0g",
        "flow_direction": "opposed",

        # Figure 2.20 nominal comparison condition.
        "nominal_oxygen_fraction": 0.207,
        "nominal_nitrogen_fraction": 0.79,
        "nominal_pressure_kpa": 101.325,

        "appendix_table": (
            "Table A.1 - Bhattacharjee Test Matrix"
        ),

        "verification_status": (
            "cross_source_verified"
        ),
    }

    records = [
        RunConditionRecord(
            **common,

            run_id="BASS-II-B03",
            source_test_id="B3",

            sample_number="148",

            thickness_um=100,
            width_mm=20,

            fan_display_sequence=[
                "47",
            ],

            air_display_sequence=[
                "2",
            ],

            calibrated_initial_o2_fraction=pct(22.2),
            calibrated_final_o2_fraction=pct(21.8),

            measured_initial_o2_fraction=pct(20.9),
            measured_final_o2_fraction=pct(20.5),

            initial_co2_fraction=pct(0.43),
            final_co2_fraction=pct(0.49),

            initial_co_ppm=12,
            final_co_ppm=19,

            actual_date="2014-02-19",
            approximate_time=(
                "12:26:33 to 12:27:01"
            ),

            as_run_test_number=11,

            pdf_page=112,
            printed_page=104,

            figure_ref="2.20",

            evidence_text=(
                "Appendix Table A.1 row B3: "
                "sample 148, 100 µm PMMA film, "
                "2 cm wide, opposed configuration. "
                "Figure 2.20 identifies the same "
                "100 µm BASS-II case as B03."
            ),

            notes=(
                "Canonical ID normalizes B3 to B03. "
                "Fan/Air display values are preserved "
                "as reported and are not automatically "
                "treated as physical flow velocity."
            ),
        ),

        RunConditionRecord(
            **common,

            run_id="BASS-II-B11",
            source_test_id="B11",

            sample_number="158m",

            thickness_um=200,
            width_mm=20,

            fan_display_sequence=[
                "2.5 (59)",
                "1.3",
                "0.7",
                "0.5",
                "0.35",
            ],

            air_display_sequence=[
                "5",
                "3",
                "1",
                "<1",
            ],

            calibrated_initial_o2_fraction=pct(21.0),
            calibrated_final_o2_fraction=pct(20.7),

            measured_initial_o2_fraction=pct(20.1),
            measured_final_o2_fraction=pct(19.8),

            initial_co2_fraction=pct(0.33),
            final_co2_fraction=pct(0.47),

            initial_co_ppm=0,
            final_co_ppm=46,

            actual_date="2014-07-07",
            approximate_time=None,

            as_run_test_number=61,

            pdf_page=111,
            printed_page=103,

            figure_ref="2.20",

            evidence_text=(
                "Appendix Table A.1 row B11: "
                "sample 158m, 2 cm wide, "
                "0.2 mm PMMA film, opposed flow."
            ),

            notes=(
                "Test observation: multiple velocities "
                "for steady spread; extinguished at "
                "pot setting 0.35."
            ),
        ),

        RunConditionRecord(
            **common,

            run_id="BASS-II-B4",
            source_test_id="B4",

            sample_number="159",

            thickness_um=300,
            width_mm=20,

            fan_display_sequence=[
                "61",
            ],

            air_display_sequence=[
                "5",
            ],

            calibrated_initial_o2_fraction=pct(22.2),
            calibrated_final_o2_fraction=pct(22.2),

            measured_initial_o2_fraction=pct(20.6),
            measured_final_o2_fraction=pct(20.6),

            initial_co2_fraction=pct(0.44),
            final_co2_fraction=pct(0.51),

            initial_co_ppm=-1,
            final_co_ppm=10,

            actual_date="2014-02-19",
            approximate_time=(
                "11:56:10 to 11:57:06"
            ),

            as_run_test_number=9,

            pdf_page=112,
            printed_page=104,

            figure_ref="2.20",

            evidence_text=(
                "Appendix Table A.1 row B4: "
                "sample 159, 300 µm PMMA film, "
                "2 cm wide, opposed configuration."
            ),

            notes=(
                "Test observation: bubble layer "
                "thickness increases with sample thickness."
            ),
        ),

        RunConditionRecord(
            **common,

            run_id="BASS-II-B13",
            source_test_id="B13",

            sample_number="162m",

            thickness_um=400,
            width_mm=20,

            fan_display_sequence=[
                "3.5 (68)",
                "1.7",
                "1.25",
                "0.9",
                "0.6",
                "0.4",
                "0.35",
            ],

            air_display_sequence=[
                "10",
                "5",
                "4",
                "3",
                "2",
                "1",
            ],

            calibrated_initial_o2_fraction=pct(21.0),
            calibrated_final_o2_fraction=pct(20.5),

            measured_initial_o2_fraction=pct(20.1),
            measured_final_o2_fraction=pct(19.6),

            initial_co2_fraction=pct(0.33),
            final_co2_fraction=pct(0.65),

            initial_co_ppm=0,
            final_co_ppm=61,

            actual_date="2014-07-07",
            approximate_time=None,

            as_run_test_number=63,

            pdf_page=111,
            printed_page=103,

            figure_ref="2.20",

            evidence_text=(
                "Appendix Table A.1 row B13: "
                "sample 162m, 2 cm wide, "
                "0.4 mm thick PMMA film, "
                "opposed flow."
            ),

            notes=(
                "Test observation: multiple velocities "
                "for steady spread; extinguished at "
                "pot setting 0.35."
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
        "VERIFIED APPENDIX RUN CONDITIONS"
    )
    print(
        "--------------------------------"
    )

    for record in records:

        print()
        print(
            f"{record.run_id}"
        )

        print(
            f"  source test : "
            f"{record.source_test_id}"
        )

        print(
            f"  sample      : "
            f"{record.sample_number}"
        )

        print(
            f"  thickness   : "
            f"{record.thickness_um:.0f} µm"
        )

        print(
            f"  nominal O2  : "
            f"{record.nominal_oxygen_fraction:.3f}"
        )

        print(
            f"  measured O2 : "
            f"{record.measured_initial_o2_fraction:.3f}"
            f" -> "
            f"{record.measured_final_o2_fraction:.3f}"
        )

        print(
            f"  PDF page    : "
            f"{record.pdf_page}"
        )

    print()
    print(
        f"Saved: {output_path}"
    )


if __name__ == "__main__":
    main()