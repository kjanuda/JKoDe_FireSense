import csv
import json
import statistics

from app.core.paths import FIGURES_DATA_DIR


SOURCE_ID = "SRC-NASA-20210011385"

TIME_START = 1.0
TIME_END = 18.5
SAMPLE_INTERVAL = 0.25


def summarize(points: list[dict]) -> dict:

    values = [
        point["spread_rate_mm_s"]
        for point in points
    ]

    if not values:
        return {
            "count": 0,
        }

    return {
        "count": len(values),
        "mean_mm_s": statistics.mean(
            values
        ),
        "median_mm_s": statistics.median(
            values
        ),
        "min_mm_s": min(values),
        "max_mm_s": max(values),
        "std_mm_s": (
            statistics.stdev(values)
            if len(values) > 1
            else 0.0
        ),
    }


def main():

    root = (
        FIGURES_DATA_DIR
        / SOURCE_ID
        / "digitization"
        / "figure_2_19"
    )

    input_path = (
        root
        / "trace_preview.json"
    )

    data = json.loads(
        input_path.read_text(
            encoding="utf-8"
        )
    )

    zero_points = (
        data["series"]["0g"]["points"]
    )

    one_points = (
        data["series"]["1g"]["points"]
    )

    expected_count = (
        int(
            round(
                (
                    TIME_END
                    - TIME_START
                )
                / SAMPLE_INTERVAL
            )
        )
        + 1
    )

    zero_summary = summarize(
        zero_points
    )

    one_summary = summarize(
        one_points
    )

    zero_coverage = (
        zero_summary["count"]
        / expected_count
    )

    one_coverage = (
        one_summary["count"]
        / expected_count
    )

    checks = {
        "0g_coverage_pass": (
            zero_coverage >= 0.90
        ),
        "1g_coverage_pass": (
            one_coverage >= 0.85
        ),
        "0g_plausible_range_pass": (
            1.5
            <= zero_summary["mean_mm_s"]
            <= 2.6
        ),
        "1g_plausible_range_pass": (
            1.5
            <= one_summary["mean_mm_s"]
            <= 2.6
        ),
    }

    automated_pass = all(
        checks.values()
    )

    result = {
        "source_id": SOURCE_ID,
        "figure_ref": "2.19",
        "panel_id": "B",

        "expected_sample_positions": (
            expected_count
        ),

        "series": {
            "0g": {
                **zero_summary,
                "coverage_fraction": (
                    zero_coverage
                ),
            },
            "1g": {
                **one_summary,
                "coverage_fraction": (
                    one_coverage
                ),
            },
        },

        "automated_checks": checks,

        "automated_validation": (
            "pass"
            if automated_pass
            else "fail"
        ),

        "visual_overlay_status": (
            "pending_human_acceptance"
        ),

        "important_note": (
            "Digitized time-series points "
            "are not independent experimental "
            "runs and must not be treated as "
            "independent GP training rows."
        ),
    }

    output_path = (
        root
        / "trace_validation.json"
    )

    output_path.write_text(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    csv_path = (
        root
        / "figure_2_19_timeseries.csv"
    )

    with csv_path.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:

        writer = csv.writer(
            file
        )

        writer.writerow(
            [
                "series",
                "gravity_regime",
                "time_s",
                "spread_rate_mm_s",
                "pixel_x",
                "pixel_y",
                "human_verified",
            ]
        )

        for point in zero_points:
            writer.writerow(
                [
                    "0g",
                    "microgravity",
                    point["time_s"],
                    point[
                        "spread_rate_mm_s"
                    ],
                    point["pixel_x"],
                    point["pixel_y"],
                    False,
                ]
            )

        for point in one_points:
            writer.writerow(
                [
                    "1g",
                    "normal_gravity",
                    point["time_s"],
                    point[
                        "spread_rate_mm_s"
                    ],
                    point["pixel_x"],
                    point["pixel_y"],
                    False,
                ]
            )

    print()
    print(
        "FIGURE 2.19 TRACE VALIDATION"
    )
    print(
        "----------------------------"
    )

    print(
        f"Expected positions: "
        f"{expected_count}"
    )

    print()

    print(
        "0g:"
    )

    print(
        f"  count    : "
        f"{zero_summary['count']}"
    )

    print(
        f"  coverage : "
        f"{zero_coverage:.1%}"
    )

    print(
        f"  mean     : "
        f"{zero_summary['mean_mm_s']:.4f}"
    )

    print(
        f"  median   : "
        f"{zero_summary['median_mm_s']:.4f}"
    )

    print(
        f"  std      : "
        f"{zero_summary['std_mm_s']:.4f}"
    )

    print()

    print(
        "1g:"
    )

    print(
        f"  count    : "
        f"{one_summary['count']}"
    )

    print(
        f"  coverage : "
        f"{one_coverage:.1%}"
    )

    print(
        f"  mean     : "
        f"{one_summary['mean_mm_s']:.4f}"
    )

    print(
        f"  median   : "
        f"{one_summary['median_mm_s']:.4f}"
    )

    print(
        f"  std      : "
        f"{one_summary['std_mm_s']:.4f}"
    )

    print()

    print(
        "Automated validation:",
        result[
            "automated_validation"
        ],
    )

    print()
    print(
        f"JSON: {output_path}"
    )

    print(
        f"CSV : {csv_path}"
    )


if __name__ == "__main__":
    main()