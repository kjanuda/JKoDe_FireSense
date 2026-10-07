import json
import shutil
from pathlib import Path

from app.core.paths import (
    CURATED_DATA_DIR,
    FIGURES_DATA_DIR,
)

from app.schemas.thin_sheet import (
    ThinSheetExperimentRecord,
)


SOURCE_ID = "SRC-NASA-20210011385"

STUDY_ID = "BASSII-CH2.3-THIN-SHEET"

SOURCE_PAGE = 50

EXPECTED_MICROGRAVITY_POINTS = 4
EXPECTED_DOWNWARD_POINTS = 9


def load_json(
    path: Path,
) -> dict:

    if not path.exists():
        raise FileNotFoundError(
            f"Missing required file: {path}"
        )

    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


def load_existing_jsonl(
    path: Path,
) -> list[dict]:

    if not path.exists():
        return []

    records = []

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        for line_number, raw_line in enumerate(
            file,
            start=1,
        ):

            line = raw_line.strip()

            if not line:
                continue

            try:
                records.append(
                    json.loads(
                        line
                    )
                )

            except json.JSONDecodeError as exc:

                raise ValueError(
                    f"Invalid JSONL at "
                    f"{path}, line {line_number}: "
                    f"{exc}"
                ) from exc

    return records


def validate_review_input(
    review: dict,
):

    if (
        review.get("source_id")
        != SOURCE_ID
    ):
        raise ValueError(
            "Unexpected source_id in "
            "Figure 2.21 review file."
        )

    if (
        review.get("figure_ref")
        != "2.21"
    ):
        raise ValueError(
            "Review file is not for "
            "Figure 2.21."
        )

    if review.get(
        "theoretical_curve_included"
    ):
        raise ValueError(
            "Theoretical curve must not "
            "be included in experimental "
            "evidence."
        )

    series = review.get(
        "series",
        {},
    )

    microgravity = series.get(
        "microgravity",
        {},
    )

    downward = series.get(
        "downward",
        {},
    )

    micro_points = microgravity.get(
        "points",
        [],
    )

    downward_points = downward.get(
        "points",
        [],
    )

    if (
        len(micro_points)
        != EXPECTED_MICROGRAVITY_POINTS
    ):
        raise ValueError(
            "Expected exactly "
            f"{EXPECTED_MICROGRAVITY_POINTS} "
            "reviewed microgravity points, "
            f"found {len(micro_points)}."
        )

    if (
        len(downward_points)
        != EXPECTED_DOWNWARD_POINTS
    ):
        raise ValueError(
            "Expected exactly "
            f"{EXPECTED_DOWNWARD_POINTS} "
            "reviewed downward points, "
            f"found {len(downward_points)}."
        )

    for name, points in (
        (
            "microgravity",
            micro_points,
        ),
        (
            "downward",
            downward_points,
        ),
    ):

        previous_thickness = None

        for point in points:

            thickness = point.get(
                "thickness_um"
            )

            spread_rate = point.get(
                "spread_rate_mm_s"
            )

            if (
                not isinstance(
                    thickness,
                    (int, float),
                )
                or thickness <= 0
            ):
                raise ValueError(
                    f"Invalid thickness in "
                    f"{name}: {point}"
                )

            if (
                not isinstance(
                    spread_rate,
                    (int, float),
                )
                or spread_rate < 0
            ):
                raise ValueError(
                    f"Invalid spread rate in "
                    f"{name}: {point}"
                )

            if (
                previous_thickness
                is not None
                and thickness
                <= previous_thickness
            ):
                raise ValueError(
                    f"{name} thicknesses are "
                    "not strictly increasing."
                )

            previous_thickness = (
                thickness
            )


