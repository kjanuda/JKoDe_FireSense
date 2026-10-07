import json
import math
from pathlib import Path

import torch

from botorch.fit import fit_gpytorch_mll
from botorch.models import SingleTaskGP
from botorch.models.transforms.outcome import Standardize
from gpytorch.mlls import ExactMarginalLogLikelihood

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


def load_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(
            f"Missing file: {path}"
        )

    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


def load_jsonl(path: Path) -> list[dict]:
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
                    f"Invalid JSONL line "
                    f"{line_number}: {exc}"
                ) from exc

    return rows


def normalize_log_thickness(
    thickness_um: torch.Tensor,
    log_min: float,
    log_max: float,
) -> torch.Tensor:
    log_x = torch.log10(
        thickness_um
    )

    denominator = (
        log_max
        - log_min
    )

    if denominator <= 0:
        raise ValueError(
            "Invalid thickness domain."
        )

    return (
        log_x
        - log_min
    ) / denominator


def denormalize_log_thickness(
    normalized_x: torch.Tensor,
    log_min: float,
    log_max: float,
) -> torch.Tensor:
    log_x = (
        log_min
        + normalized_x
        * (
            log_max
            - log_min
        )
    )

    return torch.pow(
        10.0,
        log_x,
    )


def tensor_to_float(
    value: torch.Tensor,
) -> float:
    return float(
        value.detach()
        .cpu()
        .item()
    )


def named_parameter_snapshot(
    model: SingleTaskGP,
) -> dict:
    result = {}

    for name, parameter in (
        model.named_parameters()
    ):
        detached = (
            parameter.detach()
            .cpu()
        )

        if detached.numel() == 1:
            result[name] = float(
                detached.item()
            )
        else:
            result[name] = (
                detached.tolist()
            )

    return result


