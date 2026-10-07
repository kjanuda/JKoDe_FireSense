import json
import math
from pathlib import Path

from app.core.paths import (
    CURATED_DATA_DIR,
    FIGURES_DATA_DIR,
)

from app.schemas.thin_sheet import (
    ThinSheetExperimentRecord,
)


SOURCE_ID = "SRC-NASA-20210011385"

PIXEL_UNCERTAINTY_PX = 4.0


def load_json(
    path: Path,
) -> dict:

    if not path.exists():
        raise FileNotFoundError(
            f"Missing file: {path}"
        )

    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


def load_evidence(
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

                records.append(
                    ThinSheetExperimentRecord
                    .model_validate(
                        payload
                    )
                )

            except Exception as exc:

                raise ValueError(
                    f"Invalid evidence at "
                    f"line {line_number}: {exc}"
                ) from exc

    return records


def calculate_digitization_uncertainty(
    calibration: dict,
) -> float:

    y_axis = calibration[
        "y_axis"
    ]

    value_range = abs(
        y_axis["value_max"]
        - y_axis["value_min"]
    )

    pixel_range = abs(
        y_axis["pixel_max"]
        - y_axis["pixel_min"]
    )

    if pixel_range == 0:

        raise ValueError(
            "Y-axis pixel range cannot be zero."
        )

    value_per_pixel = (
        value_range
        / pixel_range
    )

    return (
        value_per_pixel
        * PIXEL_UNCERTAINTY_PX
    )


def main():

    curated_dir = (
        CURATED_DATA_DIR
        / "thin_sheet"
    )

    evidence_path = (
        curated_dir
        / "experiment_evidence.jsonl"
    )

    calibration_path = (
        FIGURES_DATA_DIR
        / SOURCE_ID
        / "digitization"
        / "figure_2_21"
        / "calibration_metadata.json"
    )

    records = load_evidence(
        evidence_path
    )

    calibration = load_json(
        calibration_path
    )

    digitization_uncertainty = (
        calculate_digitization_uncertainty(
            calibration
        )
    )

    candidates = []

    excluded = []

    for record in records:

        # ----------------------------------
        # Figure 2.19 policy
        # ----------------------------------

        if record.figure_ref == "2.19":

            excluded.append(
                {
                    "record_id": (
                        record.record_id
                    ),

                    "figure_ref": (
                        record.figure_ref
                    ),

                    "reason": (
                        "Figure 2.19 is retained "
                        "as temporal/validation "
                        "evidence. It overlaps the "
                        "approximately 100 µm "
                        "Figure 2.21 observations "
                        "and has unresolved run "
                        "identity/atmosphere linkage."
                    ),

                    "use": (
                        "validation_or_context"
                    ),
                }
            )

            continue

        # ----------------------------------
        # Current modeling family
        # ----------------------------------

        if record.figure_ref != "2.21":

            excluded.append(
                {
                    "record_id": (
                        record.record_id
                    ),

                    "figure_ref": (
                        record.figure_ref
                    ),

                    "reason": (
                        "Not part of the current "
                        "Figure 2.21 thin-sheet "
                        "modeling family."
                    ),

                    "use": "excluded",
                }
            )

            continue

        # ----------------------------------
        # Figure 2.21 checks
        # ----------------------------------

        if (
            record.review_status
            != "accepted_evidence"
        ):

            excluded.append(
                {
                    "record_id": (
                        record.record_id
                    ),

                    "reason": (
                        "Not accepted evidence."
                    ),

                    "use": "excluded",
                }
            )

            continue

        if (
            not record.human_verified
            or not record.overlay_verified
        ):

            excluded.append(
                {
                    "record_id": (
                        record.record_id
                    ),

                    "reason": (
                        "Human/overlay verification "
                        "is incomplete."
                    ),

                    "use": "excluded",
                }
            )

            continue

        if (
            record.oxygen_fraction
            is None
            or record.pressure_kpa
            is None
        ):

            excluded.append(
                {
                    "record_id": (
                        record.record_id
                    ),

                    "reason": (
                        "Required atmosphere "
                        "condition is missing."
                    ),

                    "use": "excluded",
                }
            )

            continue

        if (
            record.flame_spread_rate_mm_s
            is None
        ):

            excluded.append(
                {
                    "record_id": (
                        record.record_id
                    ),

                    "reason": (
                        "Spread-rate outcome "
                        "is missing."
                    ),

                    "use": "excluded",
                }
            )

            continue

        # ----------------------------------
        # Candidate row
        # ----------------------------------

        relative_digitization_uncertainty = (
            digitization_uncertainty
            / record.flame_spread_rate_mm_s
        )

        candidates.append(
            {
                "record_id": (
                    record.record_id
                ),

                "source_id": (
                    record.source_id
                ),

                "study_id": (
                    record.study_id
                ),

                "figure_ref": (
                    record.figure_ref
                ),

                "material": (
                    record.material_name
                ),

                "geometry": (
                    record.geometry
                ),

                "gravity_regime": (
                    record.gravity_regime
                ),

                "gravity_g": (
                    record.gravity_g
                ),

                "thickness_um": (
                    record.thickness_um
                ),

                "oxygen_fraction": (
                    record.oxygen_fraction
                ),

                "pressure_kpa": (
                    record.pressure_kpa
                ),

                "flow_velocity_cm_s": (
                    record.flow_velocity_cm_s
                ),

                "flow_direction": (
                    record.flow_direction
                ),

                "spread_rate_mm_s": (
                    record.flame_spread_rate_mm_s
                ),

                "digitization_uncertainty_mm_s": (
                    round(
                        digitization_uncertainty,
                        6,
                    )
                ),

                "relative_digitization_uncertainty": (
                    round(
                        relative_digitization_uncertainty,
                        6,
                    )
                ),

                "experimental_uncertainty_mm_s": (
                    record.experimental_uncertainty_mm_s
                ),

                "run_id": (
                    record.run_id
                ),

                "run_identity_status": (
                    "unresolved"
                    if record.run_id is None
                    else "known"
                ),

                "modeling_status": (
                    "candidate_for_modeling_v0"
                ),

                "training_policy_notes": [
                    (
                        "Exact run identity is not "
                        "required for this figure-level "
                        "experimental summary observation."
                    ),
                    (
                        "No run-specific Appendix "
                        "conditions may be propagated "
                        "without a confirmed evidence link."
                    ),
                    (
                        "Figure 2.19 overlapping "
                        "observations are excluded "
                        "from training to prevent "
                        "double weighting."
                    ),
                    (
                        "Digitization uncertainty "
                        "is a method-level estimate "
                        "based on a conservative "
                        "4-pixel vertical placement "
                        "bound."
                    ),
                ],
            }
        )

    candidates.sort(
        key=lambda item: (
            item["gravity_regime"],
            item["thickness_um"],
        )
    )

    result = {
        "source_id": SOURCE_ID,

        "dataset_name": (
            "FireSense PMMA Thin-Sheet "
            "Modeling Candidates v0"
        ),

        "status": (
            "candidate_dataset_not_frozen"
        ),

        "policy": {
            "canonical_training_figure": (
                "2.21"
            ),

            "figure_2_19_policy": (
                "validation/context only"
            ),

            "run_id_required_for_figure_level_summary": (
                False
            ),

            "run_specific_condition_join_requires_confirmed_link": (
                True
            ),

            "pixel_uncertainty_px": (
                PIXEL_UNCERTAINTY_PX
            ),

            "digitization_uncertainty_mm_s": (
                round(
                    digitization_uncertainty,
                    6,
                )
            ),

            "experimental_uncertainty_policy": (
                "Remain separate and null "
                "unless explicitly supported "
                "by source evidence."
            ),
        },

        "candidate_count": len(
            candidates
        ),

        "excluded_count": len(
            excluded
        ),

        "candidates": candidates,

        "excluded": excluded,

        "important_notes": [
            (
                "This dataset is not yet the "
                "final frozen training dataset."
            ),
            (
                "All current candidates originate "
                "from one NASA report/study family."
            ),
            (
                "Random train/test splitting "
                "must not be used as evidence "
                "of cross-study generalization."
            ),
            (
                "Figure 2.22 and/or additional "
                "independent studies are needed "
                "for external validation."
            ),
        ],
    }

    output_json = (
        curated_dir
        / "modeling_candidates_v0.json"
    )

    output_json.write_text(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    output_jsonl = (
        curated_dir
        / "modeling_candidates_v0.jsonl"
    )

    with output_jsonl.open(
        "w",
        encoding="utf-8",
    ) as file:

        for candidate in candidates:

            file.write(
                json.dumps(
                    candidate,
                    ensure_ascii=False,
                )
            )

            file.write("\n")

    print()
    print(
        "MODELING CANDIDATE DATASET"
    )

    print(
        "--------------------------"
    )

    print()
    print(
        f"Evidence records : "
        f"{len(records)}"
    )

    print(
        f"Candidates       : "
        f"{len(candidates)}"
    )

    print(
        f"Excluded         : "
        f"{len(excluded)}"
    )

    print()

    print(
        "Digitization uncertainty:"
    )

    print(
        f"  pixel bound : "
        f"±{PIXEL_UNCERTAINTY_PX:.1f} px"
    )

    print(
        f"  y scale     : "
        f"{digitization_uncertainty / PIXEL_UNCERTAINTY_PX:.6f} "
        f"mm/s per px"
    )

    print(
        f"  uncertainty : "
        f"±{digitization_uncertainty:.6f} mm/s"
    )

    print()
    print(
        "CANDIDATES"
    )

    print(
        "----------"
    )

    for item in candidates:

        print(
            f"{item['record_id']:<16}"
            f" | "
            f"{item['gravity_regime']:<14}"
            f" | "
            f"{item['thickness_um']:>8.3f} µm"
            f" | "
            f"{item['spread_rate_mm_s']:>7.4f} mm/s"
            f" | "
            f"±{item['digitization_uncertainty_mm_s']:.4f}"
        )

    print()
    print(
        "EXCLUDED"
    )

    print(
        "--------"
    )

    for item in excluded:

        print(
            f"{item['record_id']:<16}"
            f" | "
            f"{item.get('figure_ref')}"
            f" | "
            f"{item['use']}"
        )

    print()
    print(
        "STATUS:"
    )

    print(
        "  candidate_dataset_not_frozen"
    )

    print()
    print(
        f"JSON : {output_json}"
    )

    print(
        f"JSONL: {output_jsonl}"
    )

    print()
    print(
        "Original evidence records "
        "were NOT modified."
    )


if __name__ == "__main__":
    main()