def create_microgravity_records(
    points: list[dict],
) -> list[
    ThinSheetExperimentRecord
]:

    records = []

    for index, point in enumerate(
        points,
        start=1,
    ):

        record = (
            ThinSheetExperimentRecord(
                record_id=(
                    f"TS-F221-MG-{index:03d}"
                ),

                source_id=SOURCE_ID,

                study_id=STUDY_ID,

                run_id=None,

                thickness_um=(
                    point[
                        "thickness_um"
                    ]
                ),

                gravity_regime=(
                    "microgravity"
                ),

                gravity_g=None,

                reported_gravity_label=(
                    "microgravity"
                ),

                # Figure 2.21 legend:
                # 21 percent O2, 1 atm.
                oxygen_fraction=0.21,

                pressure_kpa=101.325,

                # Do not infer physical
                # opposed-flow velocity
                # from other figures/runs.
                flow_velocity_cm_s=None,

                flow_direction=(
                    "opposed"
                ),

                flame_spread_rate_mm_s=(
                    point[
                        "spread_rate_mm_s"
                    ]
                ),

                sustained_flame=None,
                extinguished=None,

                observation_type=(
                    "spread_rate"
                ),

                outcome_summary_method=(
                    "figure_digitized_point"
                ),

                value_source=(
                    "figure_digitized"
                ),

                source_page=(
                    SOURCE_PAGE
                ),

                figure_ref="2.21",

                figure_panel=None,

                evidence_text=(
                    "Figure 2.21 blue filled "
                    "circle: experimental flame "
                    "spread rate at 21 percent "
                    "O2 and 1 atm in microgravity."
                ),

                estimated_from_figure=True,

                overlay_verified=True,

                human_verified=True,

                review_status=(
                    "accepted_evidence"
                ),

                digitization_uncertainty_mm_s=None,

                experimental_uncertainty_mm_s=None,

                notes=(
                    "Human-reviewed Figure 2.21 "
                    "digitization. The continuous "
                    "red thin-behavior curve is "
                    "excluded. No BASS-II run ID "
                    "is assigned because same-run "
                    "identity has not been proven. "
                    "Accepted evidence only; not "
                    "training-ready."
                ),
            )
        )

        records.append(
            record
        )

    return records


def create_downward_records(
    points: list[dict],
) -> list[
    ThinSheetExperimentRecord
]:

    records = []

    for index, point in enumerate(
        points,
        start=1,
    ):

        record = (
            ThinSheetExperimentRecord(
                record_id=(
                    f"TS-F221-DW-{index:03d}"
                ),

                source_id=SOURCE_ID,

                study_id=STUDY_ID,

                run_id=None,

                thickness_um=(
                    point[
                        "thickness_um"
                    ]
                ),

                gravity_regime=(
                    "normal_gravity"
                ),

                gravity_g=1.0,

                reported_gravity_label=(
                    "downward / 1g"
                ),

                # Figure 2.21 legend:
                # 21 percent O2, 1 atm.
                oxygen_fraction=0.21,

                pressure_kpa=101.325,

                flow_velocity_cm_s=None,

                flow_direction=(
                    "buoyancy_generated_opposed"
                ),

                flame_spread_rate_mm_s=(
                    point[
                        "spread_rate_mm_s"
                    ]
                ),

                sustained_flame=None,
                extinguished=None,

                observation_type=(
                    "spread_rate"
                ),

                outcome_summary_method=(
                    "figure_digitized_point"
                ),

                value_source=(
                    "figure_digitized"
                ),

                source_page=(
                    SOURCE_PAGE
                ),

                figure_ref="2.21",

                figure_panel=None,

                evidence_text=(
                    "Figure 2.21 red open "
                    "circle: experimental downward "
                    "flame-spread rate at 21 percent "
                    "O2 and 1 atm."
                ),

                estimated_from_figure=True,

                overlay_verified=True,

                human_verified=True,

                review_status=(
                    "accepted_evidence"
                ),

                digitization_uncertainty_mm_s=None,

                experimental_uncertainty_mm_s=None,

                notes=(
                    "Human-reviewed Figure 2.21 "
                    "digitization. Natural "
                    "convection supplies the "
                    "opposing flow in the downward "
                    "configuration. The theoretical "
                    "curve is excluded. Accepted "
                    "evidence only; not "
                    "training-ready."
                ),
            )
        )

        records.append(
            record
        )

    return records


