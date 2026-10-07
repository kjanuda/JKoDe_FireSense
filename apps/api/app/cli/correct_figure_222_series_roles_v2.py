import json
from pathlib import Path

from app.core.paths import CURATED_DATA_DIR


SOURCE_ID = "SRC-NASA-20210011385"


def load_json(path: Path) -> dict:

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

    resolution_v1_path = (
        curated_dir
        / "figure_2_22_external_source_resolution_v1.json"
    )

    duplicate_policy_path = (
        curated_dir
        / "figure_2_22_duplicate_policy_v1.json"
    )

    provenance = load_json(
        provenance_path
    )

    resolution_v1 = load_json(
        resolution_v1_path
    )

    duplicate_policy = load_json(
        duplicate_policy_path
    )

    if (
        provenance.get(
            "total_experimental_points"
        )
        != 33
    ):
        raise ValueError(
            "Expected 33 Figure 2.22 points."
        )

    if (
        duplicate_policy.get("status")
        != "duplicate_policy_locked"
    ):
        raise ValueError(
            "Duplicate policy must be locked."
        )

    result = {
        "source_id": SOURCE_ID,

        "figure_ref": "2.22",

        "audit_version": "v2",

        "supersedes_interpretation_from": (
            str(resolution_v1_path)
        ),

        "important_correction": (
            "Figure legend labels must not "
            "automatically be interpreted as "
            "publication identities. Several "
            "labels represent experiment, "
            "dataset, material-source, or "
            "supplier categories."
        ),

        "series_roles": {

            "bass": {
                "label": "BASS",

                "point_count": 4,

                "role": (
                    "experiment_program_dataset"
                ),

                "identity": "BASS-II",

                "gravity_context": (
                    "microgravity"
                ),

                "publication_identity": None,

                "training_policy": (
                    "comparison_validation_only"
                ),

                "reason": (
                    "Substantial duplicate risk "
                    "with canonical Figure 2.21 "
                    "microgravity observations."
                ),
            },

            "nasa": {
                "label": "NASA",

                "point_count": 3,

                "role": (
                    "pmma_dataset_or_material_"
                    "source_label"
                ),

                "identity_status": (
                    "partially_resolved_from_"
                    "nasa_report_context"
                ),

                "gravity_context": (
                    "normal_gravity"
                ),

                "publication_identity": None,

                "training_policy": (
                    "comparison_validation_only"
                ),

                "reason": (
                    "NASA report context identifies "
                    "NASA-labelled PMMA experiments "
                    "in 1g at San Diego State "
                    "University. Figure 2.22 values "
                    "also overlap canonical "
                    "Figure 2.21 evidence."
                ),
            },

            "astra": {
                "label": "Astra",

                "point_count": 1,

                "role": (
                    "pmma_dataset_or_material_"
                    "source_label"
                ),

                "identity_status": (
                    "partially_resolved_from_"
                    "nasa_report_context"
                ),

                "gravity_context": (
                    "normal_gravity"
                ),

                "publication_identity": None,

                "training_policy": (
                    "comparison_validation_only"
                ),

                "reason": (
                    "NASA report context identifies "
                    "Astra-labelled PMMA experiment "
                    "in 1g at San Diego State "
                    "University."
                ),
            },

            "ridout": {
                "label": "Ridout",

                "point_count": 4,

                "role": (
                    "probable_material_or_"
                    "supplier_source_label"
                ),

                "identity_status": (
                    "probable_but_not_proven"
                ),

                "candidate_identity": (
                    "Ridout Plastics, San Diego"
                ),

                "publication_identity": None,

                "gravity_context": (
                    "unresolved"
                ),

                "training_policy": (
                    "blocked_pending_source_"
                    "role_confirmation"
                ),

                "reason": (
                    "Public evidence shows Ridout "
                    "Plastics was a San Diego "
                    "acrylic/plastics supplier. "
                    "This makes supplier/material-"
                    "source interpretation plausible, "
                    "but Figure 2.22 linkage still "
                    "requires direct report/source "
                    "evidence."
                ),

                "do_not_assume": [
                    "author_name",
                    "publication_identity",
                    "gravity",
                    "oxygen_fraction",
                    "pressure",
                    "flow_velocity",
                ],
            },

            "mrc": {
                "label": "MRC",

                "point_count": 2,

                "role": (
                    "unresolved_legend_label"
                ),

                "identity_status": (
                    "unresolved"
                ),

                "publication_identity": None,

                "gravity_context": (
                    "unresolved"
                ),

                "training_policy": (
                    "blocked_pending_role_resolution"
                ),

                "reason": (
                    "Current evidence does not "
                    "establish whether MRC is a "
                    "material supplier, sample "
                    "source, facility, experiment, "
                    "or publication dataset."
                ),
            },

            "vcf": {
                "label": "VCF",

                "point_count": 5,

                "role": (
                    "unresolved_legend_label"
                ),

                "identity_status": (
                    "unresolved"
                ),

                "publication_identity": None,

                "gravity_context": (
                    "unresolved"
                ),

                "training_policy": (
                    "blocked_pending_role_resolution"
                ),

                "reason": (
                    "Current evidence does not "
                    "establish whether VCF is a "
                    "material supplier, sample "
                    "source, facility, experiment, "
                    "or publication dataset."
                ),
            },

            "fernandez_pello_williams": {
                "label": (
                    "Fernandez-Pello and Williams"
                ),

                "point_count": 14,

                "role": (
                    "external_literature_dataset"
                ),

                "identity_status": (
                    "publication_resolved"
                ),

                "publication_identity": {
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

                "known_from_publication": [
                    (
                        "Flat PMMA surfaces "
                        "were studied."
                    ),
                    (
                        "Flame-spread directions "
                        "ranged from downward "
                        "to horizontal."
                    ),
                    (
                        "Spread-rate measurements "
                        "were reported."
                    ),
                ],

                "exact_figure_222_subset_status": (
                    "unresolved"
                ),

                "training_policy": (
                    "blocked_pending_original_"
                    "paper_subset_audit"
                ),

                "do_not_assume": [
                    (
                        "all 14 points share one "
                        "orientation"
                    ),
                    "exact pressure",
                    "exact oxygen_fraction",
                    "exact sample geometry",
                    "exact experimental grouping",
                ],
            },
        },

        "summary": {
            "experiment_program_labels": [
                "bass"
            ],

            "dataset_or_material_source_labels": [
                "nasa",
                "astra",
            ],

            "probable_material_supplier_labels": [
                "ridout"
            ],

            "unresolved_role_labels": [
                "mrc",
                "vcf",
            ],

            "confirmed_external_literature_labels": [
                "fernandez_pello_williams"
            ],

            "training_ready_series": [],
        },

        "scientific_policy": [
            (
                "Legend label identity and "
                "publication identity are "
                "different concepts."
            ),

            (
                "Unknown legend roles remain "
                "unresolved rather than guessed."
            ),

            (
                "Material supplier/source labels "
                "must not be treated as independent "
                "research studies."
            ),

            (
                "Publication-level provenance "
                "must be separated from sample/"
                "material provenance."
            ),

            (
                "Figure 2.22 remains comparison "
                "evidence until source roles and "
                "conditions are resolved."
            ),
        ],

        "next_action": (
            "Resolve MRC and VCF legend roles "
            "and audit the exact Fernandez-Pello "
            "and Williams plotted subset."
        ),

        "status": (
            "series_role_model_corrected"
        ),
    }

    output_path = (
        curated_dir
        / "figure_2_22_series_roles_v2.json"
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
        "FIGURE 2.22 SERIES ROLE CORRECTION V2"
    )

    print(
        "-------------------------------------"
    )

    print()
    print(
        "BASS:"
    )
    print(
        "  experiment/program dataset"
    )

    print()
    print(
        "NASA:"
    )
    print(
        "  PMMA dataset/material-source label"
    )

    print()
    print(
        "Astra:"
    )
    print(
        "  PMMA dataset/material-source label"
    )

    print()
    print(
        "Ridout:"
    )
    print(
        "  probable material/supplier label"
    )
    print(
        "  publication identity: NOT ASSIGNED"
    )

    print()
    print(
        "MRC:"
    )
    print(
        "  role unresolved"
    )

    print()
    print(
        "VCF:"
    )
    print(
        "  role unresolved"
    )

    print()
    print(
        "Fernandez-Pello & Williams:"
    )
    print(
        "  external literature dataset"
    )
    print(
        "  publication resolved"
    )
    print(
        "  exact plotted subset unresolved"
    )

    print()
    print(
        "Training-ready Figure 2.22 "
        "series: 0"
    )

    print()
    print(
        "STATUS:"
    )
    print(
        "  series_role_model_corrected"
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
        "Previous audit files were NOT deleted."
    )


if __name__ == "__main__":
    main()