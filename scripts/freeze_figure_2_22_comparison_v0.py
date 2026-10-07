from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(r"E:\Nasa\FireSense")

CURATED = (
    ROOT
    / "data"
    / "curated"
    / "thin_sheet"
)

PROVENANCE_PATH = (
    CURATED
    / "figure_2_22_provenance_audit_v0.json"
)

ROLES_PATH = (
    CURATED
    / "figure_2_22_series_roles_v2.json"
)

DUPLICATE_PATH = (
    CURATED
    / "figure_2_22_duplicate_linkage_audit_v1.json"
)

OUT_DATASET = (
    CURATED
    / "figure_2_22_comparison_dataset_v0.jsonl"
)

OUT_MANIFEST = (
    CURATED
    / "figure_2_22_comparison_dataset_v0_manifest.json"
)


def load_json(
    path: Path,
) -> dict[str, Any]:
    return json.loads(
        path.read_text(
            encoding="utf-8",
        ),
    )


def file_sha256(
    path: Path,
) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(
                1024 * 1024,
            ),
            b"",
        ):
            digest.update(
                chunk,
            )

    return digest.hexdigest()


def normalize_series_key(
    value: str,
) -> str:
    return (
        value
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
    )


provenance = load_json(
    PROVENANCE_PATH,
)

roles = load_json(
    ROLES_PATH,
)

duplicates = load_json(
    DUPLICATE_PATH,
)


# --------------------------------------------------
# Scientific guardrails
# --------------------------------------------------

if (
    provenance.get(
        "figure_ref",
    )
    != "2.22"
):
    raise RuntimeError(
        "Unexpected provenance figure_ref."
    )


if (
    provenance.get(
        "figure_validation_status",
    )
    != "human_overlay_verified"
):
    raise RuntimeError(
        "Figure 2.22 is not human-overlay verified."
    )


if provenance.get(
    "theoretical_curves_included",
):
    raise RuntimeError(
        "Theory must not enter the experimental comparison dataset."
    )


expected_count = int(
    provenance.get(
        "total_experimental_points",
        0,
    ),
)

if expected_count != 33:
    raise RuntimeError(
        f"Expected 33 experimental points, got {expected_count}."
    )


series_roles = (
    roles.get(
        "series_roles",
        {},
    )
)


duplicate_map: dict[
    str,
    dict[str, Any],
] = {}

for item in duplicates.get(
    "comparisons",
    [],
):
    point_id = item.get(
        "figure_2_22_point_id",
    )

    if point_id:
        duplicate_map[
            str(point_id)
        ] = item


records: list[
    dict[str, Any]
] = []


