import json
from pathlib import Path

from app.core.paths import (
    CURATED_DATA_DIR,
    FIGURES_DATA_DIR,
)

from app.schemas.thin_sheet import (
    ThinSheetExperimentRecord,
)


SOURCE_ID = "SRC-NASA-20210011385"


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
) -> list[
    ThinSheetExperimentRecord
]:

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
                    f"line {line_number}: "
                    f"{exc}"
                ) from exc

    return records


def symmetric_percent_difference(
    a: float,
    b: float,
) -> float:

    denominator = (
        abs(a)
        + abs(b)
    ) / 2.0

    if denominator == 0:
        return 0.0

    return (
        abs(a - b)
        / denominator
        * 100.0
    )


def classify_match(
    thickness_difference_pct: float,
    spread_difference_pct: float,
) -> str:

    # These categories are review-priority
    # labels only.
    #
    # They do NOT prove same run or
    # same experiment.

    if (
        thickness_difference_pct <= 5.0
        and spread_difference_pct <= 10.0
    ):
        return "strong_duplicate_candidate"

    if (
        thickness_difference_pct <= 5.0
        and spread_difference_pct <= 20.0
    ):
        return "moderate_duplicate_candidate"

    if (
        thickness_difference_pct <= 5.0
        and spread_difference_pct <= 35.0
    ):
        return "possible_duplicate_candidate"

    return "weak_or_unresolved"


def find_nearest_by_thickness(
    source_point: dict,
    candidates: list[
        ThinSheetExperimentRecord
    ],
) -> ThinSheetExperimentRecord:

    return min(
        candidates,
        key=lambda record: abs(
            float(
                source_point[
                    "thickness_um"
                ]
            )
            - float(
                record.thickness_um
            )
        ),
    )


def compare_point(
    source_series: str,
    source_index: int,
    source_point: dict,
    target_record: ThinSheetExperimentRecord,
) -> dict:

    source_thickness = float(
        source_point[
            "thickness_um"
        ]
    )

    source_spread = float(
        source_point[
            "spread_rate_mm_s"
        ]
    )

    target_thickness = float(
        target_record.thickness_um
    )

    target_spread = float(
        target_record.flame_spread_rate_mm_s
    )

    thickness_delta = (
        source_thickness
        - target_thickness
    )

    spread_delta = (
        source_spread
        - target_spread
    )

    thickness_difference_pct = (
        symmetric_percent_difference(
            source_thickness,
            target_thickness,
        )
    )

    spread_difference_pct = (
        symmetric_percent_difference(
            source_spread,
            target_spread,
        )
    )

    classification = classify_match(
        thickness_difference_pct,
        spread_difference_pct,
    )

    return {
        "figure_2_22_point_id": (
            f"F222-{source_series.upper()}-"
            f"{source_index:03d}"
        ),

        "figure_2_22_series": (
            source_series
        ),

        "figure_2_22_thickness_um": (
            source_thickness
        ),

        "figure_2_22_spread_rate_mm_s": (
            source_spread
        ),

        "matched_figure_2_21_record_id": (
            target_record.record_id
        ),

        "figure_2_21_gravity_regime": (
            target_record.gravity_regime
        ),

        "figure_2_21_thickness_um": (
            target_thickness
        ),

        "figure_2_21_spread_rate_mm_s": (
            target_spread
        ),

        "thickness_delta_um": round(
            thickness_delta,
            6,
        ),

        "spread_rate_delta_mm_s": round(
            spread_delta,
            6,
        ),

        "thickness_symmetric_difference_pct": round(
            thickness_difference_pct,
            4,
        ),

        "spread_rate_symmetric_difference_pct": round(
            spread_difference_pct,
            4,
        ),

        "classification": (
            classification
        ),

        "relationship_status": (
            "unresolved"
        ),

        "same_run_confirmed": (
            False
        ),

        "safe_for_training_join": (
            False
        ),

        "important_note": (
            "Numerical similarity alone does "
            "not prove same experiment or "
            "same run."
        ),
    }


