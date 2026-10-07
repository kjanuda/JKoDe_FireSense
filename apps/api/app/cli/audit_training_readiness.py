import json
from pathlib import Path

from app.core.paths import CURATED_DATA_DIR
from app.schemas.thin_sheet import ThinSheetExperimentRecord


SOURCE_ID = "SRC-NASA-20210011385"


def load_jsonl(
    path: Path,
) -> list[ThinSheetExperimentRecord]:

    if not path.exists():
        raise FileNotFoundError(
            f"Missing evidence file: {path}"
        )

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

                payload = json.loads(
                    line
                )

                record = (
                    ThinSheetExperimentRecord
                    .model_validate(
                        payload
                    )
                )

                records.append(
                    record
                )

            except Exception as exc:

                raise ValueError(
                    f"Invalid evidence record "
                    f"at line {line_number}: "
                    f"{exc}"
                ) from exc

    return records


def near(
    a: float,
    b: float,
    tolerance: float,
) -> bool:

    return (
        abs(a - b)
        <= tolerance
    )


def find_possible_cross_figure_duplicates(
    records: list[
        ThinSheetExperimentRecord
    ],
) -> dict[str, list[str]]:

    results: dict[
        str,
        list[str]
    ] = {}

    for record in records:

        matches = []

        if (
            record.flame_spread_rate_mm_s
            is None
        ):
            continue

        for other in records:

            if (
                record.record_id
                == other.record_id
            ):
                continue

            if (
                record.figure_ref
                == other.figure_ref
            ):
                continue

            if (
                record.gravity_regime
                != other.gravity_regime
            ):
                continue

            if (
                other.flame_spread_rate_mm_s
                is None
            ):
                continue

            same_thickness_region = near(
                record.thickness_um,
                other.thickness_um,
                tolerance=5.0,
            )

            similar_spread_region = near(
                record.flame_spread_rate_mm_s,
                other.flame_spread_rate_mm_s,
                tolerance=0.35,
            )

            if (
                same_thickness_region
                and similar_spread_region
            ):
                matches.append(
                    other.record_id
                )

        if matches:

            results[
                record.record_id
            ] = sorted(
                set(matches)
            )

    return results


def audit_record(
    record: ThinSheetExperimentRecord,
    duplicate_map: dict[
        str,
        list[str]
    ],
) -> dict:

    blockers = []
    warnings = []
    passes = []

    # ------------------------------------
    # Baseline evidence checks
    # ------------------------------------

    if (
        record.review_status
        != "accepted_evidence"
    ):
        blockers.append(
            "record_not_accepted_evidence"
        )
    else:
        passes.append(
            "accepted_evidence"
        )

    if not record.human_verified:

        blockers.append(
            "not_human_verified"
        )

    else:

        passes.append(
            "human_verified"
        )

    if (
        record.value_source
        == "figure_digitized"
    ):

        if not record.overlay_verified:

            blockers.append(
                "figure_overlay_not_verified"
            )

        else:

            passes.append(
                "figure_overlay_verified"
            )

    # ------------------------------------
    # Provenance completeness
    # ------------------------------------

    if (
        record.source_id
        != SOURCE_ID
    ):

        blockers.append(
            "unexpected_source_id"
        )

    if not record.figure_ref:

        blockers.append(
            "missing_figure_reference"
        )

    if not record.source_page:

        blockers.append(
            "missing_source_page"
        )

    # ------------------------------------
    # Experimental identity
    # ------------------------------------

    if record.run_id is None:

        warnings.append(
            "run_identity_unresolved"
        )

    else:

        passes.append(
            "run_identity_present"
        )

    # ------------------------------------
    # Conditions
    # ------------------------------------

    if (
        record.oxygen_fraction
        is None
    ):

        warnings.append(
            "oxygen_condition_missing"
        )

    else:

        passes.append(
            "oxygen_condition_present"
        )

    if (
        record.pressure_kpa
        is None
    ):

        warnings.append(
            "pressure_condition_missing"
        )

    else:

        passes.append(
            "pressure_condition_present"
        )

    if (
        record.gravity_regime
        == "microgravity"
        and record.gravity_g == 0.0
    ):

        blockers.append(
            "microgravity_incorrectly_encoded_as_zero_g"
        )

    # ------------------------------------
    # Digitization uncertainty
    # ------------------------------------

    if (
        record.value_source
        == "figure_digitized"
        and record.digitization_uncertainty_mm_s
        is None
    ):

        warnings.append(
            "digitization_uncertainty_not_quantified"
        )

    # ------------------------------------
    # Cross-figure duplicate risk
    # ------------------------------------

    possible_duplicates = (
        duplicate_map.get(
            record.record_id,
            [],
        )
    )

    if possible_duplicates:

        blockers.append(
            "possible_cross_figure_duplicate"
        )

    # ------------------------------------
    # Figure-specific rules
    # ------------------------------------

    if (
        record.figure_ref
        == "2.19"
    ):

        blockers.append(
            "figure_2_19_run_linkage_not_resolved"
        )

        warnings.append(
            "time_series_summary_not_independent_point_series"
        )

    if (
        record.figure_ref
        == "2.21"
    ):

        passes.append(
            "multi_thickness_experimental_figure"
        )

        if (
            record.run_id is None
        ):

            warnings.append(
                "figure_2_21_run_id_not_proven"
            )

    # ------------------------------------
    # Final classification
    # ------------------------------------

    if blockers:

        status = (
            "not_training_ready"
        )

    elif warnings:

        status = (
            "candidate_needs_review"
        )

    else:

        status = (
            "training_ready"
        )

    return {
        "record_id": (
            record.record_id
        ),

        "figure_ref": (
            record.figure_ref
        ),

        "gravity_regime": (
            record.gravity_regime
        ),

        "thickness_um": (
            record.thickness_um
        ),

        "spread_rate_mm_s": (
            record.flame_spread_rate_mm_s
        ),

        "status": status,

        "blockers": sorted(
            set(blockers)
        ),

        "warnings": sorted(
            set(warnings)
        ),

        "passes": sorted(
            set(passes)
        ),

        "possible_duplicate_records": (
            possible_duplicates
        ),
    }