for raw_series_key, series in (
    provenance.get(
        "series",
        {},
    ).items()
):
    series_key = normalize_series_key(
        raw_series_key,
    )

    role = series_roles.get(
        series_key,
        {},
    )

    label = (
        role.get(
            "label",
        )
        or series.get(
            "label",
        )
        or raw_series_key
    )

    points = series.get(
        "points",
        [],
    )


    declared_count = series.get(
        "point_count",
    )

    if (
        declared_count is not None
        and int(
            declared_count,
        )
        != len(
            points,
        )
    ):
        raise RuntimeError(
            "Point-count mismatch for "
            f"{series_key}: "
            f"declared={declared_count}, "
            f"actual={len(points)}"
        )


    for index, point in enumerate(
        points,
        start=1,
    ):
        point_id = (
            f"F222-"
            f"{series_key.upper()}-"
            f"{index:03d}"
        )

        duplicate = duplicate_map.get(
            point_id,
        )


        gravity_context = role.get(
            "gravity_context",
        )

        training_policy = role.get(
            "training_policy",
        )

        # Figure 2.22 remains comparison evidence only
        # in v0. No row becomes training evidence here.
        training_eligible = False

        # Do not call any Figure 2.22 row independent
        # external validation until source identity,
        # conditions and run linkage are proven.
        independent_validation_eligible = False


        record = {
            "record_id": point_id,

            "source_id": provenance[
                "source_id"
            ],

            "figure_ref": "2.22",

            "dataset_version": "v0",

            "series_key": series_key,

            "series_label": label,

            "series_role": role.get(
                "role",
            ),

            "series_identity": role.get(
                "identity",
            ),

            "identity_status": (
                role.get(
                    "identity_status",
                )
                or series.get(
                    "identity_status",
                )
            ),

            "publication_identity": (
                role.get(
                    "publication_identity",
                )
            ),

            "gravity_context": (
                gravity_context
            ),

            "gravity_status": (
                series.get(
                    "gravity_status",
                )
            ),

            "source_family_status": (
                series.get(
                    "source_family_status",
                )
            ),

            "evidence_type": (
                series.get(
                    "evidence_type",
                    "experimental",
                )
            ),

            "thickness_um": float(
                point[
                    "thickness_um"
                ],
            ),

            "observed_spread_rate_mm_s": float(
                point[
                    "spread_rate_mm_s"
                ],
            ),

            "pixel_x": point.get(
                "pixel_x",
            ),

            "pixel_y": point.get(
                "pixel_y",
            ),

            # Figure-specific quantitative
            # digitization uncertainty has not
            # been established in this v0 freeze.
            "digitization_uncertainty_mm_s": None,

            "digitization_uncertainty_status":
                "not_quantified_for_figure_2_22_v0",

            "figure_validation_status": (
                provenance[
                    "figure_validation_status"
                ]
            ),

            "training_policy": (
                training_policy
                or "comparison_only"
            ),

            "training_eligible":
                training_eligible,

            "evaluation_role":
                "comparison_only",

            "independent_validation_eligible":
                independent_validation_eligible,

            "possible_duplicate_with_existing_evidence":
                bool(
                    series.get(
                        "possible_duplicate_with_existing_evidence",
                        False,
                    ),
                ),

            "duplicate_linkage": (
                None
                if duplicate is None
                else {
                    "matched_figure_2_21_record_id":
                        duplicate.get(
                            "matched_figure_2_21_record_id",
                        ),

                    "classification":
                        duplicate.get(
                            "classification",
                        ),

                    "relationship_status":
                        duplicate.get(
                            "relationship_status",
                        ),

                    "same_run_confirmed":
                        bool(
                            duplicate.get(
                                "same_run_confirmed",
                                False,
                            ),
                        ),

                    "safe_for_training_join":
                        bool(
                            duplicate.get(
                                "safe_for_training_join",
                                False,
                            ),
                        ),
                }
            ),

            "series_notes": series.get(
                "notes",
                [],
            ),

            "role_reason": role.get(
                "reason",
            ),
        }


        if (
            record[
                "evidence_type"
            ]
            != "experimental"
        ):
            raise RuntimeError(
                "Non-experimental row encountered: "
                f"{point_id}"
            )


        records.append(
            record,
        )


# --------------------------------------------------
# Dataset validation
# --------------------------------------------------

if len(
    records,
) != expected_count:
    raise RuntimeError(
        "Frozen row count does not match "
        f"provenance audit: "
        f"{len(records)} != {expected_count}"
    )


ids = [
    row[
        "record_id"
    ]
    for row in records
]

if len(
    ids,
) != len(
    set(
        ids,
    )
):
    raise RuntimeError(
        "Duplicate Figure 2.22 record IDs."
    )


if any(
    row[
        "training_eligible"
    ]
    for row in records
):
    raise RuntimeError(
        "Figure 2.22 v0 must contain "
        "zero training-eligible rows."
    )


if any(
    row[
        "independent_validation_eligible"
    ]
    for row in records
):
    raise RuntimeError(
        "Figure 2.22 v0 must contain "
        "zero independently validated rows."
    )


