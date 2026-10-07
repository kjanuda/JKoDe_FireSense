import json
from collections import Counter

from app.core.paths import CURATED_DATA_DIR
from app.schemas.run_condition import RunConditionRecord


EXPECTED_RUNS = {
    "BASS-II-B03",
    "BASS-II-B11",
    "BASS-II-B4",
    "BASS-II-B13",
}


def main():

    input_path = (
        CURATED_DATA_DIR
        / "thin_sheet"
        / "run_conditions.jsonl"
    )

    if not input_path.exists():
        raise FileNotFoundError(
            f"Run-condition file not found: "
            f"{input_path}"
        )

    records = []

    errors = []

    with input_path.open(
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
                    RunConditionRecord
                    .model_validate(
                        payload
                    )
                )

                records.append(
                    record
                )

            except Exception as exc:

                errors.append(
                    {
                        "line": line_number,
                        "error": str(exc),
                    }
                )

    print()
    print(
        "RUN CONDITION VALIDATION"
    )
    print(
        "------------------------"
    )

    print(
        f"Records : {len(records)}"
    )

    print(
        f"Errors  : {len(errors)}"
    )

    ids = [
        record.run_id
        for record in records
    ]

    duplicates = [
        run_id
        for run_id, count
        in Counter(ids).items()
        if count > 1
    ]

    actual_runs = set(
        ids
    )

    missing_runs = (
        EXPECTED_RUNS
        - actual_runs
    )

    unexpected_runs = (
        actual_runs
        - EXPECTED_RUNS
    )

    print()
    print(
        "RUN IDS"
    )

    for record in records:

        print(
            f"  {record.run_id:<13} "
            f"{record.thickness_um:>4.0f} µm "
            f"| sample={record.sample_number}"
        )

    print()
    print(
        f"Duplicates : "
        f"{sorted(duplicates)}"
    )

    print(
        f"Missing    : "
        f"{sorted(missing_runs)}"
    )

    print(
        f"Unexpected : "
        f"{sorted(unexpected_runs)}"
    )

    # ---------------------------------
    # Scientific consistency checks
    # ---------------------------------

    checks = []

    for record in records:

        run_checks = {
            "run_id": record.run_id,

            "valid_thickness": (
                record.thickness_um
                in {
                    100,
                    200,
                    300,
                    400,
                }
            ),

            "valid_width": (
                record.width_mm
                == 20.0
            ),

            "microgravity": (
                record.gravity_regime
                == "microgravity"
            ),

            "opposed_flow": (
                record.flow_direction
                == "opposed"
            ),

            "nominal_o2_valid": (
                record.nominal_oxygen_fraction
                is not None
                and 0.0
                < record.nominal_oxygen_fraction
                <= 1.0
            ),

            "measured_o2_valid": (
                record.measured_initial_o2_fraction
                is not None
                and record.measured_final_o2_fraction
                is not None
                and 0.0
                < record.measured_initial_o2_fraction
                <= 1.0
                and 0.0
                < record.measured_final_o2_fraction
                <= 1.0
            ),

            "calibrated_o2_valid": (
                record.calibrated_initial_o2_fraction
                is not None
                and record.calibrated_final_o2_fraction
                is not None
                and 0.0
                < record.calibrated_initial_o2_fraction
                <= 1.0
                and 0.0
                < record.calibrated_final_o2_fraction
                <= 1.0
            ),

            "flow_velocity_not_invented": (
                record.flow_velocity_cm_s
                is None
            ),

            "appendix_verified": (
                record.verification_status
                in {
                    "appendix_verified",
                    "cross_source_verified",
                }
            ),
        }

        checks.append(
            run_checks
        )

    all_checks_pass = True

    print()
    print(
        "SCIENTIFIC CHECKS"
    )
    print(
        "-----------------"
    )

    for check in checks:

        run_id = check["run_id"]

        passed = all(
            value
            for key, value
            in check.items()
            if key != "run_id"
        )

        if not passed:
            all_checks_pass = False

        print(
            f"{run_id:<13}: "
            f"{'PASS' if passed else 'FAIL'}"
        )

        if not passed:

            for (
                key,
                value,
            ) in check.items():

                if (
                    key != "run_id"
                    and not value
                ):
                    print(
                        f"    failed: {key}"
                    )

    structural_pass = (
        not errors
        and not duplicates
        and not missing_runs
        and not unexpected_runs
    )

    final_pass = (
        structural_pass
        and all_checks_pass
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

    if errors:

        print()
        print(
            "VALIDATION ERRORS"
        )

        for error in errors:

            print(
                f"Line {error['line']}: "
                f"{error['error']}"
            )


if __name__ == "__main__":
    main()