def merge_records(
    existing: list[dict],
    new_records: list[
        ThinSheetExperimentRecord
    ],
) -> list[dict]:

    new_payloads = [
        record.model_dump(
            mode="json"
        )
        for record in new_records
    ]

    new_ids = {
        payload["record_id"]
        for payload in new_payloads
    }

    preserved = []

    for payload in existing:

        record_id = payload.get(
            "record_id"
        )

        # Remove an older copy of the
        # same Figure 2.21 record so
        # rerunning this script is safe.
        if record_id in new_ids:
            continue

        preserved.append(
            payload
        )

    return (
        preserved
        + new_payloads
    )


def write_jsonl_atomically(
    path: Path,
    records: list[dict],
):

    temporary_path = (
        path.with_suffix(
            path.suffix + ".tmp"
        )
    )

    with temporary_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        for record in records:

            file.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                )
            )

            file.write(
                "\n"
            )

    temporary_path.replace(
        path
    )


def main():

    figure_dir = (
        FIGURES_DATA_DIR
        / SOURCE_ID
        / "digitization"
        / "figure_2_21"
    )

    review_path = (
        figure_dir
        / "figure_2_21_final_review.json"
    )

    curated_dir = (
        CURATED_DATA_DIR
        / "thin_sheet"
    )

    curated_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        curated_dir
        / "experiment_evidence.jsonl"
    )

    review = load_json(
        review_path
    )

    validate_review_input(
        review
    )

    series = review[
        "series"
    ]

    microgravity_records = (
        create_microgravity_records(
            series[
                "microgravity"
            ][
                "points"
            ]
        )
    )

    downward_records = (
        create_downward_records(
            series[
                "downward"
            ][
                "points"
            ]
        )
    )

    figure_221_records = (
        microgravity_records
        + downward_records
    )

    existing_records = (
        load_existing_jsonl(
            output_path
        )
    )

    # Make one backup before the first
    # Figure 2.21 curation.
    if output_path.exists():

        backup_path = (
            curated_dir
            / (
                "experiment_evidence"
                ".before_figure_2_21"
                ".jsonl"
            )
        )

        if not backup_path.exists():

            shutil.copy2(
                output_path,
                backup_path,
            )

            print(
                f"Backup : {backup_path}"
            )

    merged = merge_records(
        existing=existing_records,
        new_records=figure_221_records,
    )

    write_jsonl_atomically(
        output_path,
        merged,
    )

    print()
    print(
        "FIGURE 2.21 CURATED EVIDENCE"
    )

    print(
        "----------------------------"
    )

    print()
    print(
        f"Microgravity records : "
        f"{len(microgravity_records)}"
    )

    print(
        f"Downward records     : "
        f"{len(downward_records)}"
    )

    print(
        f"Figure 2.21 total    : "
        f"{len(figure_221_records)}"
    )

    print()

    for record in (
        figure_221_records
    ):

        print(
            f"{record.record_id:<16}"
            f" | "
            f"{record.gravity_regime:<14}"
            f" | "
            f"{record.thickness_um:>8.3f} µm"
            f" | "
            f"{record.flame_spread_rate_mm_s:>7.4f} mm/s"
            f" | "
            f"{record.review_status}"
        )

    print()
    print(
        f"Existing before merge: "
        f"{len(existing_records)}"
    )

    print(
        f"Total after merge    : "
        f"{len(merged)}"
    )

    print()

    print(
        f"Saved:"
    )

    print(
        f"  {output_path}"
    )

    print()

    print(
        "IMPORTANT:"
    )

    print(
        "  Figure 2.21 records are "
        "accepted_evidence, NOT "
        "training_ready."
    )

    print(
        "  No run IDs were inferred."
    )

    print(
        "  The theoretical curve was "
        "not added."
    )


if __name__ == "__main__":
    main()