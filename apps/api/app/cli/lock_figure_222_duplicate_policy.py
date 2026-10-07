import json
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


def main():

    curated_dir = (
        CURATED_DATA_DIR
        / "thin_sheet"
    )

    audit_path = (
        curated_dir
        / "figure_2_22_duplicate_linkage_audit_v1.json"
    )

    audit = load_json(
        audit_path
    )

    comparisons = audit.get(
        "comparisons",
        [],
    )

    if len(comparisons) != 8:
        raise ValueError(
            f"Expected 8 comparisons, "
            f"found {len(comparisons)}."
        )

    classifications = [
        item["classification"]
        for item in comparisons
    ]

    strong_count = (
        classifications.count(
            "strong_duplicate_candidate"
        )
    )

    moderate_count = (
        classifications.count(
            "moderate_duplicate_candidate"
        )
    )

    possible_count = (
        classifications.count(
            "possible_duplicate_candidate"
        )
    )

    if strong_count < 1:
        raise ValueError(
            "Expected at least one strong "
            "duplicate candidate."
        )

    policy = {
        "policy_version": "v1",

        "scope": (
            "Figure 2.22 BASS/NASA/Astra "
            "versus Figure 2.21 canonical "
            "experimental evidence"
        ),

        "audit_source": (
            str(audit_path)
        ),

        "comparison_summary": {
            "total": len(
                comparisons
            ),

            "strong": (
                strong_count
            ),

            "moderate": (
                moderate_count
            ),

            "possible": (
                possible_count
            ),
        },

        "canonical_evidence_policy": {
            "microgravity": (
                "Figure 2.21"
            ),

            "normal_gravity": (
                "Figure 2.21"
            ),

            "reason": (
                "Figure 2.21 provides the "
                "already-curated experimental "
                "thin-sheet observations used "
                "by FireSense. Figure 2.22 is "
                "a cross-study comparison plot "
                "with substantial numerical "
                "overlap."
            ),
        },

        "figure_2_22_series_policy": {
            "bass": {
                "independent_training_row": (
                    False
                ),

                "use": (
                    "comparison_validation_only"
                ),

                "relationship": (
                    "possible_duplicate_or_"
                    "derived_representation"
                ),

                "same_run_confirmed": (
                    False
                ),
            },

            "nasa": {
                "independent_training_row": (
                    False
                ),

                "use": (
                    "comparison_validation_only"
                ),

                "relationship": (
                    "possible_duplicate_or_"
                    "derived_representation"
                ),

                "same_run_confirmed": (
                    False
                ),
            },

            "astra": {
                "independent_training_row": (
                    False
                ),

                "use": (
                    "comparison_validation_only"
                ),

                "relationship": (
                    "possible_duplicate_or_"
                    "derived_representation"
                ),

                "same_run_confirmed": (
                    False
                ),
            },
        },

        "external_series_policy": {
            "mrc": {
                "training_status": (
                    "blocked_pending_source_resolution"
                )
            },

            "vcf": {
                "training_status": (
                    "blocked_pending_source_resolution"
                )
            },

            "ridout": {
                "training_status": (
                    "blocked_pending_source_resolution"
                )
            },

            "fernandez_pello_williams": {
                "training_status": (
                    "blocked_pending_source_resolution"
                )
            },
        },

        "scientific_safeguards": [
            (
                "Numerical similarity is not "
                "proof of same-run identity."
            ),

            (
                "Figure 2.22 BASS/NASA/Astra "
                "points must not be added as "
                "independent training rows."
            ),

            (
                "No Appendix run conditions "
                "may be propagated without "
                "explicit evidence linkage."
            ),

            (
                "Figure 2.21 remains the "
                "canonical thin-sheet modeling "
                "evidence for overlapping "
                "thickness regions."
            ),

            (
                "Figure 2.22 external literature "
                "series require original-source "
                "provenance review before modeling."
            ),
        ],

        "status": (
            "duplicate_policy_locked"
        ),
    }

    output_path = (
        curated_dir
        / "figure_2_22_duplicate_policy_v1.json"
    )

    output_path.write_text(
        json.dumps(
            policy,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print()
    print(
        "FIGURE 2.22 DUPLICATE POLICY"
    )

    print(
        "----------------------------"
    )

    print()
    print(
        f"Comparisons : "
        f"{len(comparisons)}"
    )

    print(
        f"Strong      : "
        f"{strong_count}"
    )

    print(
        f"Moderate    : "
        f"{moderate_count}"
    )

    print(
        f"Possible    : "
        f"{possible_count}"
    )

    print()
    print(
        "CANONICAL POLICY"
    )

    print(
        "----------------"
    )

    print(
        "Figure 2.21:"
    )

    print(
        "  canonical modeling evidence"
    )

    print()

    print(
        "Figure 2.22 BASS:"
    )

    print(
        "  comparison/validation only"
    )

    print()

    print(
        "Figure 2.22 NASA:"
    )

    print(
        "  comparison/validation only"
    )

    print()

    print(
        "Figure 2.22 Astra:"
    )

    print(
        "  comparison/validation only"
    )

    print()
    print(
        "EXTERNAL SERIES"
    )

    print(
        "---------------"
    )

    print(
        "MRC:"
    )

    print(
        "  source resolution required"
    )

    print()

    print(
        "VCF:"
    )

    print(
        "  source resolution required"
    )

    print()

    print(
        "Ridout:"
    )

    print(
        "  source resolution required"
    )

    print()

    print(
        "Fernandez-Pello and Williams:"
    )

    print(
        "  source resolution required"
    )

    print()
    print(
        "STATUS:"
    )

    print(
        "  duplicate_policy_locked"
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