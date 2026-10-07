import json
import hashlib
from pathlib import Path

from app.core.paths import CURATED_DATA_DIR


SOURCE_ID = "SRC-NASA-20210011385"

EXPECTED_TOTAL = 13
EXPECTED_MICROGRAVITY = 4
EXPECTED_NORMAL_GRAVITY = 9


def load_json(path: Path) -> dict:

    if not path.exists():
        raise FileNotFoundError(
            f"Missing required file: {path}"
        )

    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


def sha256_file(path: Path) -> str:

    digest = hashlib.sha256()

    with path.open("rb") as file:

        while True:

            chunk = file.read(
                1024 * 1024
            )

            if not chunk:
                break

            digest.update(
                chunk
            )

    return digest.hexdigest()


def main():

    curated_dir = (
        CURATED_DATA_DIR
        / "thin_sheet"
    )

    candidate_path = (
        curated_dir
        / "modeling_candidates_v0.json"
    )

    duplicate_policy_path = (
        curated_dir
        / "figure_2_22_duplicate_policy_v1.json"
    )

    series_roles_path = (
        curated_dir
        / "figure_2_22_series_roles_v2.json"
    )

    candidate_data = load_json(
        candidate_path
    )

    duplicate_policy = load_json(
        duplicate_policy_path
    )

    series_roles = load_json(
        series_roles_path
    )

    # -----------------------------------
    # Safety checks
    # -----------------------------------

    candidates = candidate_data.get(
        "candidates",
        []
    )

    if len(candidates) != EXPECTED_TOTAL:

        raise ValueError(
            f"Expected {EXPECTED_TOTAL} "
            f"candidates, found "
            f"{len(candidates)}."
        )

    if (
        duplicate_policy.get("status")
        != "duplicate_policy_locked"
    ):

        raise ValueError(
            "Figure 2.22 duplicate policy "
            "is not locked."
        )

    if (
        series_roles.get("status")
        != "series_role_model_corrected"
    ):

        raise ValueError(
            "Figure 2.22 series-role "
            "correction is not complete."
        )

    record_ids = [
        row["record_id"]
        for row in candidates
    ]

    if len(record_ids) != len(
        set(record_ids)
    ):

        raise ValueError(
            "Duplicate record IDs found."
        )

    # -----------------------------------
    # Figure policy
    # -----------------------------------

    bad_figures = [
        row["record_id"]
        for row in candidates
        if row.get("figure_ref")
        != "2.21"
    ]

    if bad_figures:

        raise ValueError(
            "Baseline dataset contains "
            "non-Figure-2.21 records: "
            f"{bad_figures}"
        )

    # -----------------------------------
    # Gravity groups
    # -----------------------------------

    microgravity = [
        row
        for row in candidates
        if (
            row.get(
                "gravity_regime"
            )
            == "microgravity"
        )
    ]

    normal_gravity = [
        row
        for row in candidates
        if (
            row.get(
                "gravity_regime"
            )
            == "normal_gravity"
        )
    ]

    if (
        len(microgravity)
        != EXPECTED_MICROGRAVITY
    ):

        raise ValueError(
            "Expected 4 microgravity rows."
        )

    if (
        len(normal_gravity)
        != EXPECTED_NORMAL_GRAVITY
    ):

        raise ValueError(
            "Expected 9 normal-gravity rows."
        )

    # -----------------------------------
    # Scientific-condition checks
    # -----------------------------------

    for row in candidates:

        if (
            row.get(
                "oxygen_fraction"
            )
            != 0.21
        ):

            raise ValueError(
                f"{row['record_id']}: "
                "unexpected oxygen fraction."
            )

        if (
            row.get(
                "pressure_kpa"
            )
            != 101.325
        ):

            raise ValueError(
                f"{row['record_id']}: "
                "unexpected pressure."
            )

        spread_rate = row.get(
            "spread_rate_mm_s"
        )

        thickness = row.get(
            "thickness_um"
        )

        if (
            spread_rate is None
            or spread_rate <= 0
        ):

            raise ValueError(
                f"{row['record_id']}: "
                "invalid spread rate."
            )

        if (
            thickness is None
            or thickness <= 0
        ):

            raise ValueError(
                f"{row['record_id']}: "
                "invalid thickness."
            )

        if (
            row.get(
                "digitization_uncertainty_mm_s"
            )
            is None
        ):

            raise ValueError(
                f"{row['record_id']}: "
                "missing digitization uncertainty."
            )

    # -----------------------------------
    # Sort canonical output
    # -----------------------------------

    gravity_order = {
        "microgravity": 0,
        "normal_gravity": 1,
    }

    frozen_rows = sorted(
        candidates,
        key=lambda row: (
            gravity_order.get(
                row[
                    "gravity_regime"
                ],
                99,
            ),
            row[
                "thickness_um"
            ],
        ),
    )

    # -----------------------------------
    # Write JSONL
    # -----------------------------------

    output_jsonl = (
        curated_dir
        / "baseline_dataset_v0.jsonl"
    )

    with output_jsonl.open(
        "w",
        encoding="utf-8",
    ) as file:

        for row in frozen_rows:

            output_row = dict(
                row
            )

            output_row[
                "baseline_dataset_version"
            ] = "v0"

            output_row[
                "baseline_use_status"
            ] = (
                "frozen_for_exploratory_"
                "physics_baseline"
            )

            output_row[
                "production_training_ready"
            ] = False

            file.write(
                json.dumps(
                    output_row,
                    ensure_ascii=False,
                )
            )

            file.write(
                "\n"
            )

    dataset_sha256 = sha256_file(
        output_jsonl
    )

    # -----------------------------------
    # Manifest
    # -----------------------------------

    manifest = {
        "dataset_name": (
            "FireSense PMMA Thin-Sheet "
            "Baseline Dataset v0"
        ),

        "dataset_version": "v0",

        "status": (
            "frozen_for_exploratory_"
            "physics_baseline"
        ),

        "source_id": SOURCE_ID,

        "canonical_evidence_figure": (
            "2.21"
        ),

        "record_count": len(
            frozen_rows
        ),

        "gravity_groups": {
            "microgravity": len(
                microgravity
            ),

            "normal_gravity": len(
                normal_gravity
            ),
        },

        "fixed_conditions": {
            "material": "PMMA",

            "geometry": (
                "thin_sheet"
            ),

            "oxygen_fraction": 0.21,

            "pressure_kpa": 101.325,
        },

        "outcome": (
            "flame_spread_rate_mm_s"
        ),

        "primary_input_for_v0": (
            "thickness_um"
        ),

        "secondary_grouping_input": (
            "gravity_regime"
        ),

        "digitization_uncertainty": {
            "included": True,

            "field": (
                "digitization_uncertainty_mm_s"
            ),

            "experimental_uncertainty": (
                "not yet available"
            ),
        },

        "excluded_evidence": {
            "figure_2_19": (
                "validation/context only; "
                "overlap risk"
            ),

            "figure_2_22_bass": (
                "comparison/validation only"
            ),

            "figure_2_22_nasa": (
                "comparison/validation only"
            ),

            "figure_2_22_astra": (
                "comparison/validation only"
            ),

            "figure_2_22_external_series": (
                "blocked pending provenance "
                "resolution"
            ),

            "theoretical_curves": (
                "never experimental training rows"
            ),
        },

        "validation_policy": [
            (
                "Do not claim cross-study "
                "generalization from this dataset."
            ),

            (
                "Do not use random row splitting "
                "as evidence of independent "
                "validation."
            ),

            (
                "Use this dataset only to develop "
                "and sanity-check the first "
                "physics baseline."
            ),

            (
                "Figure 2.22 external literature "
                "will later provide independent "
                "validation if provenance can "
                "be resolved."
            ),
        ],

        "production_training_ready": (
            False
        ),

        "dataset_file": str(
            output_jsonl
        ),

        "dataset_sha256": (
            dataset_sha256
        ),
    }

    manifest_path = (
        curated_dir
        / "baseline_dataset_v0_manifest.json"
    )

    manifest_path.write_text(
        json.dumps(
            manifest,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print()
    print(
        "FIRESENSE BASELINE DATASET V0"
    )

    print(
        "----------------------------"
    )

    print()
    print(
        f"Records        : "
        f"{len(frozen_rows)}"
    )

    print(
        f"Microgravity   : "
        f"{len(microgravity)}"
    )

    print(
        f"Normal gravity : "
        f"{len(normal_gravity)}"
    )

    print()
    print(
        "Canonical source:"
    )

    print(
        "  Figure 2.21"
    )

    print()
    print(
        "Excluded:"
    )

    print(
        "  Figure 2.19"
    )

    print(
        "  Figure 2.22 BASS/NASA/Astra"
    )

    print(
        "  Figure 2.22 unresolved "
        "external series"
    )

    print(
        "  theoretical curves"
    )

    print()
    print(
        "Dataset status:"
    )

    print(
        "  frozen_for_exploratory_"
        "physics_baseline"
    )

    print()

    print(
        "Production training ready:"
    )

    print(
        "  NO"
    )

    print()
    print(
        f"SHA256:"
    )

    print(
        f"  {dataset_sha256}"
    )

    print()
    print(
        "Saved:"
    )

    print(
        f"  {output_jsonl}"
    )

    print(
        f"  {manifest_path}"
    )


if __name__ == "__main__":
    main()