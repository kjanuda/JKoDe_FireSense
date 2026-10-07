import json
from pathlib import Path

from app.core.paths import (
    CURATED_DATA_DIR,
    FIGURES_DATA_DIR,
)


SOURCE_ID = "SRC-NASA-20210011385"


SERIES_POLICIES = {
    "mrc": {
        "label": "MRC",
        "identity_status": "unresolved",
        "gravity_status": "unresolved",
        "source_family_status": "unresolved",
        "possible_duplicate_with_existing_evidence": False,
        "training_safe": False,
        "notes": [
            (
                "Series label is visible in Figure 2.22, "
                "but exact original study identity and "
                "experimental conditions are not yet "
                "proven from the current source audit."
            ),
            (
                "Do not infer gravity, oxygen, pressure, "
                "or flow conditions from marker position."
            ),
        ],
    },

    "vcf": {
        "label": "VCF",
        "identity_status": "unresolved",
        "gravity_status": "unresolved",
        "source_family_status": "unresolved",
        "possible_duplicate_with_existing_evidence": False,
        "training_safe": False,
        "notes": [
            (
                "Series label is visible in Figure 2.22, "
                "but exact original study identity and "
                "experimental conditions remain unresolved."
            ),
            (
                "Do not propagate conditions from BASS-II "
                "or another series."
            ),
        ],
    },

    "astra": {
        "label": "Astra",
        "identity_status": "partially_resolved",
        "gravity_status": "probable_normal_gravity",
        "source_family_status": "surrounding_report_context",
        "possible_duplicate_with_existing_evidence": True,
        "training_safe": False,
        "notes": [
            (
                "The surrounding report section identifies "
                "Astra PMMA data in normal gravity at "
                "San Diego State University."
            ),
            (
                "Figure-level linkage must still be checked "
                "before assigning exact atmosphere or "
                "run-specific conditions to this Figure 2.22 point."
            ),
            (
                "May overlap with data already represented "
                "elsewhere in Figures 2.20/2.21."
            ),
        ],
    },

    "nasa": {
        "label": "NASA",
        "identity_status": "partially_resolved",
        "gravity_status": "probable_normal_gravity",
        "source_family_status": "surrounding_report_context",
        "possible_duplicate_with_existing_evidence": True,
        "training_safe": False,
        "notes": [
            (
                "The surrounding report section identifies "
                "NASA PMMA comparison data in normal gravity."
            ),
            (
                "Exact point-to-run identity is not proven."
            ),
            (
                "May overlap with downward evidence already "
                "represented in the FireSense evidence store."
            ),
        ],
    },

    "bass": {
        "label": "BASS",
        "identity_status": "partially_resolved",
        "gravity_status": "probable_microgravity",
        "source_family_status": "BASS-II",
        "possible_duplicate_with_existing_evidence": True,
        "training_safe": False,
        "notes": [
            (
                "BASS/BASS-II is part of the microgravity "
                "PMMA study family in the surrounding section."
            ),
            (
                "The four Figure 2.22 BASS thicknesses are "
                "close to the 100/200/300/400 µm family "
                "already represented by Figure 2.21."
            ),
            (
                "Treat as possible duplicate/derived "
                "representation until explicitly linked."
            ),
        ],
    },

    "ridout": {
        "label": "Ridout",
        "identity_status": "label_known_source_unresolved",
        "gravity_status": "unresolved",
        "source_family_status": "external_literature",
        "possible_duplicate_with_existing_evidence": False,
        "training_safe": False,
        "notes": [
            (
                "Figure label identifies Ridout, but the "
                "original publication and full conditions "
                "must be recovered before modeling."
            ),
            (
                "Large-thickness data must not automatically "
                "be assumed to share BASS-II conditions."
            ),
        ],
    },

    "fernandez_pello_williams": {
        "label": "Fernandez-Pello and Williams",
        "identity_status": "named_external_literature",
        "gravity_status": "unresolved_until_reference_review",
        "source_family_status": "external_literature",
        "possible_duplicate_with_existing_evidence": False,
        "training_safe": False,
        "notes": [
            (
                "Figure 2.22 explicitly labels this as "
                "Fernandez-Pello and Williams experimental data."
            ),
            (
                "Original publication and experimental "
                "conditions must be checked before training."
            ),
        ],
    },
}


def load_json(
    path: Path,
) -> dict:

    if not path.exists():
        raise FileNotFoundError(
            f"Missing required file: {path}"
        )

    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


