import json
import math
from pathlib import Path

import torch

from botorch.acquisition.analytic import (
    PosteriorStandardDeviation,
)
from botorch.fit import fit_gpytorch_mll
from botorch.models import SingleTaskGP
from botorch.models.transforms.outcome import (
    Standardize,
)
from gpytorch.mlls import (
    ExactMarginalLogLikelihood,
)

from app.core.paths import CURATED_DATA_DIR


torch.set_default_dtype(torch.double)


GROUPS = (
    "microgravity",
    "normal_gravity",
)


EXPECTED_COUNTS = {
    "microgravity": 4,
    "normal_gravity": 9,
}


GRID_SIZE = 1001


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


def load_jsonl(
    path: Path,
) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(
            f"Missing file: {path}"
        )

    rows = []

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
                rows.append(
                    json.loads(line)
                )
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSONL at line "
                    f"{line_number}: {exc}"
                ) from exc

    return rows


def tensor_float(
    value: torch.Tensor,
) -> float:
    return float(
        value.detach()
        .cpu()
        .item()
    )


def normalize_log_thickness(
    thickness_um: torch.Tensor,
    log_min: float,
    log_max: float,
) -> torch.Tensor:
    denominator = (
        log_max
        - log_min
    )

    if denominator <= 0:
        raise ValueError(
            "Invalid log-thickness domain."
        )

    return (
        torch.log10(thickness_um)
        - log_min
    ) / denominator


def fit_residual_gp(
    rows: list[dict],
    group_name: str,
    coefficient_k: float,
) -> dict:
    group_rows = sorted(
        [
            row
            for row in rows
            if (
                row["gravity_regime"]
                == group_name
            )
        ],
        key=lambda row: float(
            row["thickness_um"]
        ),
    )

    expected_count = (
        EXPECTED_COUNTS[group_name]
    )

    if len(group_rows) != expected_count:
        raise ValueError(
            f"{group_name}: expected "
            f"{expected_count} records, "
            f"found {len(group_rows)}."
        )

    thickness = torch.tensor(
        [
            float(row["thickness_um"])
            for row in group_rows
        ],
        dtype=torch.double,
    )

    observed = torch.tensor(
        [
            float(
                row["spread_rate_mm_s"]
            )
            for row in group_rows
        ],
        dtype=torch.double,
    )

    physics_prediction = (
        coefficient_k
        / thickness
    )

    log_residual = (
        torch.log(observed)
        - torch.log(
            physics_prediction
        )
    )

    log_min = tensor_float(
        torch.log10(
            thickness.min()
        )
    )

    log_max = tensor_float(
        torch.log10(
            thickness.max()
        )
    )

    train_x = (
        normalize_log_thickness(
            thickness,
            log_min,
            log_max,
        )
        .unsqueeze(-1)
    )

    train_y = (
        log_residual
        .unsqueeze(-1)
    )

    print(
        f"Fitting GP: {group_name}"
    )

    model = SingleTaskGP(
        train_X=train_x,
        train_Y=train_y,
        outcome_transform=(
            Standardize(m=1)
        ),
    )

    mll = (
        ExactMarginalLogLikelihood(
            model.likelihood,
            model,
        )
    )

    fit_gpytorch_mll(
        mll
    )

    model.eval()
    model.likelihood.eval()

    return {
        "model": model,
        "group_rows": group_rows,
        "thickness": thickness,
        "coefficient_k": coefficient_k,
        "log_min": log_min,
        "log_max": log_max,
    }


def evaluate_group(
    fit: dict,
    candidate_thickness: torch.Tensor,
) -> dict:
    normalized_x = (
        normalize_log_thickness(
            candidate_thickness,
            fit["log_min"],
            fit["log_max"],
        )
        .unsqueeze(-1)
    )

    acquisition = (
        PosteriorStandardDeviation(
            fit["model"]
        )
    )

    with torch.no_grad():
        posterior = (
            fit["model"].posterior(
                normalized_x
            )
        )

        posterior_mean = (
            posterior.mean
            .reshape(-1)
        )

        acquisition_x = (
            normalized_x
            .unsqueeze(-2)
        )

        posterior_sd = (
            acquisition(
                acquisition_x
            )
            .reshape(-1)
        )

    return {
        "normalized_x": (
            normalized_x.reshape(-1)
        ),
        "posterior_mean": (
            posterior_mean
        ),
        "posterior_sd": (
            posterior_sd
        ),
    }


