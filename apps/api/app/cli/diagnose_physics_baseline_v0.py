import json
import math
from pathlib import Path

import numpy as np

from app.core.paths import CURATED_DATA_DIR


GROUPS = (
    "microgravity",
    "normal_gravity",
)


EXPECTED_COUNTS = {
    "microgravity": 4,
    "normal_gravity": 9,
}


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
                    json.loads(
                        line
                    )
                )

            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON on line "
                    f"{line_number}: {exc}"
                ) from exc

    return rows


def fit_inverse_k(
    thickness: np.ndarray,
    spread_rate: np.ndarray,
) -> float:

    log_k = np.mean(
        np.log(
            spread_rate
        )
        + np.log(
            thickness
        )
    )

    return float(
        np.exp(
            log_k
        )
    )


def fit_power_law(
    thickness: np.ndarray,
    spread_rate: np.ndarray,
) -> tuple[float, float]:

    log_x = np.log(
        thickness
    )

    log_y = np.log(
        spread_rate
    )

    slope, intercept = np.polyfit(
        log_x,
        log_y,
        1,
    )

    coefficient = float(
        np.exp(
            intercept
        )
    )

    exponent = float(
        slope
    )

    return (
        coefficient,
        exponent,
    )


def metrics(
    observed: np.ndarray,
    predicted: np.ndarray,
) -> dict:

    log_residual = np.log(
        observed
        / predicted
    )

    rmse_log = float(
        np.sqrt(
            np.mean(
                log_residual ** 2
            )
        )
    )

    mae_log = float(
        np.mean(
            np.abs(
                log_residual
            )
        )
    )

    mape = float(
        np.mean(
            np.abs(
                predicted
                - observed
            )
            / observed
        )
        * 100.0
    )

    return {
        "rmse_log": (
            rmse_log
        ),

        "mae_log": (
            mae_log
        ),

        "mape_percent": (
            mape
        ),
    }


def leave_one_out_inverse(
    thickness: np.ndarray,
    spread_rate: np.ndarray,
) -> dict:

    predictions = []

    fitted_k_values = []

    for test_index in range(
        len(thickness)
    ):

        train_mask = np.ones(
            len(thickness),
            dtype=bool,
        )

        train_mask[
            test_index
        ] = False

        train_x = (
            thickness[
                train_mask
            ]
        )

        train_y = (
            spread_rate[
                train_mask
            ]
        )

        k = fit_inverse_k(
            train_x,
            train_y,
        )

        prediction = (
            k
            / thickness[
                test_index
            ]
        )

        fitted_k_values.append(
            float(
                k
            )
        )

        predictions.append(
            float(
                prediction
            )
        )

    predictions = np.array(
        predictions,
        dtype=float,
    )

    return {
        "predictions": (
            predictions
        ),

        "k_values": (
            fitted_k_values
        ),

        "metrics": metrics(
            spread_rate,
            predictions,
        ),
    }


def leave_one_out_power_law(
    thickness: np.ndarray,
    spread_rate: np.ndarray,
) -> dict:

    predictions = []

    coefficients = []

    exponents = []

    for test_index in range(
        len(thickness)
    ):

        train_mask = np.ones(
            len(thickness),
            dtype=bool,
        )

        train_mask[
            test_index
        ] = False

        train_x = (
            thickness[
                train_mask
            ]
        )

        train_y = (
            spread_rate[
                train_mask
            ]
        )

        if len(
            train_x
        ) < 2:

            raise ValueError(
                "Not enough rows for "
                "power-law LOOCV."
            )

        coefficient, exponent = (
            fit_power_law(
                train_x,
                train_y,
            )
        )

        prediction = (
            coefficient
            * thickness[
                test_index
            ]
            ** exponent
        )

        coefficients.append(
            float(
                coefficient
            )
        )

        exponents.append(
            float(
                exponent
            )
        )

        predictions.append(
            float(
                prediction
            )
        )

    predictions = np.array(
        predictions,
        dtype=float,
    )

    return {
        "predictions": (
            predictions
        ),

        "coefficients": (
            coefficients
        ),

        "exponents": (
            exponents
        ),

        "metrics": metrics(
            spread_rate,
            predictions,
        ),
    }


