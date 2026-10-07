import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from app.core.paths import (
    CURATED_DATA_DIR,
    FIGURES_DATA_DIR,
)


SOURCE_ID = "SRC-NASA-20210011385"

DATASET_VERSION = "v0"

SOURCE_THEORY_COEFFICIENT = 223.0

EXPECTED_COUNTS = {
    "microgravity": 4,
    "normal_gravity": 9,
}


def load_jsonl(
    path: Path,
) -> list[dict]:

    if not path.exists():
        raise FileNotFoundError(
            f"Missing dataset: {path}"
        )

    rows = []

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        for line_number, line in enumerate(
            file,
            start=1,
        ):

            line = line.strip()

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
                    f"Invalid JSONL at "
                    f"line {line_number}: "
                    f"{exc}"
                ) from exc

    return rows


def fit_inverse_model(
    thickness: np.ndarray,
    spread_rate: np.ndarray,
) -> dict:

    # Physics-inspired model:
    #
    # V = K / tau
    #
    # Fit in log space:
    #
    # log(V) = log(K) - log(tau)
    #
    # The exponent is fixed at -1.
    #
    # Using log space prevents the
    # largest spread rates from
    # dominating solely because of scale.

    log_k = np.mean(
        np.log(spread_rate)
        + np.log(thickness)
    )

    k = float(
        np.exp(
            log_k
        )
    )

    predicted = (
        k
        / thickness
    )

    return {
        "coefficient_k": k,
        "exponent": -1.0,
        "predicted": predicted,
    }


def fit_free_power_law(
    thickness: np.ndarray,
    spread_rate: np.ndarray,
) -> dict:

    # Diagnostic model only:
    #
    # V = A * tau^b
    #
    # b is allowed to move away
    # from the theoretical -1 value.

    x = np.log(
        thickness
    )

    y = np.log(
        spread_rate
    )

    slope, intercept = np.polyfit(
        x,
        y,
        1,
    )

    exponent = float(
        slope
    )

    coefficient_a = float(
        np.exp(
            intercept
        )
    )

    predicted = (
        coefficient_a
        * np.power(
            thickness,
            exponent,
        )
    )

    return {
        "coefficient_a": (
            coefficient_a
        ),
        "exponent": (
            exponent
        ),
        "predicted": (
            predicted
        ),
    }


def calculate_metrics(
    observed: np.ndarray,
    predicted: np.ndarray,
) -> dict:

    log_observed = np.log(
        observed
    )

    log_predicted = np.log(
        predicted
    )

    residuals = (
        log_observed
        - log_predicted
    )

    rmse_log = float(
        np.sqrt(
            np.mean(
                residuals ** 2
            )
        )
    )

    mae_log = float(
        np.mean(
            np.abs(
                residuals
            )
        )
    )

    mape = float(
        np.mean(
            np.abs(
                (
                    predicted
                    - observed
                )
                / observed
            )
        )
        * 100.0
    )

    ss_res = float(
        np.sum(
            residuals ** 2
        )
    )

    centered = (
        log_observed
        - np.mean(
            log_observed
        )
    )

    ss_total = float(
        np.sum(
            centered ** 2
        )
    )

    if ss_total > 0:

        r2_log = float(
            1.0
            - ss_res
            / ss_total
        )

    else:

        r2_log = None

    residual_log_sd = float(
        np.std(
            residuals,
            ddof=1,
        )
    ) if len(
        residuals
    ) > 1 else None

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

        "r2_log_space": (
            r2_log
        ),

        "residual_log_sd": (
            residual_log_sd
        ),
    }