def main():
    curated_dir = (
        CURATED_DATA_DIR
        / "thin_sheet"
    )

    dataset_path = (
        curated_dir
        / "baseline_dataset_v0.jsonl"
    )

    manifest_path = (
        curated_dir
        / "baseline_dataset_v0_manifest.json"
    )

    physics_model_path = (
        curated_dir
        / "models"
        / "physics_baseline_v0.json"
    )

    output_dir = (
        curated_dir
        / "models"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    rows = load_jsonl(
        dataset_path
    )

    manifest = load_json(
        manifest_path
    )

    physics_model = load_json(
        physics_model_path
    )

    if len(rows) != 13:
        raise ValueError(
            f"Expected 13 baseline rows, "
            f"found {len(rows)}."
        )

    if (
        manifest.get(
            "dataset_version"
        )
        != "v0"
    ):
        raise ValueError(
            "Expected baseline dataset v0."
        )

    if (
        physics_model.get(
            "status"
        )
        !=
        "exploratory_physics_baseline_fitted"
    ):
        raise ValueError(
            "Physics baseline v0 is not "
            "in fitted state."
        )

    result = {
        "model_name": (
            "FireSense Physics-Informed "
            "Residual GP v0"
        ),

        "model_version": "v0",

        "dataset_version": "v0",

        "source_id": (
            manifest[
                "source_id"
            ]
        ),

        "canonical_evidence_figure": (
            "2.21"
        ),

        "architecture": {
            "physics_baseline": (
                "V = K / tau"
            ),

            "gp_target": (
                "ln(V_observed) "
                "- ln(V_physics)"
            ),

            "gp_input": (
                "normalized log10(thickness_um)"
            ),

            "group_strategy": (
                "separate GP per "
                "gravity regime"
            ),

            "likelihood": (
                "learned homoskedastic "
                "Gaussian noise"
            ),

            "outcome_transform": (
                "Standardize(m=1)"
            ),
        },

        "groups": {},

        "scientific_guardrails": [
            (
                "Only frozen Figure 2.21 "
                "experimental evidence is used."
            ),
            (
                "Figure 2.22 data are not used "
                "for GP fitting."
            ),
            (
                "Theoretical curves are not "
                "training observations."
            ),
            (
                "Digitization uncertainty is "
                "not supplied as fixed GP noise "
                "because it is not the complete "
                "experimental uncertainty."
            ),
            (
                "Posterior standard deviation "
                "is model uncertainty under "
                "this GP specification; it is "
                "not yet externally calibrated."
            ),
            (
                "Search is restricted to each "
                "gravity group's empirical "
                "thickness domain."
            ),
            (
                "No cross-study validation "
                "claim is made."
            ),
        ],

        "external_validation": (
            "not_performed"
        ),

        "production_ready": False,

        "status": (
            "physics_informed_gp_fitted"
        ),
    }

    for group_name in GROUPS:
        group_rows = sorted(
            [
                row
                for row in rows
                if (
                    row[
                        "gravity_regime"
                    ]
                    == group_name
                )
            ],
            key=lambda row: float(
                row[
                    "thickness_um"
                ]
            ),
        )

        expected_count = (
            EXPECTED_COUNTS[
                group_name
            ]
        )

        if (
            len(group_rows)
            != expected_count
        ):
            raise ValueError(
                f"{group_name}: expected "
                f"{expected_count} rows, "
                f"found {len(group_rows)}."
            )

        thickness = torch.tensor(
            [
                float(
                    row[
                        "thickness_um"
                    ]
                )
                for row in group_rows
            ],
            dtype=torch.double,
        )

        observed = torch.tensor(
            [
                float(
                    row[
                        "spread_rate_mm_s"
                    ]
                )
                for row in group_rows
            ],
            dtype=torch.double,
        )

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

        physics_prediction = (
            coefficient_k
            / thickness
        )

        residual = (
            torch.log(observed)
            - torch.log(
                physics_prediction
            )
        )

        log_min = tensor_to_float(
            torch.log10(
                thickness.min()
            )
        )

        log_max = tensor_to_float(
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
            residual.unsqueeze(-1)
        )

        print()
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

        with torch.no_grad():
            train_posterior = (
                model.posterior(
                    train_x
                )
            )

            train_mean = (
                train_posterior.mean
                .squeeze(-1)
            )

            train_variance = (
                train_posterior.variance
                .squeeze(-1)
            )

            train_sd = torch.sqrt(
                train_variance.clamp_min(
                    0.0
                )
            )

        residual_rmse = (
            torch.sqrt(
                torch.mean(
                    (
                        residual
                        - train_mean
                    )
                    ** 2
                )
            )
        )

        grid_x = torch.linspace(
            0.0,
            1.0,
            501,
            dtype=torch.double,
        ).unsqueeze(-1)

        with torch.no_grad():
            posterior = (
                model.posterior(
                    grid_x
                )
            )

            posterior_mean = (
                posterior.mean
                .squeeze(-1)
            )

            posterior_variance = (
                posterior.variance
                .squeeze(-1)
            )

            posterior_sd = torch.sqrt(
                posterior_variance
                .clamp_min(
                    0.0
                )
            )

        grid_thickness = (
            denormalize_log_thickness(
                grid_x.squeeze(-1),
                log_min,
                log_max,
            )
        )

        peak_index = int(
            torch.argmax(
                posterior_sd
            ).item()
        )

        peak_thickness = (
            tensor_to_float(
                grid_thickness[
                    peak_index
                ]
            )
        )

        peak_residual_mean = (
            tensor_to_float(
                posterior_mean[
                    peak_index
                ]
            )
        )

        peak_residual_sd = (
            tensor_to_float(
                posterior_sd[
                    peak_index
                ]
            )
        )

        peak_physics_prediction = (
            coefficient_k
            / peak_thickness
        )

        peak_gp_corrected_prediction = (
            peak_physics_prediction
            * math.exp(
                peak_residual_mean
            )
        )

        peak_multiplicative_factor = (
            math.exp(
                peak_residual_sd
            )
        )

        training_rows = []

        for index, row in enumerate(
            group_rows
        ):
            training_rows.append(
                {
                    "record_id": (
                        row[
                            "record_id"
                        ]
                    ),

                    "thickness_um": (
                        tensor_to_float(
                            thickness[
                                index
                            ]
                        )
                    ),

                    "normalized_log10_thickness": (
                        tensor_to_float(
                            train_x[
                                index,
                                0,
                            ]
                        )
                    ),

                    "observed_spread_rate_mm_s": (
                        tensor_to_float(
                            observed[
                                index
                            ]
                        )
                    ),

                    "physics_prediction_mm_s": (
                        tensor_to_float(
                            physics_prediction[
                                index
                            ]
                        )
                    ),

                    "log_residual_target": (
                        tensor_to_float(
                            residual[
                                index
                            ]
                        )
                    ),

                    "posterior_mean_log_residual": (
                        tensor_to_float(
                            train_mean[
                                index
                            ]
                        )
                    ),

                    "posterior_sd_log_residual": (
                        tensor_to_float(
                            train_sd[
                                index
                            ]
                        )
                    ),
                }
            )

        grid_output = []

        for index in range(
            len(grid_thickness)
        ):
            thickness_value = (
                tensor_to_float(
                    grid_thickness[
                        index
                    ]
                )
            )

            mean_value = (
                tensor_to_float(
                    posterior_mean[
                        index
                    ]
                )
            )

            sd_value = (
                tensor_to_float(
                    posterior_sd[
                        index
                    ]
                )
            )

            physics_value = (
                coefficient_k
                / thickness_value
            )

            corrected_value = (
                physics_value
                * math.exp(
                    mean_value
                )
            )

            grid_output.append(
                {
                    "thickness_um": (
                        thickness_value
                    ),

                    "normalized_x": (
                        tensor_to_float(
                            grid_x[
                                index,
                                0,
                            ]
                        )
                    ),

                    "posterior_mean_log_residual": (
                        mean_value
                    ),

                    "posterior_sd_log_residual": (
                        sd_value
                    ),

                    "physics_prediction_mm_s": (
                        physics_value
                    ),

                    "gp_corrected_prediction_mm_s": (
                        corrected_value
                    ),

                    "multiplicative_uncertainty_factor": (
                        math.exp(
                            sd_value
                        )
                    ),
                }
            )

        result[
            "groups"
        ][
            group_name
        ] = {
            "record_count": (
                len(group_rows)
            ),

            "physics_coefficient_k": (
                coefficient_k
            ),

            "domain": {
                "thickness_um_min": (
                    tensor_to_float(
                        thickness.min()
                    )
                ),

                "thickness_um_max": (
                    tensor_to_float(
                        thickness.max()
                    )
                ),

                "log10_thickness_min": (
                    log_min
                ),

                "log10_thickness_max": (
                    log_max
                ),
            },

            "training_fit": {
                "residual_rmse_log_space": (
                    tensor_to_float(
                        residual_rmse
                    )
                ),

                "role": (
                    "descriptive_only"
                ),
            },

            "gp_parameters_raw": (
                named_parameter_snapshot(
                    model
                )
            ),

            "training_rows": (
                training_rows
            ),

            "uncertainty_peak": {
                "thickness_um": (
                    peak_thickness
                ),

                "posterior_mean_log_residual": (
                    peak_residual_mean
                ),

                "posterior_sd_log_residual": (
                    peak_residual_sd
                ),

                "multiplicative_uncertainty_factor": (
                    peak_multiplicative_factor
                ),

                "physics_prediction_mm_s": (
                    peak_physics_prediction
                ),

                "gp_corrected_prediction_mm_s": (
                    peak_gp_corrected_prediction
                ),

                "status": (
                    "posterior_uncertainty_peak_"
                    "inside_empirical_domain"
                ),

                "important_note": (
                    "This is not yet the final "
                    "next-experiment recommendation."
                ),
            },

            "posterior_grid": (
                grid_output
            ),
        }

    output_path = (
        output_dir
        / "physics_informed_gp_v0.json"
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
        "FIRESENSE PHYSICS-INFORMED GP V0"
    )

    print(
        "--------------------------------"
    )

    for group_name in GROUPS:
        group = (
            result[
                "groups"
            ][
                group_name
            ]
        )

        peak = (
            group[
                "uncertainty_peak"
            ]
        )

        print()
        print(
            group_name.upper()
        )

        print(
            "-" * len(group_name)
        )

        print(
            f"Records            : "
            f"{group['record_count']}"
        )

        print(
            "Residual RMSE log  : "
            f"{group['training_fit']['residual_rmse_log_space']:.6f}"
        )

        print(
            "Uncertainty peak   : "
            f"{peak['thickness_um']:.3f} um"
        )

        print(
            "Posterior SD log   : "
            f"{peak['posterior_sd_log_residual']:.6f}"
        )

        print(
            "Uncertainty factor : x/"
            f"{peak['multiplicative_uncertainty_factor']:.4f}"
        )

        print(
            "GP corrected V     : "
            f"{peak['gp_corrected_prediction_mm_s']:.6f} mm/s"
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
        "Final next experiment:"
    )

    print(
        "  NOT YET SELECTED"
    )

    print()
    print(
        "STATUS:"
    )

    print(
        "  physics_informed_gp_fitted"
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