def main():

    figure_dir = (
        FIGURES_DATA_DIR
        / SOURCE_ID
        / "digitization"
        / "figure_2_22"
    )

    review_path = (
        figure_dir
        / "figure_2_22_final_review.json"
    )

    validation_path = (
        figure_dir
        / "figure_2_22_final_validation.json"
    )

    review = load_json(
        review_path
    )

    validation = load_json(
        validation_path
    )

    if (
        validation.get("final_status")
        != "pass"
    ):
        raise ValueError(
            "Figure 2.22 final validation "
            "must be PASS before provenance audit."
        )

    if (
        review.get("human_verified")
        is not True
    ):
        raise ValueError(
            "Figure 2.22 has not been "
            "human verified."
        )

    series = review.get(
        "series",
        {},
    )

    audit_series = {}

    total_points = 0

    for (
        series_id,
        policy,
    ) in SERIES_POLICIES.items():

        if series_id not in series:
            raise ValueError(
                f"Missing Figure 2.22 "
                f"series: {series_id}"
            )

        figure_series = series[
            series_id
        ]

        points = figure_series.get(
            "points",
            [],
        )

        total_points += len(
            points
        )

        audit_series[
            series_id
        ] = {
            "label": (
                policy["label"]
            ),

            "point_count": len(
                points
            ),

            "marker": (
                figure_series.get(
                    "marker"
                )
            ),

            "evidence_type": (
                "experimental"
            ),

            "identity_status": (
                policy[
                    "identity_status"
                ]
            ),

            "gravity_status": (
                policy[
                    "gravity_status"
                ]
            ),

            "source_family_status": (
                policy[
                    "source_family_status"
                ]
            ),

            "possible_duplicate_with_existing_evidence": (
                policy[
                    "possible_duplicate_with_existing_evidence"
                ]
            ),

            "training_safe": (
                policy[
                    "training_safe"
                ]
            ),

            "notes": (
                policy["notes"]
            ),

            "points": points,
        }

    if total_points != 33:
        raise ValueError(
            f"Expected 33 points, "
            f"found {total_points}."
        )

    possible_duplicate_series = [
        series_id
        for (
            series_id,
            item,
        ) in audit_series.items()
        if item[
            "possible_duplicate_with_existing_evidence"
        ]
    ]

    unresolved_identity_series = [
        series_id
        for (
            series_id,
            item,
        ) in audit_series.items()
        if (
            item["identity_status"]
            in {
                "unresolved",
                "label_known_source_unresolved",
            }
        )
    ]

    training_safe_series = [
        series_id
        for (
            series_id,
            item,
        ) in audit_series.items()
        if item[
            "training_safe"
        ]
    ]

    result = {
        "source_id": SOURCE_ID,

        "figure_ref": "2.22",

        "audit_version": "v0",

        "figure_validation_status": (
            "human_overlay_verified"
        ),

        "total_experimental_points": (
            total_points
        ),

        "theoretical_curves_included": (
            False
        ),

        "series": audit_series,

        "summary": {
            "series_count": (
                len(
                    audit_series
                )
            ),

            "possible_duplicate_series": (
                possible_duplicate_series
            ),

            "unresolved_identity_series": (
                unresolved_identity_series
            ),

            "training_safe_series": (
                training_safe_series
            ),

            "training_safe_point_count": 0,
        },

        "global_policy": [
            (
                "Figure 2.22 is a cross-study "
                "comparison figure."
            ),
            (
                "A plotted series label is not "
                "sufficient proof of complete "
                "experimental conditions."
            ),
            (
                "No Figure 2.22 point may be "
                "marked training-ready until "
                "its original-study provenance "
                "and duplicate status are audited."
            ),
            (
                "Theoretical thin/thick limits "
                "must remain separate from "
                "experimental evidence."
            ),
            (
                "No run-specific BASS-II "
                "conditions may be propagated "
                "without an explicit evidence link."
            ),
        ],

        "next_required_actions": [
            (
                "Resolve MRC original study/reference."
            ),
            (
                "Resolve VCF original study/reference."
            ),
            (
                "Confirm NASA/Astra Figure 2.22 "
                "relationship to normal-gravity "
                "comparison experiments."
            ),
            (
                "Audit BASS Figure 2.22 points "
                "against Figure 2.21 and BASS-II "
                "run-condition evidence."
            ),
            (
                "Resolve Ridout original publication "
                "and conditions."
            ),
            (
                "Resolve Fernandez-Pello and Williams "
                "original publication and conditions."
            ),
        ],
    }

    output_dir = (
        CURATED_DATA_DIR
        / "thin_sheet"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        output_dir
        / "figure_2_22_provenance_audit_v0.json"
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
        "FIGURE 2.22 PROVENANCE AUDIT V0"
    )

    print(
        "--------------------------------"
    )

    print()
    print(
        f"Experimental points : "
        f"{total_points}"
    )

    print(
        f"Series              : "
        f"{len(audit_series)}"
    )

    print()

    print(
        "SERIES STATUS"
    )

    print(
        "-------------"
    )

    for (
        series_id,
        item,
    ) in audit_series.items():

        print()
        print(
            f"{item['label']}"
        )

        print(
            f"  points          : "
            f"{item['point_count']}"
        )

        print(
            f"  identity        : "
            f"{item['identity_status']}"
        )

        print(
            f"  gravity         : "
            f"{item['gravity_status']}"
        )

        print(
            f"  source family   : "
            f"{item['source_family_status']}"
        )

        print(
            f"  duplicate risk  : "
            f"{item['possible_duplicate_with_existing_evidence']}"
        )

        print(
            f"  training safe   : "
            f"{item['training_safe']}"
        )

    print()
    print(
        "SUMMARY"
    )

    print(
        "-------"
    )

    print(
        "Possible duplicate series:"
    )

    for series_id in (
        possible_duplicate_series
    ):
        print(
            f"  - {series_id}"
        )

    print()
    print(
        "Unresolved identity series:"
    )

    for series_id in (
        unresolved_identity_series
    ):
        print(
            f"  - {series_id}"
        )

    print()
    print(
        "Training-safe Figure 2.22 "
        "series: 0"
    )

    print()
    print(
        "IMPORTANT:"
    )

    print(
        "  No Figure 2.22 points "
        "were added to the training "
        "dataset."
    )

    print()
    print(
        f"Saved:"
    )

    print(
        f"  {output_path}"
    )


if __name__ == "__main__":
    main()