def main():

    evidence_path = (
        CURATED_DATA_DIR
        / "thin_sheet"
        / "experiment_evidence.jsonl"
    )

    records = load_jsonl(
        evidence_path
    )

    duplicate_map = (
        find_possible_cross_figure_duplicates(
            records
        )
    )

    audits = [
        audit_record(
            record,
            duplicate_map,
        )
        for record in records
    ]

    training_ready = [
        item
        for item in audits
        if (
            item["status"]
            == "training_ready"
        )
    ]

    candidates = [
        item
        for item in audits
        if (
            item["status"]
            == "candidate_needs_review"
        )
    ]

    blocked = [
        item
        for item in audits
        if (
            item["status"]
            == "not_training_ready"
        )
    ]

    result = {
        "source_id": SOURCE_ID,

        "record_count": len(
            records
        ),

        "training_ready_count": len(
            training_ready
        ),

        "candidate_needs_review_count": len(
            candidates
        ),

        "not_training_ready_count": len(
            blocked
        ),

        "possible_cross_figure_duplicates": (
            duplicate_map
        ),

        "records": audits,

        "important_note": (
            "This audit does not mutate "
            "experiment_evidence.jsonl."
        ),
    }

    output_path = (
        CURATED_DATA_DIR
        / "thin_sheet"
        / "training_readiness_audit.json"
    )

    output_path.write_text(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print()
    print(
        "TRAINING READINESS AUDIT"
    )

    print(
        "------------------------"
    )

    print()
    print(
        f"Records              : "
        f"{len(records)}"
    )

    print(
        f"Training ready       : "
        f"{len(training_ready)}"
    )

    print(
        f"Needs review         : "
        f"{len(candidates)}"
    )

    print(
        f"Not training ready   : "
        f"{len(blocked)}"
    )

    print()
    print(
        "RECORD STATUS"
    )

    print(
        "-------------"
    )

    for item in audits:

        print()

        print(
            f"{item['record_id']}"
        )

        print(
            f"  figure : "
            f"{item['figure_ref']}"
        )

        print(
            f"  status : "
            f"{item['status']}"
        )

        if item[
            "possible_duplicate_records"
        ]:

            print(
                "  possible duplicates:"
            )

            for duplicate in item[
                "possible_duplicate_records"
            ]:

                print(
                    f"    - {duplicate}"
                )

        if item["blockers"]:

            print(
                "  blockers:"
            )

            for blocker in item[
                "blockers"
            ]:

                print(
                    f"    - {blocker}"
                )

        if item["warnings"]:

            print(
                "  warnings:"
            )

            for warning in item[
                "warnings"
            ]:

                print(
                    f"    - {warning}"
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
        "No evidence records were modified."
    )


if __name__ == "__main__":
    main()