def nearest_observation(
    thickness_values: torch.Tensor,
    candidate_um: float,
) -> dict:
    values = [
        float(value)
        for value in (
            thickness_values
            .detach()
            .cpu()
            .tolist()
        )
    ]

    nearest = min(
        values,
        key=lambda value: abs(
            math.log(
                value
                / candidate_um
            )
        ),
    )

    return {
        "thickness_um": nearest,
        "absolute_distance_um": abs(
            nearest
            - candidate_um
        ),
        "log_ratio_distance": abs(
            math.log(
                nearest
                / candidate_um
            )
        ),
    }


def main():
    curated_dir = (
        CURATED_DATA_DIR
        / "thin_sheet"
    )

    models_dir = (
        curated_dir
        / "models"
    )

    dataset_path = (
        curated_dir
        / "baseline_dataset_v0.jsonl"
    )

    manifest_path = (
        curated_dir
        / "baseline_dataset_v0_manifest.json"
    )

    physics_path = (
        models_dir
        / "physics_baseline_v0.json"
    )

    gp_artifact_path = (
        models_dir
        / "physics_informed_gp_v0.json"
    )

    rows = load_jsonl(
        dataset_path
    )

    manifest = load_json(
        manifest_path
    )

    physics_model = load_json(
        physics_path
    )

    gp_artifact = load_json(
        gp_artifact_path
    )

    if len(rows) != 13:
        raise ValueError(
            f"Expected 13 frozen records; "
            f"found {len(rows)}."
        )

    if (
        manifest.get("dataset_version")
        != "v0"
    ):
        raise ValueError(
            "Expected baseline dataset v0."
        )

    if (
        gp_artifact.get("status")
        != "physics_informed_gp_fitted"
    ):
        raise ValueError(
            "Physics-informed GP v0 "
            "artifact is not fitted."
        )

    fitted = {}

    for group_name in GROUPS:
        coefficient_k = float(
            physics_model[
                "groups"
            ][
                group_name
            ][
                "physics_inverse_baseline"
            ][
                "coefficient_k"
            ]
        )

        fitted[group_name] = (
            fit_residual_gp(
                rows=rows,
                group_name=group_name,
                coefficient_k=(
                    coefficient_k
                ),
            )
        )

    mg = fitted[
        "microgravity"
    ]

    ng = fitted[
        "normal_gravity"
    ]

    mg_min = tensor_float(
        mg["thickness"].min()
    )

    mg_max = tensor_float(
        mg["thickness"].max()
    )

    ng_min = tensor_float(
        ng["thickness"].min()
    )

    ng_max = tensor_float(
        ng["thickness"].max()
    )

    common_min = max(
        mg_min,
        ng_min,
    )

    common_max = min(
        mg_max,
        ng_max,
    )

    if common_min >= common_max:
        raise ValueError(
            "Gravity regimes do not have "
            "an overlapping thickness domain."
        )

    common_log_min = (
        math.log10(
            common_min
        )
    )

    common_log_max = (
        math.log10(
            common_max
        )
    )

    log_grid = torch.linspace(
        common_log_min,
        common_log_max,
        GRID_SIZE,
        dtype=torch.double,
    )

    thickness_grid = torch.pow(
        torch.tensor(
            10.0,
            dtype=torch.double,
        ),
        log_grid,
    )

    mg_eval = evaluate_group(
        mg,
        thickness_grid,
    )

    ng_eval = evaluate_group(
        ng,
        thickness_grid,
    )

    #
    # Independent-GP approximation:
    #
    # Var[
    #   log(V_mg) - log(V_ng)
    # ]
    #
    # =
    #
    # Var_mg + Var_ng
    #
    joint_sd = torch.sqrt(
        mg_eval[
            "posterior_sd"
        ].square()
        +
        ng_eval[
            "posterior_sd"
        ].square()
    )

    best_index = int(
        torch.argmax(
            joint_sd
        ).item()
    )

    candidate_um = (
        tensor_float(
            thickness_grid[
                best_index
            ]
        )
    )

    mg_sd = tensor_float(
        mg_eval[
            "posterior_sd"
        ][
            best_index
        ]
    )

    ng_sd = tensor_float(
        ng_eval[
            "posterior_sd"
        ][
            best_index
        ]
    )

    combined_sd = tensor_float(
        joint_sd[
            best_index
        ]
    )

    mg_mean = tensor_float(
        mg_eval[
            "posterior_mean"
        ][
            best_index
        ]
    )

    ng_mean = tensor_float(
        ng_eval[
            "posterior_mean"
        ][
            best_index
        ]
    )

    mg_physics_prediction = (
        mg["coefficient_k"]
        / candidate_um
    )

    ng_physics_prediction = (
        ng["coefficient_k"]
        / candidate_um
    )

    mg_corrected_prediction = (
        mg_physics_prediction
        * math.exp(
            mg_mean
        )
    )

    ng_corrected_prediction = (
        ng_physics_prediction
        * math.exp(
            ng_mean
        )
    )

    predicted_ratio = (
        mg_corrected_prediction
        / ng_corrected_prediction
    )

    ratio_uncertainty_factor = (
        math.exp(
            combined_sd
        )
    )

    acquisition_grid = []

    for index in range(
        GRID_SIZE
    ):
        acquisition_grid.append(
            {
                "thickness_um": (
                    tensor_float(
                        thickness_grid[
                            index
                        ]
                    )
                ),

                "microgravity_posterior_sd_log": (
                    tensor_float(
                        mg_eval[
                            "posterior_sd"
                        ][
                            index
                        ]
                    )
                ),

                "normal_gravity_posterior_sd_log": (
                    tensor_float(
                        ng_eval[
                            "posterior_sd"
                        ][
                            index
                        ]
                    )
                ),

                "matched_pair_joint_sd_log": (
                    tensor_float(
                        joint_sd[
                            index
                        ]
                    )
                ),
            }
        )

    result = {
        "candidate_id": (
            "NEXTEXP-BAYES-V0-001"
        ),

        "candidate_version": "v0",

        "source_id": (
            manifest["source_id"]
        ),

        "dataset_version": "v0",

        "canonical_evidence_figure": (
            "2.21"
        ),

        "recommendation_basis": (
            "bayesian_pure_exploration_"
            "matched_pair"
        ),

        "recommendation_status": (
            "bayesian_candidate_only"
        ),

        "approval_status": (
            "not_approved"
        ),

        "production_ready": False,

        "external_validation": (
            "not_performed"
        ),

        "experiment_family": {
            "material": "PMMA",
            "geometry_family": (
                "thin_sheet"
            ),
            "oxygen_percent": 21.0,
            "pressure_kpa": 101.325,
            "matched_variable": (
                "thickness_um"
            ),
            "gravity_regimes": [
                "microgravity",
                "normal_gravity",
            ],
        },

        "search_domain": {
            "basis": (
                "intersection_of_empirical_"
                "domains"
            ),

            "microgravity_domain_um": [
                mg_min,
                mg_max,
            ],

            "normal_gravity_domain_um": [
                ng_min,
                ng_max,
            ],

            "common_domain_um": [
                common_min,
                common_max,
            ],

            "grid_size": GRID_SIZE,

            "grid_spacing": (
                "uniform_in_log10_thickness"
            ),
        },

        "acquisition": {
            "library": "BoTorch",

            "individual_acquisition": (
                "PosteriorStandardDeviation"
            ),

            "matched_pair_objective": (
                "sqrt("
                "sigma_microgravity^2 + "
                "sigma_normal_gravity^2"
                ")"
            ),

            "interpretation": (
                "Posterior standard deviation "
                "of the log spread-rate "
                "difference under independent "
                "gravity-regime GP models."
            ),
        },

        "candidate": {
            "thickness_um": (
                candidate_um
            ),

            "microgravity": {
                "posterior_mean_log_residual": (
                    mg_mean
                ),

                "posterior_sd_log_residual": (
                    mg_sd
                ),

                "physics_prediction_mm_s": (
                    mg_physics_prediction
                ),

                "gp_corrected_prediction_mm_s": (
                    mg_corrected_prediction
                ),

                "nearest_existing_observation": (
                    nearest_observation(
                        mg["thickness"],
                        candidate_um,
                    )
                ),
            },

            "normal_gravity": {
                "posterior_mean_log_residual": (
                    ng_mean
                ),

                "posterior_sd_log_residual": (
                    ng_sd
                ),

                "physics_prediction_mm_s": (
                    ng_physics_prediction
                ),

                "gp_corrected_prediction_mm_s": (
                    ng_corrected_prediction
                ),

                "nearest_existing_observation": (
                    nearest_observation(
                        ng["thickness"],
                        candidate_um,
                    )
                ),
            },

            "matched_pair_joint_sd_log": (
                combined_sd
            ),

            "predicted_mg_to_ng_spread_ratio": (
                predicted_ratio
            ),

            "one_sd_ratio_uncertainty_factor": (
                ratio_uncertainty_factor
            ),
        },

        "scientific_guardrails": [
            (
                "This is a Bayesian "
                "pure-exploration candidate, "
                "not an approved experiment."
            ),

            (
                "Only frozen Figure 2.21 "
                "experimental observations "
                "are used for model fitting."
            ),

            (
                "Figure 2.22 observations and "
                "theoretical curves are excluded "
                "from training."
            ),

            (
                "The two gravity-regime GPs are "
                "treated as independent in v0."
            ),

            (
                "Physics-baseline coefficient "
                "uncertainty is not propagated "
                "in this v0 acquisition."
            ),

            (
                "Digitization uncertainty is "
                "kept distinct and is not treated "
                "as complete experimental noise."
            ),

            (
                "Posterior uncertainty is not "
                "externally calibrated."
            ),

            (
                "Search is restricted to the "
                "intersection of observed "
                "thickness domains."
            ),

            (
                "No certification, safety "
                "approval, or cabin-fire "
                "probability claim is made."
            ),
        ],

        "acquisition_grid": (
            acquisition_grid
        ),

        "status": (
            "bayesian_next_experiment_"
            "candidate_generated"
        ),
    }

    output_path = (
        models_dir
        / "bayesian_next_experiment_"
        "candidate_v0.json"
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
        "FIRESENSE BAYESIAN NEXT "
        "EXPERIMENT CANDIDATE V0"
    )

    print(
        "--------------------------------"
    )

    print()
    print(
        "Common domain:"
    )

    print(
        f"  {common_min:.3f} "
        f"→ {common_max:.3f} um"
    )

    print()
    print(
        "Recommended matched thickness:"
    )

    print(
        f"  {candidate_um:.3f} um"
    )

    print()
    print(
        "Posterior uncertainty:"
    )

    print(
        f"  Microgravity : "
        f"{mg_sd:.6f}"
    )

    print(
        f"  Normal       : "
        f"{ng_sd:.6f}"
    )

    print(
        f"  Joint        : "
        f"{combined_sd:.6f}"
    )

    print()
    print(
        "Predicted spread rate:"
    )

    print(
        f"  Microgravity : "
        f"{mg_corrected_prediction:.6f} "
        f"mm/s"
    )

    print(
        f"  Normal       : "
        f"{ng_corrected_prediction:.6f} "
        f"mm/s"
    )

    print(
        f"  MG / Normal  : "
        f"{predicted_ratio:.6f}"
    )

    print()
    print(
        "1-SD uncertainty factor "
        "for spread-rate ratio:"
    )

    print(
        f"  x/{ratio_uncertainty_factor:.4f}"
    )

    print()
    print(
        "Recommendation status:"
    )

    print(
        "  BAYESIAN CANDIDATE ONLY"
    )

    print(
        "  NOT EXPERIMENT APPROVAL"
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