# Stable ordering
records.sort(
    key=lambda row: (
        row[
            "series_key"
        ],
        row[
            "thickness_um"
        ],
        row[
            "record_id"
        ],
    ),
)


with OUT_DATASET.open(
    "w",
    encoding="utf-8",
    newline="\n",
) as handle:
    for record in records:
        handle.write(
            json.dumps(
                record,
                ensure_ascii=False,
                sort_keys=True,
                separators=(
                    ",",
                    ":",
                ),
            )
        )

        handle.write(
            "\n",
        )


dataset_sha = file_sha256(
    OUT_DATASET,
)


series_counts = Counter(
    row[
        "series_key"
    ]
    for row in records
)


gravity_counts = Counter(
    (
        row[
            "gravity_context"
        ]
        or "unresolved"
    )
    for row in records
)


duplicate_class_counts = Counter()

for row in records:
    linkage = row[
        "duplicate_linkage"
    ]

    if linkage:
        classification = linkage.get(
            "classification",
        )

        if classification:
            duplicate_class_counts[
                classification
            ] += 1


manifest = {
    "dataset_name":
        "figure_2_22_comparison_dataset_v0",

    "dataset_version":
        "v0",

    "source_id":
        provenance[
            "source_id"
        ],

    "figure_ref":
        "2.22",

    "purpose":
        "comparison_only",

    "scientific_status":
        "comparison_evidence_not_independent_external_validation",

    "figure_validation_status":
        provenance[
            "figure_validation_status"
        ],

    "experimental_point_count":
        len(
            records,
        ),

    "theoretical_curves_included":
        False,

    "training_eligible_count":
        0,

    "independent_validation_eligible_count":
        0,

    "digitization_uncertainty_status":
        "not_quantified_for_figure_2_22_v0",

    "series_counts":
        dict(
            sorted(
                series_counts.items(),
            ),
        ),

    "gravity_context_counts":
        dict(
            sorted(
                gravity_counts.items(),
            ),
        ),

    "duplicate_linkage_class_counts":
        dict(
            sorted(
                duplicate_class_counts.items(),
            ),
        ),

    "dataset_sha256":
        dataset_sha,

    "input_artifacts": {
        PROVENANCE_PATH.name: {
            "sha256":
                file_sha256(
                    PROVENANCE_PATH,
                ),
        },

        ROLES_PATH.name: {
            "sha256":
                file_sha256(
                    ROLES_PATH,
                ),
        },

        DUPLICATE_PATH.name: {
            "sha256":
                file_sha256(
                    DUPLICATE_PATH,
                ),
        },
    },

    "guardrails": [
        "Figure 2.22 experimental points are not added to the Figure 2.21 training dataset.",
        "BASS, NASA and Astra numerical overlap does not prove independent experiments.",
        "Series labels are not automatically treated as publication identities.",
        "Unresolved source identity or experimental conditions block independent-validation claims.",
        "Theory is excluded from this dataset.",
        "Figure 2.22 digitization uncertainty is not borrowed from Figure 2.21.",
    ],
}


OUT_MANIFEST.write_text(
    json.dumps(
        manifest,
        indent=2,
        ensure_ascii=False,
    )
    + "\n",
    encoding="utf-8",
)


print()
print(
    "Figure 2.22 comparison dataset frozen."
)
print(
    f"Rows: {len(records)}"
)
print(
    f"Training eligible: "
    f"{sum(row['training_eligible'] for row in records)}"
)
print(
    "Independent validation eligible: "
    f"{sum(row['independent_validation_eligible'] for row in records)}"
)
print(
    f"Dataset SHA-256: {dataset_sha}"
)
print()
print(
    f"Dataset: {OUT_DATASET}"
)
print(
    f"Manifest: {OUT_MANIFEST}"
)
print()
print(
    "Series counts:"
)

for key, value in sorted(
    series_counts.items(),
):
    print(
        f"  {key}: {value}"
    )