def make_prediction_rows(
    group_name: str,
    rows: list[dict],
    inverse_prediction: np.ndarray,
    free_prediction: np.ndarray,
    theory_prediction: np.ndarray,
) -> list[dict]:

    result = []

    ordered_rows = sorted(
        rows,
        key=lambda row: (
            row["thickness_um"]
        ),
    )

    for (
        row,
        inverse_value,
        free_value,
        theory_value,
    ) in zip(
        ordered_rows,
        inverse_prediction,
        free_prediction,
        theory_prediction,
    ):

        observed = float(
            row[
                "spread_rate_mm_s"
            ]
        )

        result.append(
            {
                "record_id": (
                    row["record_id"]
                ),

                "gravity_regime": (
                    group_name
                ),

                "thickness_um": float(
                    row[
                        "thickness_um"
                    ]
                ),

                "observed_spread_rate_mm_s": (
                    observed
                ),

                "digitization_uncertainty_mm_s": (
                    float(
                        row[
                            "digitization_uncertainty_mm_s"
                        ]
                    )
                ),

                "source_theory_223_over_tau_mm_s": (
                    float(
                        theory_value
                    )
                ),

                "fitted_inverse_prediction_mm_s": (
                    float(
                        inverse_value
                    )
                ),

                "free_power_law_prediction_mm_s": (
                    float(
                        free_value
                    )
                ),

                "inverse_percent_error": (
                    float(
                        abs(
                            inverse_value
                            - observed
                        )
                        / observed
                        * 100.0
                    )
                ),

                "free_power_law_percent_error": (
                    float(
                        abs(
                            free_value
                            - observed
                        )
                        / observed
                        * 100.0
                    )
                ),
            }
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

    model_dir = (
        curated_dir
        / "models"
    )

    model_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    figure_dir = (
        FIGURES_DATA_DIR
        / SOURCE_ID
        / "modeling"
    )

    figure_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    rows = load_jsonl(
        dataset_path
    )

    if len(rows) != 13:

        raise ValueError(
            f"Expected 13 rows, "
            f"found {len(rows)}."
        )

    if not manifest_path.exists():

        raise FileNotFoundError(
            f"Missing baseline manifest: "
            f"{manifest_path}"
        )

    manifest = json.loads(
        manifest_path.read_text(
            encoding="utf-8"
        )
    )

    if (
        manifest.get(
            "dataset_version"
        )
        != DATASET_VERSION
    ):

        raise ValueError(
            "Unexpected dataset version."
        )

    if (
        manifest.get(
            "production_training_ready"
        )
        is not False
    ):

        raise ValueError(
            "Baseline v0 must remain "
            "non-production."
        )

    grouped = {}

    for group_name in (
        "microgravity",
        "normal_gravity",
    ):

        group_rows = [
            row
            for row in rows
            if (
                row.get(
                    "gravity_regime"
                )
                == group_name
            )
        ]

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
                f"{group_name}: "
                f"expected "
                f"{expected_count}, "
                f"found "
                f"{len(group_rows)}."
            )

        group_rows = sorted(
            group_rows,
            key=lambda row: (
                row[
                    "thickness_um"
                ]
            ),
        )

        thickness = np.array(
            [
                float(
                    row[
                        "thickness_um"
                    ]
                )
                for row
                in group_rows
            ],
            dtype=float,
        )

        spread_rate = np.array(
            [
                float(
                    row[
                        "spread_rate_mm_s"
                    ]
                )
                for row
                in group_rows
            ],
            dtype=float,
        )

        inverse_model = (
            fit_inverse_model(
                thickness,
                spread_rate,
            )
        )

        free_model = (
            fit_free_power_law(
                thickness,
                spread_rate,
            )
        )

        theory_prediction = (
            SOURCE_THEORY_COEFFICIENT
            / thickness
        )

        inverse_metrics = (
            calculate_metrics(
                spread_rate,
                inverse_model[
                    "predicted"
                ],
            )
        )

        free_metrics = (
            calculate_metrics(
                spread_rate,
                free_model[
                    "predicted"
                ],
            )
        )

        theory_metrics = (
            calculate_metrics(
                spread_rate,
                theory_prediction,
            )
        )

        prediction_rows = (
            make_prediction_rows(
                group_name=group_name,
                rows=group_rows,
                inverse_prediction=(
                    inverse_model[
                        "predicted"
                    ]
                ),
                free_prediction=(
                    free_model[
                        "predicted"
                    ]
                ),
                theory_prediction=(
                    theory_prediction
                ),
            )
        )

        grouped[
            group_name
        ] = {
            "record_count": (
                len(group_rows)
            ),

            "thickness_range_um": [
                float(
                    thickness.min()
                ),
                float(
                    thickness.max()
                ),
            ],

            "source_theory_reference": {
                "formula": (
                    "V = 223 / tau"
                ),

                "coefficient": (
                    SOURCE_THEORY_COEFFICIENT
                ),

                "exponent": -1.0,

                "fitted": False,

                "training_data": False,

                "metrics": (
                    theory_metrics
                ),
            },

            "physics_inverse_baseline": {
                "formula": (
                    "V = K / tau"
                ),

                "coefficient_k": (
                    inverse_model[
                        "coefficient_k"
                    ]
                ),

                "exponent": -1.0,

                "fit_space": (
                    "natural_log"
                ),

                "metrics": (
                    inverse_metrics
                ),
            },

            "free_power_law_diagnostic": {
                "formula": (
                    "V = A * tau^b"
                ),

                "coefficient_a": (
                    free_model[
                        "coefficient_a"
                    ]
                ),

                "exponent_b": (
                    free_model[
                        "exponent"
                    ]
                ),

                "fit_space": (
                    "natural_log"
                ),

                "role": (
                    "diagnostic_challenger_only"
                ),

                "metrics": (
                    free_metrics
                ),
            },

            "predictions": (
                prediction_rows
            ),
        }

    # --------------------------------
    # Save model report
    # --------------------------------

    result = {
        "model_name": (
            "FireSense PMMA "
            "Physics Baseline v0"
        ),

        "model_version": "v0",

        "dataset_version": "v0",

        "source_id": SOURCE_ID,

        "canonical_evidence_figure": (
            "2.21"
        ),

        "scientific_scope": {
            "material": "PMMA",

            "geometry": (
                "thin_sheet"
            ),

            "oxygen_fraction": 0.21,

            "pressure_kpa": 101.325,

            "input": (
                "thickness_um"
            ),

            "group_variable": (
                "gravity_regime"
            ),

            "output": (
                "spread_rate_mm_s"
            ),
        },

        "groups": (
            grouped
        ),

        "important_limitations": [
            (
                "Only 13 Figure 2.21 "
                "observations are used."
            ),

            (
                "Microgravity has only "
                "4 observations."
            ),

            (
                "Digitization uncertainty "
                "is known, but experimental "
                "uncertainty is not yet "
                "quantified."
            ),

            (
                "Digitization uncertainty "
                "is not used as statistical "
                "weight because it is not "
                "the complete observation "
                "uncertainty."
            ),

            (
                "The free power-law fit "
                "is diagnostic only and "
                "must not replace physics "
                "solely because it achieves "
                "lower training residuals."
            ),

            (
                "No Figure 2.22 points "
                "are used for fitting."
            ),

            (
                "No production or "
                "cross-study performance "
                "claim is supported."
            ),
        ],

        "modeling_policy": {
            "primary_baseline": (
                "physics_inverse_baseline"
            ),

            "diagnostic_challenger": (
                "free_power_law"
            ),

            "external_validation": (
                "pending Figure 2.22 "
                "provenance resolution"
            ),

            "production_ready": False,
        },

        "status": (
            "exploratory_physics_baseline_fitted"
        ),
    }

    model_path = (
        model_dir
        / "physics_baseline_v0.json"
    )

    model_path.write_text(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    # --------------------------------
    # Flatten predictions
    # --------------------------------

    predictions_path = (
        model_dir
        / "physics_baseline_v0_predictions.jsonl"
    )

    with predictions_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        for group_name in grouped:

            for row in (
                grouped[
                    group_name
                ][
                    "predictions"
                ]
            ):

                file.write(
                    json.dumps(
                        row,
                        ensure_ascii=False,
                    )
                )

                file.write(
                    "\n"
                )

    # --------------------------------
    # Plot
    # --------------------------------

    fig, ax = plt.subplots(
        figsize=(
            10,
            7,
        )
    )

    marker_map = {
        "microgravity": "o",
        "normal_gravity": "s",
    }

    for group_name in (
        "microgravity",
        "normal_gravity",
    ):

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
            key=lambda row: (
                row[
                    "thickness_um"
                ]
            ),
        )

        x = np.array(
            [
                row[
                    "thickness_um"
                ]
                for row
                in group_rows
            ],
            dtype=float,
        )

        y = np.array(
            [
                row[
                    "spread_rate_mm_s"
                ]
                for row
                in group_rows
            ],
            dtype=float,
        )

        yerr = np.array(
            [
                row[
                    "digitization_uncertainty_mm_s"
                ]
                for row
                in group_rows
            ],
            dtype=float,
        )

        group_result = (
            grouped[
                group_name
            ]
        )

        k = (
            group_result[
                "physics_inverse_baseline"
            ][
                "coefficient_k"
            ]
        )

        a = (
            group_result[
                "free_power_law_diagnostic"
            ][
                "coefficient_a"
            ]
        )

        b = (
            group_result[
                "free_power_law_diagnostic"
            ][
                "exponent_b"
            ]
        )

        x_curve = np.logspace(
            math.log10(
                x.min()
            ),
            math.log10(
                x.max()
            ),
            200,
        )

        ax.errorbar(
            x,
            y,
            yerr=yerr,
            fmt=marker_map[
                group_name
            ],
            linestyle="none",
            capsize=3,
            label=(
                f"{group_name} measured"
            ),
        )

        ax.plot(
            x_curve,
            k / x_curve,
            label=(
                f"{group_name} "
                f"V=K/tau"
            ),
        )

        ax.plot(
            x_curve,
            a
            * np.power(
                x_curve,
                b,
            ),
            linestyle="--",
            label=(
                f"{group_name} "
                f"free power law"
            ),
        )

    global_x_min = min(
        row[
            "thickness_um"
        ]
        for row in rows
    )

    global_x_max = max(
        row[
            "thickness_um"
        ]
        for row in rows
    )

    theory_x = np.logspace(
        math.log10(
            global_x_min
        ),
        math.log10(
            global_x_max
        ),
        300,
    )

    ax.plot(
        theory_x,
        SOURCE_THEORY_COEFFICIENT
        / theory_x,
        linestyle=":",
        linewidth=2,
        label=(
            "source theory reference "
            "V=223/tau"
        ),
    )

    ax.set_xscale(
        "log"
    )

    ax.set_yscale(
        "log"
    )

    ax.set_xlabel(
        "PMMA thickness (um)"
    )

    ax.set_ylabel(
        "Flame spread rate (mm/s)"
    )

    ax.set_title(
        "FireSense Physics Baseline v0"
    )

    ax.grid(
        True,
        which="both",
        alpha=0.25,
    )

    ax.legend(
        fontsize=8,
    )

    fig.tight_layout()

    plot_path = (
        figure_dir
        / "physics_baseline_v0.png"
    )

    fig.savefig(
        plot_path,
        dpi=180,
        bbox_inches="tight",
    )

    plt.close(
        fig
    )

    # --------------------------------
    # Terminal report
    # --------------------------------

    print()
    print(
        "FIRESENSE PHYSICS BASELINE V0"
    )

    print(
        "-----------------------------"
    )

    for group_name in (
        "microgravity",
        "normal_gravity",
    ):

        group = grouped[
            group_name
        ]

        inverse = group[
            "physics_inverse_baseline"
        ]

        free = group[
            "free_power_law_diagnostic"
        ]

        theory = group[
            "source_theory_reference"
        ]

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
            f"Records        : "
            f"{group['record_count']}"
        )

        print(
            f"Fitted K       : "
            f"{inverse['coefficient_k']:.6f}"
        )

        print(
            f"Physics model  : "
            f"V = "
            f"{inverse['coefficient_k']:.6f}"
            f" / tau"
        )

        print(
            f"Physics MAPE   : "
            f"{inverse['metrics']['mape_percent']:.2f}%"
        )

        print(
            f"Physics R2 log : "
            f"{inverse['metrics']['r2_log_space']:.4f}"
        )

        print(
            f"Free exponent  : "
            f"{free['exponent_b']:.6f}"
        )

        print(
            f"Free MAPE      : "
            f"{free['metrics']['mape_percent']:.2f}%"
        )

        print(
            f"Free R2 log    : "
            f"{free['metrics']['r2_log_space']:.4f}"
        )

        print(
            f"Theory 223/tau "
            f"MAPE            : "
            f"{theory['metrics']['mape_percent']:.2f}%"
        )

    print()
    print(
        "PRIMARY MODEL:"
    )

    print(
        "  V = K / tau"
    )

    print()
    print(
        "FREE POWER LAW:"
    )

    print(
        "  diagnostic only"
    )

    print()
    print(
        "SOURCE 223/tau:"
    )

    print(
        "  reference only"
    )

    print()
    print(
        "External validation:"
    )

    print(
        "  NOT YET PERFORMED"
    )

    print()
    print(
        "Production ready:"
    )

    print(
        "  NO"
    )

    print()
    print(
        "Saved:"
    )

    print(
        f"  {model_path}"
    )

    print(
        f"  {predictions_path}"
    )

    print(
        f"  {plot_path}"
    )


if __name__ == "__main__":
    main()