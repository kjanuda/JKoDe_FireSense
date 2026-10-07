import hashlib
import json
import math
from pathlib import Path

from app.core.paths import CURATED_DATA_DIR


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


def sha256_file(
    path: Path,
) -> str:
    hasher = hashlib.sha256()

    with path.open(
        "rb"
    ) as file:
        for chunk in iter(
            lambda: file.read(
                1024 * 1024
            ),
            b"",
        ):
            hasher.update(
                chunk
            )

    return hasher.hexdigest()


def main() -> None:
    models_dir = (
        CURATED_DATA_DIR
        / "thin_sheet"
        / "models"
    )

    coverage_path = (
        models_dir
        / "coverage_next_experiment_candidate_v0.json"
    )

    bayesian_path = (
        models_dir
        / "bayesian_next_experiment_candidate_v0.json"
    )

    output_path = (
        models_dir
        / "next_experiment_decision_v0.json"
    )

    coverage = load_json(
        coverage_path
    )

    bayesian = load_json(
        bayesian_path
    )

    coverage_candidate = (
        coverage[
            "candidate"
        ]
    )

    bayesian_candidate = (
        bayesian[
            "candidate"
        ]
    )

    coverage_thickness = float(
        coverage_candidate[
            "matched_pair"
        ][
            "thickness_um"
        ]
    )

    bayesian_thickness = float(
        bayesian_candidate[
            "thickness_um"
        ]
    )

    absolute_difference = abs(
        bayesian_thickness
        - coverage_thickness
    )

    mean_thickness = (
        bayesian_thickness
        + coverage_thickness
    ) / 2.0

    relative_difference = (
        absolute_difference
        / mean_thickness
    )

    within_one_percent = (
        relative_difference
        <= 0.01
    )

    if not (
        coverage_candidate[
            "approval_status"
        ]
        == "not_approved"
    ):
        raise ValueError(
            "Coverage candidate has "
            "unexpected approval state."
        )

    if not (
        bayesian[
            "approval_status"
        ]
        == "not_approved"
    ):
        raise ValueError(
            "Bayesian candidate has "
            "unexpected approval state."
        )

    if (
        coverage[
            "dataset_version"
        ]
        != bayesian[
            "dataset_version"
        ]
    ):
        raise ValueError(
            "Dataset versions differ."
        )

    if (
        coverage[
            "canonical_evidence_figure"
        ]
        != bayesian[
            "canonical_evidence_figure"
        ]
    ):
        raise ValueError(
            "Canonical evidence figures differ."
        )

    if (
        coverage[
            "source_id"
        ]
        != bayesian[
            "source_id"
        ]
    ):
        raise ValueError(
            "Source IDs differ."
        )

    decision = {
        "decision_record_name": (
            "FireSense Next Experiment "
            "Decision Record v0"
        ),

        "decision_record_version": "v0",

        "source_id": (
            coverage[
                "source_id"
            ]
        ),

        "dataset_version": (
            coverage[
                "dataset_version"
            ]
        ),

        "dataset_sha256": (
            coverage[
                "dataset_sha256"
            ]
        ),

        "canonical_evidence_figure": (
            coverage[
                "canonical_evidence_figure"
            ]
        ),

        "input_artifacts": {
            "coverage_candidate": {
                "filename": (
                    coverage_path.name
                ),

                "sha256": (
                    sha256_file(
                        coverage_path
                    )
                ),

                "candidate_id": (
                    coverage_candidate[
                        "candidate_id"
                    ]
                ),

                "matched_thickness_um": (
                    coverage_thickness
                ),

                "recommendation_status": (
                    coverage_candidate[
                        "recommendation_status"
                    ]
                ),

                "approval_status": (
                    coverage_candidate[
                        "approval_status"
                    ]
                ),
            },

            "bayesian_candidate": {
                "filename": (
                    bayesian_path.name
                ),

                "sha256": (
                    sha256_file(
                        bayesian_path
                    )
                ),

                "candidate_id": (
                    bayesian[
                        "candidate_id"
                    ]
                ),

                "matched_thickness_um": (
                    bayesian_thickness
                ),

                "recommendation_status": (
                    bayesian[
                        "recommendation_status"
                    ]
                ),

                "approval_status": (
                    bayesian[
                        "approval_status"
                    ]
                ),
            },
        },

        "agreement_analysis": {
            "coverage_thickness_um": (
                coverage_thickness
            ),

            "bayesian_thickness_um": (
                bayesian_thickness
            ),

            "absolute_difference_um": (
                absolute_difference
            ),

            "relative_difference": (
                relative_difference
            ),

            "relative_difference_percent": (
                relative_difference
                * 100.0
            ),

            "within_one_percent": (
                within_one_percent
            ),

            "interpretation": (
                "The empirical coverage heuristic "
                "and Bayesian matched-pair "
                "pure-exploration acquisition "
                "identify closely aligned "
                "thickness regions."
            ),
        },

        "selected_research_candidate": {
            "thickness_um": (
                bayesian_thickness
            ),

            "selection_source": (
                "bayesian_next_experiment_"
                "candidate_v0"
            ),

            "selection_basis": (
                "The Bayesian matched-pair "
                "candidate is selected as the "
                "current research-priority "
                "candidate because it directly "
                "optimizes posterior uncertainty "
                "within the shared empirical "
                "thickness domain. The coverage "
                "candidate provides internal "
                "corroboration of the same region."
            ),

            "experiment_family": (
                bayesian[
                    "experiment_family"
                ]
            ),

            "predicted_microgravity_"
            "spread_rate_mm_s": (
                bayesian_candidate[
                    "microgravity"
                ][
                    "gp_corrected_prediction_mm_s"
                ]
            ),

            "predicted_normal_gravity_"
            "spread_rate_mm_s": (
                bayesian_candidate[
                    "normal_gravity"
                ][
                    "gp_corrected_prediction_mm_s"
                ]
            ),

            "predicted_mg_to_ng_"
            "spread_ratio": (
                bayesian_candidate[
                    "predicted_mg_to_ng_spread_ratio"
                ]
            ),

            "matched_pair_joint_sd_log": (
                bayesian_candidate[
                    "matched_pair_joint_sd_log"
                ]
            ),

            "one_sd_ratio_uncertainty_factor": (
                bayesian_candidate[
                    "one_sd_ratio_uncertainty_factor"
                ]
            ),
        },

        "evidence_relationship": {
            "shared_canonical_evidence": True,

            "independent_validation": False,

            "external_validation": (
                "not_performed"
            ),

            "note": (
                "Coverage and Bayesian results "
                "are derived from the same frozen "
                "Figure 2.21 evidence base. Their "
                "agreement is internal convergence, "
                "not independent validation."
            ),
        },

        "decision_status": (
            "research_priority_candidate"
        ),

        "approval_status": (
            "not_approved"
        ),

        "production_ready": False,

        "scientific_guardrails": [
            (
                "The selected thickness is a "
                "research-priority candidate, "
                "not an approved experiment."
            ),

            (
                "The result is not an external "
                "validation of the GP model."
            ),

            "Coverage and Bayesian methods share the same frozen Figure 2.21 evidence base.",

            (
                "The Bayesian acquisition uses "
                "independent gravity-regime GP "
                "models in v0."
            ),

            (
                "Physics-baseline parameter "
                "uncertainty is not propagated "
                "into the v0 acquisition."
            ),

            (
                "Digitization uncertainty and "
                "experimental uncertainty remain "
                "distinct."
            ),

            "Posterior uncertainty is not externally calibrated.",

            (
                "No certification, operational "
                "safety approval, or cabin-fire "
                "probability claim is made."
            ),
        ],

        "required_before_experiment_approval": [
            (
                "Confirm practical PMMA sample "
                "availability near the selected "
                "thickness."
            ),

            (
                "Confirm experimental hardware "
                "and geometry constraints."
            ),

            (
                "Confirm atmosphere and flow "
                "configuration."
            ),

            (
                "Define replication strategy."
            ),

            (
                "Review measurement and "
                "digitization uncertainty."
            ),

            (
                "Perform scientific and "
                "safety review."
            ),
        ],

        "status": (
            "next_experiment_decision_frozen"
        ),
    }

    output_path.write_text(
        json.dumps(
            decision,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print()
    print(
        "FIRESENSE NEXT EXPERIMENT "
        "DECISION V0"
    )

    print(
        "--------------------------------"
    )

    print()
    print(
        "Coverage candidate:"
    )

    print(
        f"  {coverage_thickness:.6f} um"
    )

    print()
    print(
        "Bayesian candidate:"
    )

    print(
        f"  {bayesian_thickness:.6f} um"
    )

    print()
    print(
        "Absolute difference:"
    )

    print(
        f"  {absolute_difference:.6f} um"
    )

    print()
    print(
        "Relative difference:"
    )

    print(
        f"  "
        f"{relative_difference * 100.0:.4f}%"
    )

    print()
    print(
        "Within 1 percent:"
    )

    print(
        f"  {within_one_percent}"
    )

    print()
    print(
        "Selected research-priority "
        "candidate:"
    )

    print(
        f"  {bayesian_thickness:.6f} um"
    )

    print()
    print(
        "Decision status:"
    )

    print(
        "  RESEARCH PRIORITY CANDIDATE"
    )

    print(
        "  NOT APPROVED EXPERIMENT"
    )

    print()
    print(
        "External validation:"
    )

    print(
        "  NOT PERFORMED"
    )

    print()
    print(
        "Saved:"
    )

    print(
        f"  {output_path}"
    )


if __name__ == "__main__":
    main()