def main():

    curated_dir = (
        CURATED_DATA_DIR
        / "thin_sheet"
    )

    dataset_path = (
        curated_dir
        / "baseline_dataset_v0.jsonl"
    )

    model_path = (
        curated_dir
        / "models"
        / "physics_baseline_v0.json"
    )

    output_dir = (
        curated_dir
        / "models"
    )

    dataset = load_jsonl(
        dataset_path
    )

    model = load_json(
        model_path
    )

    if (
        model.get(
            "status"
        )
        != "exploratory_physics_baseline_fitted"
    ):

        raise ValueError(
            "Physics baseline v0 "
            "has not been fitted."
        )

    all_residual_rows = []

    group_diagnostics = {}

    for group_name in GROUPS:

        rows = sorted(
            [
                row
                for row in dataset
                if (
                    row[
                        "gravity_regime"
                    ]
                    == group_name
                )
            ],
            key=lambda row: (
                row[
                    "thickness_um"
                ]
            ),
        )

        if (
            len(rows)
            != EXPECTED_COUNTS[
                group_name
            ]
        ):

            raise ValueError(
                f"{group_name}: "
                "unexpected row count."
            )

        thickness = np.array(
            [
                float(
                    row[
                        "thickness_um"
                    ]
                )
                for row in rows
            ],
            dtype=float,
        )

        observed = np.array(
            [
                float(
                    row[
                        "spread_rate_mm_s"
                    ]
                )
                for row in rows
            ],
            dtype=float,
        )

        full_model = (
            model[
                "groups"
            ][
                group_name
            ]
        )

        fitted_k = float(
            full_model[
                "physics_inverse_baseline"
            ][
                "coefficient_k"
            ]
        )

        full_prediction = (
            fitted_k
            / thickness
        )

        loo_inverse = (
            leave_one_out_inverse(
                thickness,
                observed,
            )
        )

        loo_power = (
            leave_one_out_power_law(
                thickness,
                observed,
            )
        )

        log_residuals = np.log(
            observed
            / full_prediction
        )

        abs_log_residuals = np.abs(
            log_residuals
        )

        worst_index = int(
            np.argmax(
                abs_log_residuals
            )
        )

        residual_log_sd = float(
            np.std(
                log_residuals,
                ddof=1,
            )
        )

        descriptive_factor = float(
            math.exp(
                residual_log_sd
            )
        )

        domain_min = float(
            thickness.min()
        )

        domain_max = float(
            thickness.max()
        )

        group_diagnostics[
            group_name
        ] = {
            "record_count": (
                len(rows)
            ),

            "empirical_domain": {
                "thickness_um_min": (
                    domain_min
                ),

                "thickness_um_max": (
                    domain_max
                ),

                "material": "PMMA",

                "geometry": (
                    "thin_sheet"
                ),

                "oxygen_fraction": (
                    0.21
                ),

                "pressure_kpa": (
                    101.325
                ),

                "gravity_regime": (
                    group_name
                ),
            },

            "full_fit_inverse": {
                "coefficient_k": (
                    fitted_k
                ),

                "metrics": metrics(
                    observed,
                    full_prediction,
                ),
            },

            "leave_one_out_inverse": {
                "metrics": (
                    loo_inverse[
                        "metrics"
                    ]
                ),

                "k_min": float(
                    min(
                        loo_inverse[
                            "k_values"
                        ]
                    )
                ),

                "k_max": float(
                    max(
                        loo_inverse[
                            "k_values"
                        ]
                    )
                ),
            },

            "leave_one_out_free_power_law": {
                "role": (
                    "diagnostic_only"
                ),

                "metrics": (
                    loo_power[
                        "metrics"
                    ]
                ),

                "exponent_min": float(
                    min(
                        loo_power[
                            "exponents"
                        ]
                    )
                ),

                "exponent_max": float(
                    max(
                        loo_power[
                            "exponents"
                        ]
                    )
                ),
            },

            "residual_description": {
                "log_residual_sd": (
                    residual_log_sd
                ),

                "multiplicative_residual_factor": (
                    descriptive_factor
                ),

                "important_note": (
                    "This is descriptive "
                    "training residual spread, "
                    "not a calibrated prediction "
                    "interval."
                ),
            },

            "worst_training_residual": {
                "record_id": (
                    rows[
                        worst_index
                    ][
                        "record_id"
                    ]
                ),

                "thickness_um": float(
                    thickness[
                        worst_index
                    ]
                ),

                "observed_mm_s": float(
                    observed[
                        worst_index
                    ]
                ),

                "predicted_mm_s": float(
                    full_prediction[
                        worst_index
                    ]
                ),

                "absolute_log_residual": float(
                    abs_log_residuals[
                        worst_index
                    ]
                ),
            },
        }

        for index, row in enumerate(
            rows
        ):

            all_residual_rows.append(
                {
                    "record_id": (
                        row[
                            "record_id"
                        ]
                    ),

                    "gravity_regime": (
                        group_name
                    ),

                    "thickness_um": float(
                        thickness[
                            index
                        ]
                    ),

                    "observed_mm_s": float(
                        observed[
                            index
                        ]
                    ),

                    "full_fit_inverse_prediction_mm_s": float(
                        full_prediction[
                            index
                        ]
                    ),

                    "full_fit_log_residual": float(
                        log_residuals[
                            index
                        ]
                    ),

                    "loo_inverse_prediction_mm_s": float(
                        loo_inverse[
                            "predictions"
                        ][
                            index
                        ]
                    ),

                    "loo_power_law_prediction_mm_s": float(
                        loo_power[
                            "predictions"
                        ][
                            index
                        ]
                    ),

                    "digitization_uncertainty_mm_s": float(
                        row[
                            "digitization_uncertainty_mm_s"
                        ]
                    ),
                }
            )

    abstention_policy = {
        "policy_version": "v0",

        "decision": (
            "interpolation_only"
        ),

        "predict_only_when_all_true": [
            (
                "material == PMMA"
            ),

            (
                "geometry == thin_sheet"
            ),

            (
                "oxygen_fraction == 0.21"
            ),

            (
                "pressure_kpa == 101.325"
            ),

            (
                "gravity_regime is exactly "
                "microgravity or normal_gravity"
            ),

            (
                "thickness_um is inside the "
                "observed range for the selected "
                "gravity group"
            ),
        ],

        "abstain_when_any_true": [
            (
                "thickness is outside the "
                "empirical group range"
            ),

            (
                "material or geometry differs"
            ),

            (
                "oxygen fraction differs"
            ),

            (
                "pressure differs"
            ),

            (
                "gravity regime is unknown or "
                "intermediate"
            ),

            (
                "requested output is not "
                "flame spread rate"
            ),
        ],

        "important_note": (
            "This abstention policy is a "
            "scientific scope guardrail, not "
            "a calibrated uncertainty-based "
            "selective prediction threshold."
        ),
    }

    result = {
        "diagnostic_name": (
            "FireSense Physics Baseline "
            "v0 Diagnostics"
        ),

        "model_version": "v0",

        "dataset_version": "v0",

        "groups": (
            group_diagnostics
        ),

        "abstention_policy": (
            abstention_policy
        ),

        "validation_status": (
            "internal_leave_one_out_"
            "sensitivity_only"
        ),

        "external_validation": (
            "not_performed"
        ),

        "important_limitations": [
            (
                "Leave-one-out evaluation "
                "is not independent external "
                "validation because all rows "
                "come from the same curated "
                "Figure 2.21 evidence source."
            ),

            (
                "Microgravity contains only "
                "four observations."
            ),

            (
                "Residual spread is descriptive "
                "and not a calibrated prediction "
                "interval."
            ),

            (
                "No extrapolation is approved."
            ),
        ],

        "status": (
            "baseline_diagnostics_complete"
        ),
    }

    diagnostics_path = (
        output_dir
        / "physics_baseline_v0_diagnostics.json"
    )

    diagnostics_path.write_text(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    residuals_path = (
        output_dir
        / "physics_baseline_v0_residuals.jsonl"
    )

    with residuals_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        for row in all_residual_rows:

            file.write(
                json.dumps(
                    row,
                    ensure_ascii=False,
                )
            )

            file.write(
                "\n"
            )

    policy_path = (
        output_dir
        / "physics_baseline_v0_abstention_policy.json"
    )

    policy_path.write_text(
        json.dumps(
            abstention_policy,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print()
    print(
        "FIRESENSE BASELINE DIAGNOSTICS V0"
    )

    print(
        "---------------------------------"
    )

    for group_name in GROUPS:

        group = (
            group_diagnostics[
                group_name
            ]
        )

        print()
        print(
            group_name.upper()
        )

        print(
            "-" * len(
                group_name
            )
        )

        print(
            "Domain thickness : "
            f"{group['empirical_domain']['thickness_um_min']:.3f}"
            " - "
            f"{group['empirical_domain']['thickness_um_max']:.3f}"
            " um"
        )

        print(
            "LOOCV inverse MAPE: "
            f"{group['leave_one_out_inverse']['metrics']['mape_percent']:.2f}%"
        )

        print(
            "LOOCV inverse RMSE log: "
            f"{group['leave_one_out_inverse']['metrics']['rmse_log']:.4f}"
        )

        print(
            "LOOCV K range    : "
            f"{group['leave_one_out_inverse']['k_min']:.3f}"
            " - "
            f"{group['leave_one_out_inverse']['k_max']:.3f}"
        )

        print(
            "LOOCV power MAPE : "
            f"{group['leave_one_out_free_power_law']['metrics']['mape_percent']:.2f}%"
        )

        print(
            "LOOCV exponent   : "
            f"{group['leave_one_out_free_power_law']['exponent_min']:.3f}"
            " - "
            f"{group['leave_one_out_free_power_law']['exponent_max']:.3f}"
        )

        print(
            "Worst residual   : "
            f"{group['worst_training_residual']['record_id']}"
        )

        print(
            "Residual factor  : x/"
            f"{group['residual_description']['multiplicative_residual_factor']:.3f}"
        )

    print()
    print(
        "ABSTENTION POLICY"
    )

    print(
        "-----------------"
    )

    print(
        "Interpolation inside observed "
        "domain only."
    )

    print(
        "Outside supported conditions:"
    )

    print(
        "  ABSTAIN"
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
        "STATUS:"
    )

    print(
        "  baseline_diagnostics_complete"
    )

    print()
    print(
        "Saved:"
    )

    print(
        f"  {diagnostics_path}"
    )

    print(
        f"  {residuals_path}"
    )

    print(
        f"  {policy_path}"
    )


if __name__ == "__main__":
    main()