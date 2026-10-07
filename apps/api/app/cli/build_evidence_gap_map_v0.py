import json

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from app.core.paths import (
    CURATED_DATA_DIR,
    FIGURES_DATA_DIR,
)

from app.services.evidence_gap_analyzer import (
    EvidenceGapAnalyzer,
)


SOURCE_ID = "SRC-NASA-20210011385"


def main():

    analyzer = (
        EvidenceGapAnalyzer()
    )

    result = analyzer.build()

    curated_dir = (
        CURATED_DATA_DIR
        / "thin_sheet"
    )

    output_path = (
        curated_dir
        / "evidence_gap_map_v0.json"
    )

    output_path.write_text(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
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

    plot_path = (
        figure_dir
        / "evidence_gap_map_v0.png"
    )

    fig, ax = plt.subplots(
        figsize=(
            11,
            5,
        )
    )

    y_positions = {
        "normal_gravity": 0,
        "microgravity": 1,
    }

    for group_name in (
        "normal_gravity",
        "microgravity",
    ):

        group = (
            result[
                "groups"
            ][
                group_name
            ]
        )

        y = (
            y_positions[
                group_name
            ]
        )

        thicknesses = [
            point[
                "thickness_um"
            ]
            for point
            in group[
                "observations"
            ]
        ]

        ax.scatter(
            thicknesses,
            [
                y
                for _ in thicknesses
            ],
            marker="o",
            s=70,
            label=(
                f"{group_name} observations"
            ),
        )

        candidate = float(
            group[
                "coverage_candidate"
            ][
                "thickness_um"
            ]
        )

        ax.scatter(
            [
                candidate
            ],
            [
                y
            ],
            marker="*",
            s=180,
            label=(
                f"{group_name} "
                "largest-gap midpoint"
            ),
        )

        for interval in (
            group[
                "intervals"
            ]
        ):

            left = float(
                interval[
                    "left_thickness_um"
                ]
            )

            right = float(
                interval[
                    "right_thickness_um"
                ]
            )

            score = float(
                interval[
                    "relative_gap_score"
                ]
            )

            ax.plot(
                [
                    left,
                    right,
                ],
                [
                    y,
                    y,
                ],
                linewidth=(
                    1.0
                    + 4.0
                    * score
                ),
                alpha=0.35,
            )

    ax.set_xscale(
        "log"
    )

    ax.set_yticks(
        [
            0,
            1,
        ]
    )

    ax.set_yticklabels(
        [
            "Normal gravity",
            "Microgravity",
        ]
    )

    ax.set_xlabel(
        "PMMA thickness (µm, log scale)"
    )

    ax.set_title(
        "FireSense Evidence Coverage "
        "Gap Map v0"
    )

    ax.grid(
        True,
        axis="x",
        which="both",
        alpha=0.25,
    )

    ax.legend(
        fontsize=8,
        loc="best",
    )

    fig.tight_layout()

    fig.savefig(
        plot_path,
        dpi=180,
        bbox_inches="tight",
    )

    plt.close(
        fig
    )

    print()
    print(
        "FIRESENSE EVIDENCE GAP MAP V0"
    )

    print(
        "-----------------------------"
    )

    for group_name in (
        "microgravity",
        "normal_gravity",
    ):

        group = (
            result[
                "groups"
            ][
                group_name
            ]
        )

        candidate = (
            group[
                "coverage_candidate"
            ]
        )

        largest = (
            group[
                "largest_internal_gap"
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
            f"Records       : "
            f"{group['record_count']}"
        )

        print(
            "Domain        : "
            f"{group['empirical_domain_um']['min']:.3f}"
            " - "
            f"{group['empirical_domain_um']['max']:.3f}"
            " um"
        )

        print(
            "Largest gap   : "
            f"{largest['left_thickness_um']:.3f}"
            " -> "
            f"{largest['right_thickness_um']:.3f}"
            " um"
        )

        print(
            "Gap decades   : "
            f"{largest['log_gap_decades']:.4f}"
        )

        print(
            "Candidate     : "
            f"{candidate['thickness_um']:.3f}"
            " um"
        )

    pair = (
        result[
            "paired_candidate_hint"
        ]
    )

    print()
    print(
        "PAIRED CANDIDATE HINT"
    )

    print(
        "---------------------"
    )

    print(
        "Microgravity : "
        f"{pair['microgravity_candidate_um']:.3f}"
        " um"
    )

    print(
        "Normal       : "
        f"{pair['normal_gravity_candidate_um']:.3f}"
        " um"
    )

    print(
        "Similar      : "
        f"{pair['similar_thickness_candidate']}"
    )

    print()
    print(
        "IMPORTANT:"
    )

    print(
        "  This is a coverage-only "
        "heuristic."
    )

    print(
        "  It is NOT yet a Bayesian "
        "next-experiment recommendation."
    )

    print()
    print(
        "STATUS:"
    )

    print(
        "  empirical_coverage_gap_map_complete"
    )

    print()
    print(
        "Saved:"
    )

    print(
        f"  {output_path}"
    )

    print(
        f"  {plot_path}"
    )


if __name__ == "__main__":
    main()