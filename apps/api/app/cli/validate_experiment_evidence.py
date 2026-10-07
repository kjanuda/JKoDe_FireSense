import json
from collections import Counter
from pathlib import Path

from app.core.paths import CURATED_DATA_DIR
from app.schemas.thin_sheet import ThinSheetExperimentRecord


EXPECTED_TOTAL = 15

EXPECTED_F219 = 2
EXPECTED_F221 = 13

EXPECTED_F221_MICROGRAVITY = 4
EXPECTED_F221_DOWNWARD = 9


def load_jsonl(
    path: Path,
) -> list[dict]:

    if not path.exists():
        raise FileNotFoundError(
            f"Evidence file not found: {path}"
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

            except json.JSONDecodeError as exc:

                raise ValueError(
                    f"Invalid JSON at line "
                    f"{line_number}: {exc}"
                ) from exc

            records.append(
                payload
            )

    return records


def main():

    evidence_path = (
        CURATED_DATA_DIR
        / "thin_sheet"
        / "experiment_evidence.jsonl"
    )

    raw_records = load_jsonl(
        evidence_path
    )

    validated_records = []
    schema_errors = []

    for index, payload in enumerate(
        raw_records,
        start=1,
    ):

        try:

            validated_records.append(
                ThinSheetExperimentRecord
                .model_validate(
                    payload
                )
            )

        except Exception as exc:

            schema_errors.append(
                {
                    "line": index,
                    "record_id": payload.get(
                        "record_id"
                    ),
                    "error": str(
                        exc
                    ),
                }
            )

    ids = [
        record.record_id
        for record in validated_records
    ]

    id_counts = Counter(
        ids
    )

    duplicates = sorted(
        record_id
        for record_id, count
        in id_counts.items()
        if count > 1
    )

    figure_219 = [
        record
        for record in validated_records
        if record.figure_ref == "2.19"
    ]

    figure_221 = [
        record
        for record in validated_records
        if record.figure_ref == "2.21"
    ]

    f221_microgravity = [
        record
        for record in figure_221
        if (
            record.gravity_regime
            == "microgravity"
        )
    ]

    f221_downward = [
        record
        for record in figure_221
        if (
            record.gravity_regime
            == "normal_gravity"
        )
    ]

    checks = {
        "schema_valid": (
            len(schema_errors) == 0
        ),

        "total_count": (
            len(validated_records)
            == EXPECTED_TOTAL
        ),

        "unique_record_ids": (
            len(duplicates) == 0
        ),

        "figure_219_count": (
            len(figure_219)
            == EXPECTED_F219
        ),

        "figure_221_count": (
            len(figure_221)
            == EXPECTED_F221
        ),

        "figure_221_microgravity_count": (
            len(f221_microgravity)
            == EXPECTED_F221_MICROGRAVITY
        ),

        "figure_221_downward_count": (
            len(f221_downward)
            == EXPECTED_F221_DOWNWARD
        ),

        "figure_221_all_accepted_evidence": all(
            record.review_status
            == "accepted_evidence"
            for record in figure_221
        ),

        "figure_221_no_run_ids": all(
            record.run_id is None
            for record in figure_221
        ),

        "figure_221_all_figure_digitized": all(
            record.value_source
            == "figure_digitized"
            for record in figure_221
        ),

        "figure_221_all_human_verified": all(
            record.human_verified
            is True
            for record in figure_221
        ),

        "figure_221_all_overlay_verified": all(
            record.overlay_verified
            is True
            for record in figure_221
        ),

        "figure_221_oxygen_is_21_percent": all(
            record.oxygen_fraction
            == 0.21
            for record in figure_221
        ),

        "figure_221_pressure_is_1_atm": all(
            record.pressure_kpa
            == 101.325
            for record in figure_221
        ),

        "microgravity_not_exact_zero_g": all(
            record.gravity_g is None
            for record in f221_microgravity
        ),

        "downward_is_1g": all(
            record.gravity_g == 1.0
            for record in f221_downward
        ),

        "no_negative_spread_rates": all(
            record.flame_spread_rate_mm_s
            is not None
            and record.flame_spread_rate_mm_s
            >= 0
            for record in figure_221
        ),

        "no_nonpositive_thickness": all(
            record.thickness_um > 0
            for record in figure_221
        ),
    }

    final_pass = all(
        checks.values()
    )

    print()
    print(
        "EXPERIMENT EVIDENCE VALIDATION"
    )

    print(
        "------------------------------"
    )

    print()
    print(
        f"Raw records       : "
        f"{len(raw_records)}"
    )

    print(
        f"Schema valid      : "
        f"{len(validated_records)}"
    )

    print(
        f"Schema errors     : "
        f"{len(schema_errors)}"
    )

    print()
    print(
        f"Figure 2.19       : "
        f"{len(figure_219)}"
    )

    print(
        f"Figure 2.21       : "
        f"{len(figure_221)}"
    )

    print(
        f"  microgravity    : "
        f"{len(f221_microgravity)}"
    )

    print(
        f"  downward        : "
        f"{len(f221_downward)}"
    )

    print()
    print(
        f"Duplicate IDs     : "
        f"{duplicates}"
    )

    print()
    print(
        "CHECKS"
    )

    print(
        "------"
    )

    for name, passed in checks.items():

        print(
            f"{name:<40}"
            f": "
            f"{'PASS' if passed else 'FAIL'}"
        )

    if schema_errors:

        print()
        print(
            "SCHEMA ERRORS"
        )

        print(
            "-------------"
        )

        for error in schema_errors:

            print(
                f"Line "
                f"{error['line']} "
                f"| "
                f"{error['record_id']} "
                f"| "
                f"{error['error']}"
            )

    print()
    print(
        "FINAL STATUS"
    )

    print(
        "------------"
    )

    print(
        "PASS"
        if final_pass
        else "FAIL"
    )

    result = {
        "file": str(
            evidence_path
        ),

        "record_count": len(
            validated_records
        ),

        "figure_counts": {
            "2.19": len(
                figure_219
            ),

            "2.21": len(
                figure_221
            ),

            "2.21_microgravity": len(
                f221_microgravity
            ),

            "2.21_downward": len(
                f221_downward
            ),
        },

        "duplicate_record_ids": (
            duplicates
        ),

        "checks": checks,

        "final_status": (
            "pass"
            if final_pass
            else "fail"
        ),

        "important_note": (
            "accepted_evidence does not "
            "mean training_ready"
        ),
    }

    output_path = (
        CURATED_DATA_DIR
        / "thin_sheet"
        / "experiment_evidence_validation.json"
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
        f"Validation JSON:"
    )

    print(
        f"  {output_path}"
    )


if __name__ == "__main__":
    main()