def main():

    curated_dir = (
        CURATED_DATA_DIR
        / "thin_sheet"
    )

    evidence_path = (
        curated_dir
        / "experiment_evidence.jsonl"
    )

    provenance_path = (
        curated_dir
        / "figure_2_22_provenance_audit_v0.json"
    )

    figure_dir = (
        FIGURES_DATA_DIR
        / SOURCE_ID
        / "digitization"
        / "figure_2_22"
    )

    figure_222_path = (
        figure_dir
        / "figure_2_22_final_review.json"
    )

    evidence = load_evidence(
        evidence_path
    )

    provenance = load_json(
        provenance_path
    )

    figure_222 = load_json(
        figure_222_path
    )

    if (
        provenance.get(
            "figure_validation_status"
        )
        != "human_overlay_verified"
    ):
        raise ValueError(
            "Figure 2.22 provenance audit "
            "is not based on human-verified "
            "digitization."
        )

    # ---------------------------------
    # Figure 2.21 canonical targets
    # ---------------------------------

    f221_microgravity = [
        record
        for record in evidence
        if (
            record.figure_ref == "2.21"
            and record.gravity_regime
            == "microgravity"
        )
    ]

    f221_downward = [
        record
        for record in evidence
        if (
            record.figure_ref == "2.21"
            and record.gravity_regime
            == "normal_gravity"
        )
    ]

    if len(
        f221_microgravity
    ) != 4:
        raise ValueError(
            "Expected 4 Figure 2.21 "
            "microgravity records."
        )

    if len(
        f221_downward
    ) != 9:
        raise ValueError(
            "Expected 9 Figure 2.21 "
            "downward records."
        )

    series = figure_222[
        "series"
    ]

    comparisons = []

    # ---------------------------------
    # BASS -> Figure 2.21 microgravity
    # ---------------------------------

    for index, point in enumerate(
        series["bass"]["points"],
        start=1,
    ):

        nearest = (
            find_nearest_by_thickness(
                point,
                f221_microgravity,
            )
        )

        comparisons.append(
            compare_point(
                source_series="bass",
                source_index=index,
                source_point=point,
                target_record=nearest,
            )
        )

    # ---------------------------------
    # NASA -> Figure 2.21 downward
    # ---------------------------------

    for index, point in enumerate(
        series["nasa"]["points"],
        start=1,
    ):

        nearest = (
            find_nearest_by_thickness(
                point,
                f221_downward,
            )
        )

        comparisons.append(
            compare_point(
                source_series="nasa",
                source_index=index,
                source_point=point,
                target_record=nearest,
            )
        )

    # ---------------------------------
    # Astra -> Figure 2.21 downward
    # ---------------------------------

    for index, point in enumerate(
        series["astra"]["points"],
        start=1,
    ):

        nearest = (
            find_nearest_by_thickness(
                point,
                f221_downward,
            )
        )

        comparisons.append(
            compare_point(
                source_series="astra",
                source_index=index,
                source_point=point,
                target_record=nearest,
            )
        )

    counts = {}

    for item in comparisons:

        classification = item[
            "classification"
        ]

        counts[
            classification
        ] = (
            counts.get(
                classification,
                0,
            )
            + 1
        )

    result = {
        "source_id": SOURCE_ID,

        "audit_name": (
            "Figure 2.22 vs Figure 2.21 "
            "duplicate linkage audit"
        ),

        "audit_version": "v1",

        "comparison_policy": {
            "bass_target_family": (
                "Figure 2.21 microgravity"
            ),

            "nasa_target_family": (
                "Figure 2.21 normal gravity"
            ),

            "astra_target_family": (
                "Figure 2.21 normal gravity"
            ),

            "matching_method": (
                "nearest thickness within "
                "the designated comparison "
                "family"
            ),

            "percent_difference_method": (
                "symmetric percent difference"
            ),

            "important_warning": (
                "Similarity categories are "
                "review-priority indicators, "
                "not proof of same-run identity."
            ),
        },

        "comparison_count": len(
            comparisons
        ),

        "classification_counts": (
            counts
        ),

        "comparisons": comparisons,

        "global_conclusion": {
            "same_run_links_confirmed": 0,

            "training_joins_approved": 0,

            "status": (
                "cross_figure_duplicate_risk_confirmed_"
                "but_identity_unresolved"
            ),

            "policy": (
                "Do not add Figure 2.22 BASS/NASA/Astra "
                "points as independent training rows "
                "until source identity is resolved."
            ),
        },
    }

    output_path = (
        curated_dir
        / "figure_2_22_duplicate_linkage_audit_v1.json"
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
        "FIGURE 2.22 DUPLICATE LINKAGE AUDIT"
    )

    print(
        "-----------------------------------"
    )

    print()
    print(
        f"Comparisons : "
        f"{len(comparisons)}"
    )

    print()

    for item in comparisons:

        print(
            f"{item['figure_2_22_point_id']:<18}"
            f" -> "
            f"{item['matched_figure_2_21_record_id']:<16}"
            f" | "
            f"dT={item['thickness_symmetric_difference_pct']:>6.2f}%"
            f" | "
            f"dV={item['spread_rate_symmetric_difference_pct']:>6.2f}%"
            f" | "
            f"{item['classification']}"
        )

    print()
    print(
        "CLASSIFICATION COUNTS"
    )

    print(
        "---------------------"
    )

    for (
        classification,
        count,
    ) in sorted(
        counts.items()
    ):

        print(
            f"{classification:<30}"
            f": "
            f"{count}"
        )

    print()
    print(
        "Same-run links confirmed : 0"
    )

    print(
        "Training joins approved  : 0"
    )

    print()
    print(
        "STATUS:"
    )

    print(
        "  duplicate risk present; "
        "identity unresolved"
    )

    print()
    print(
        f"Saved:"
    )

    print(
        f"  {output_path}"
    )

    print()
    print(
        "No evidence records or "
        "evidence links were modified."
    )


if __name__ == "__main__":
    main()