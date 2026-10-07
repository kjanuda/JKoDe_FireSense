import json
from pathlib import Path

from app.core.paths import CURATED_DATA_DIR


SOURCE_ID = "SRC-NASA-20210011385"


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

    curated_dir = (
        CURATED_DATA_DIR
        / "thin_sheet"
    )

    provenance_path = (
        curated_dir
        / "figure_2_22_provenance_audit_v0.json"
    )

    duplicate_policy_path = (
        curated_dir
        / "figure_2_22_duplicate_policy_v1.json"
    )

    provenance = load_json(
        provenance_path
    )

    duplicate_policy = load_json(
        duplicate_policy_path
    )

    if (
        duplicate_policy.get("status")
        != "duplicate_policy_locked"
    ):
        raise ValueError(
            "Figure 2.22 duplicate policy "
            "must be locked first."
        )

    if (
        provenance.get(
            "total_experimental_points"
        )
        != 33
    ):
        raise ValueError(
            "Expected 33 Figure 2.22 "
            "experimental points."
        )

    resolution = {
        "source_id": SOURCE_ID,

        "figure_ref": "2.22",

        "resolution_version": "v1",

        "status": (
            "external_source_resolution_in_progress"
        ),

        "series": {

            # ------------------------------------
            # MRC
            # ------------------------------------

            "mrc": {
                "label": "MRC",

                "point_count": 2,

                "publication_identity_status": (
                    "unresolved"
                ),

                "experimental_conditions_status": (
                    "unresolved"
                ),

                "source_independence_status": (
                    "unresolved"
                ),

                "training_safe": False,

                "notes": [
                    (
                        "MRC is a Figure 2.22 "
                        "legend label."
                    ),
                    (
                        "No original publication "
                        "identity has yet been "
                        "verified."
                    ),
                    (
                        "Do not infer gravity, "
                        "oxygen, pressure, geometry, "
                        "or flow conditions."
                    ),
                ],
            },

            # ------------------------------------
            # VCF
            # ------------------------------------

            "vcf": {
                "label": "VCF",

                "point_count": 5,

                "publication_identity_status": (
                    "unresolved"
                ),

                "experimental_conditions_status": (
                    "unresolved"
                ),

                "source_independence_status": (
                    "unresolved"
                ),

                "training_safe": False,

                "notes": [
                    (
                        "VCF is a Figure 2.22 "
                        "legend label."
                    ),
                    (
                        "Original publication and "
                        "experimental conditions "
                        "remain unresolved."
                    ),
                ],
            },

            # ------------------------------------
            # RIDOUT
            # ------------------------------------

            "ridout": {
                "label": "Ridout",

                "point_count": 4,

                "publication_identity_status": (
                    "unresolved"
                ),

                "experimental_conditions_status": (
                    "unresolved"
                ),

                "source_independence_status": (
                    "unresolved"
                ),

                "training_safe": False,

                "notes": [
                    (
                        "Ridout is identified by "
                        "name in the Figure 2.22 "
                        "legend."
                    ),
                    (
                        "A trustworthy original "
                        "combustion publication has "
                        "not yet been resolved."
                    ),
                    (
                        "Do not confuse the author/"
                        "source label with commercial "
                        "PMMA suppliers carrying the "
                        "Ridout name."
                    ),
                ],
            },

            # ------------------------------------
            # FERNANDEZ-PELLO & WILLIAMS
            # ------------------------------------

            "fernandez_pello_williams": {
                "label": (
                    "Fernandez-Pello and Williams"
                ),

                "point_count": 14,

                "publication_identity_status": (
                    "resolved"
                ),

                "publication": {
                    "authors": [
                        "A. Fernandez-Pello",
                        "F. A. Williams",
                    ],

                    "title": (
                        "Laminar flame spread "
                        "over PMMA surfaces"
                    ),

                    "year": 1975,

                    "venue": (
                        "Symposium (International) "
                        "on Combustion"
                    ),

                    "volume": "15",

                    "issue": "1",

                    "pages": "217-231",

                    "doi": (
                        "10.1016/"
                        "S0082-0784(75)80299-2"
                    ),
                },

                "figure_link_status": (
                    "supported_by_nasa_figure_caption"
                ),

                "experimental_conditions_status": (
                    "original_paper_review_required"
                ),

                "exact_plotted_subset_status": (
                    "unresolved"
                ),

                "source_independence_status": (
                    "likely_external_literature_"
                    "but_not_yet_training_approved"
                ),

                "training_safe": False,

                "notes": [
                    (
                        "NASA Figure 2.22 explicitly "
                        "describes Fernandez-Pello "
                        "and Williams experimental "
                        "PMMA data."
                    ),
                    (
                        "The bibliographic identity "
                        "of the Fernandez-Pello and "
                        "Williams publication has "
                        "been resolved."
                    ),
                    (
                        "The exact subset of the "
                        "1975 paper represented by "
                        "the 14 Figure 2.22 points "
                        "still requires original-"
                        "paper review."
                    ),
                    (
                        "Do not assign atmosphere, "
                        "orientation, gravity, or "
                        "flow conditions to the "
                        "14 points until that review "
                        "is complete."
                    ),
                ],
            },

            # ------------------------------------
            # DUPLICATE-POLICY SERIES
            # ------------------------------------

            "bass": {
                "point_count": 4,

                "source_status": (
                    "BASS-II_family"
                ),

                "independent_training_row": False,

                "use": (
                    "comparison_validation_only"
                ),

                "reason": (
                    "Duplicate-risk policy locked "
                    "against canonical Figure 2.21 "
                    "microgravity evidence."
                ),
            },

            "nasa": {
                "point_count": 3,

                "source_status": (
                    "surrounding_report_context"
                ),

                "independent_training_row": False,

                "use": (
                    "comparison_validation_only"
                ),

                "reason": (
                    "Duplicate-risk policy locked "
                    "against canonical Figure 2.21 "
                    "normal-gravity evidence."
                ),
            },

            "astra": {
                "point_count": 1,

                "source_status": (
                    "surrounding_report_context"
                ),

                "independent_training_row": False,

                "use": (
                    "comparison_validation_only"
                ),

                "reason": (
                    "Duplicate-risk policy locked "
                    "against canonical Figure 2.21 "
                    "normal-gravity evidence."
                ),
            },
        },

        "summary": {
            "series_total": 7,

            "fully_training_approved_series": 0,

            "publication_identity_resolved": [
                "fernandez_pello_williams"
            ],

            "publication_identity_unresolved": [
                "mrc",
                "vcf",
                "ridout",
            ],

            "comparison_only_duplicate_risk_series": [
                "bass",
                "nasa",
                "astra",
            ],
        },

        "next_required_actions": [
            (
                "Review the original "
                "Fernandez-Pello and Williams "
                "1975 paper to resolve which "
                "measurements produced the "
                "14 plotted points."
            ),
            (
                "Resolve the original MRC "
                "publication/source."
            ),
            (
                "Resolve the original VCF "
                "publication/source."
            ),
            (
                "Resolve the original Ridout "
                "publication/source."
            ),
            (
                "Keep BASS/NASA/Astra as "
                "comparison-only evidence."
            ),
        ],

        "global_policy": [
            (
                "Bibliographic identity alone "
                "does not make a series "
                "training-ready."
            ),
            (
                "Exact experimental conditions "
                "must be supported by the "
                "original source."
            ),
            (
                "Unknown conditions must remain "
                "null rather than inferred."
            ),
            (
                "Cross-study independence must "
                "be confirmed before group-based "
                "model validation."
            ),
        ],
    }

    output_path = (
        curated_dir
        / "figure_2_22_external_source_resolution_v1.json"
    )

    output_path.write_text(
        json.dumps(
            resolution,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print()
    print(
        "FIGURE 2.22 EXTERNAL SOURCE RESOLUTION"
    )

    print(
        "--------------------------------------"
    )

    print()

    print(
        "MRC:"
    )

    print(
        "  publication identity : UNRESOLVED"
    )

    print()

    print(
        "VCF:"
    )

    print(
        "  publication identity : UNRESOLVED"
    )

    print()

    print(
        "Ridout:"
    )

    print(
        "  publication identity : UNRESOLVED"
    )

    print()

    print(
        "Fernandez-Pello & Williams:"
    )

    print(
        "  publication identity : RESOLVED"
    )

    print(
        "  paper                : "
        "Laminar flame spread "
        "over PMMA surfaces"
    )

    print(
        "  year                 : 1975"
    )

    print(
        "  DOI                  : "
        "10.1016/S0082-0784(75)80299-2"
    )

    print(
        "  exact plotted subset : UNRESOLVED"
    )

    print(
        "  training safe        : NO"
    )

    print()

    print(
        "BASS / NASA / Astra:"
    )

    print(
        "  comparison-validation only"
    )

    print()

    print(
        "Training-approved external "
        "series: 0"
    )

    print()

    print(
        "STATUS:"
    )

    print(
        "  external_source_resolution_in_progress"
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