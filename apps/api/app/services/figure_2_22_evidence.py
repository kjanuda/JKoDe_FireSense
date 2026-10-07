from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from app.schemas.figure_2_22_evidence import (
    Figure222DuplicateLinkage,
    Figure222EvidenceRecord,
    Figure222EvidenceResponse,
)


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[4]
)

CURATED_DIR = (
    PROJECT_ROOT
    / "data"
    / "curated"
    / "thin_sheet"
)

DATASET_PATH = (
    CURATED_DIR
    / "figure_2_22_comparison_dataset_v0.jsonl"
)

MANIFEST_PATH = (
    CURATED_DIR
    / "figure_2_22_comparison_dataset_v0_manifest.json"
)

EXPECTED_DATASET_SHA256 = (
    "ee7e7d54b57e2bdcbd9dd4eddbcdf8b9"
    "ad88b9924fcee31a4ad7ddac3aff2a9d"
)

EXPECTED_ROW_COUNT = 33


class Figure222EvidenceError(
    RuntimeError,
):
    pass


class Figure222EvidenceIntegrityError(
    Figure222EvidenceError,
):
    pass


def _sha256(
    path: Path,
) -> str:
    digest = hashlib.sha256()

    with path.open(
        "rb",
    ) as handle:
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


def _load_json(
    path: Path,
) -> dict[str, Any]:
    return json.loads(
        path.read_text(
            encoding="utf-8",
        ),
    )


def _load_jsonl(
    path: Path,
) -> list[dict[str, Any]]:
    rows: list[
        dict[str, Any]
    ] = []

    with path.open(
        "r",
        encoding="utf-8",
    ) as handle:
        for line_number, line in enumerate(
            handle,
            start=1,
        ):
            stripped = line.strip()

            if not stripped:
                continue

            try:
                row = json.loads(
                    stripped,
                )
            except json.JSONDecodeError as exc:
                raise Figure222EvidenceIntegrityError(
                    "Invalid JSONL at "
                    f"line {line_number}."
                ) from exc

            rows.append(
                row,
            )

    return rows


def get_figure_2_22_evidence(
) -> Figure222EvidenceResponse:
    if not DATASET_PATH.exists():
        raise Figure222EvidenceError(
            "Figure 2.22 frozen dataset is missing."
        )

    if not MANIFEST_PATH.exists():
        raise Figure222EvidenceError(
            "Figure 2.22 manifest is missing."
        )


    actual_sha = _sha256(
        DATASET_PATH,
    )

    if (
        actual_sha
        != EXPECTED_DATASET_SHA256
    ):
        raise Figure222EvidenceIntegrityError(
            "Figure 2.22 dataset SHA-256 "
            "does not match the frozen v0 hash."
        )


    manifest = _load_json(
        MANIFEST_PATH,
    )


    if (
        manifest.get(
            "dataset_sha256",
        )
        != actual_sha
    ):
        raise Figure222EvidenceIntegrityError(
            "Figure 2.22 manifest and dataset "
            "hashes do not match."
        )


    if (
        manifest.get(
            "figure_ref",
        )
        != "2.22"
    ):
        raise Figure222EvidenceIntegrityError(
            "Unexpected Figure 2.22 manifest identity."
        )


    if (
        manifest.get(
            "purpose",
        )
        != "comparison_only"
    ):
        raise Figure222EvidenceIntegrityError(
            "Figure 2.22 v0 must remain "
            "comparison-only evidence."
        )


    if (
        manifest.get(
            "scientific_status",
        )
        != (
            "comparison_evidence_not_"
            "independent_external_validation"
        )
    ):
        raise Figure222EvidenceIntegrityError(
            "Unexpected Figure 2.22 "
            "scientific status."
        )


    if manifest.get(
        "theoretical_curves_included",
    ):
        raise Figure222EvidenceIntegrityError(
            "Theory must not be exposed as "
            "experimental Figure 2.22 evidence."
        )


    if (
        manifest.get(
            "training_eligible_count",
        )
        != 0
    ):
        raise Figure222EvidenceIntegrityError(
            "Figure 2.22 contains unexpected "
            "training-eligible evidence."
        )


    if (
        manifest.get(
            "independent_validation_eligible_count",
        )
        != 0
    ):
        raise Figure222EvidenceIntegrityError(
            "Figure 2.22 contains unexpected "
            "independent-validation evidence."
        )


    raw_rows = _load_jsonl(
        DATASET_PATH,
    )


    if len(
        raw_rows,
    ) != EXPECTED_ROW_COUNT:
        raise Figure222EvidenceIntegrityError(
            "Unexpected Figure 2.22 row count: "
            f"{len(raw_rows)}."
        )


    manifest_count = manifest.get(
        "experimental_point_count",
    )

    if (
        manifest_count
        != len(
            raw_rows,
        )
    ):
        raise Figure222EvidenceIntegrityError(
            "Manifest experimental-point count "
            "does not match dataset."
        )


    records: list[
        Figure222EvidenceRecord
    ] = []


    for raw in raw_rows:
        if (
            raw.get(
                "evidence_type",
            )
            != "experimental"
        ):
            raise Figure222EvidenceIntegrityError(
                "Non-experimental evidence found "
                "in Figure 2.22 comparison dataset."
            )


        if raw.get(
            "training_eligible",
        ):
            raise Figure222EvidenceIntegrityError(
                "Training-eligible Figure 2.22 "
                "row detected."
            )


        if raw.get(
            "independent_validation_eligible",
        ):
            raise Figure222EvidenceIntegrityError(
                "Independent-validation Figure 2.22 "
                "row detected."
            )


        if (
            raw.get(
                "evaluation_role",
            )
            != "comparison_only"
        ):
            raise Figure222EvidenceIntegrityError(
                "Figure 2.22 row has unexpected "
                "evaluation role."
            )


        linkage_raw = raw.get(
            "duplicate_linkage",
        )

        linkage = (
            Figure222DuplicateLinkage(
                **linkage_raw,
            )
            if linkage_raw
            else None
        )


        records.append(
            Figure222EvidenceRecord(
                record_id=raw[
                    "record_id"
                ],
                source_id=raw[
                    "source_id"
                ],
                figure_ref="2.22",
                dataset_version="v0",

                series_key=raw[
                    "series_key"
                ],
                series_label=raw[
                    "series_label"
                ],

                series_role=raw.get(
                    "series_role",
                ),

                series_identity=raw.get(
                    "series_identity",
                ),

                identity_status=raw.get(
                    "identity_status",
                ),

                publication_identity=raw.get(
                    "publication_identity",
                ),

                gravity_context=raw.get(
                    "gravity_context",
                ),

                gravity_status=raw.get(
                    "gravity_status",
                ),

                source_family_status=raw.get(
                    "source_family_status",
                ),

                evidence_type="experimental",

                thickness_um=raw[
                    "thickness_um"
                ],

                observed_spread_rate_mm_s=raw[
                    "observed_spread_rate_mm_s"
                ],

                digitization_uncertainty_mm_s=(
                    raw.get(
                        "digitization_uncertainty_mm_s",
                    )
                ),

                digitization_uncertainty_status=raw[
                    "digitization_uncertainty_status"
                ],

                figure_validation_status=raw[
                    "figure_validation_status"
                ],

                training_policy=raw[
                    "training_policy"
                ],

                training_eligible=False,

                evaluation_role="comparison_only",

                independent_validation_eligible=False,

                possible_duplicate_with_existing_evidence=(
                    raw[
                        "possible_duplicate_with_existing_evidence"
                    ]
                ),

                duplicate_linkage=linkage,
            )
        )


    return Figure222EvidenceResponse(
        dataset_name=manifest[
            "dataset_name"
        ],

        dataset_version="v0",

        source_id=manifest[
            "source_id"
        ],

        figure_ref="2.22",

        purpose="comparison_only",

        scientific_status=(
            "comparison_evidence_not_"
            "independent_external_validation"
        ),

        figure_validation_status=manifest[
            "figure_validation_status"
        ],

        experimental_point_count=len(
            records,
        ),

        theoretical_curves_included=False,

        training_eligible_count=0,

        independent_validation_eligible_count=0,

        digitization_uncertainty_status=manifest[
            "digitization_uncertainty_status"
        ],

        dataset_sha256=actual_sha,

        dataset_sha256_verified=True,

        series_counts=manifest[
            "series_counts"
        ],

        gravity_context_counts=manifest[
            "gravity_context_counts"
        ],

        duplicate_linkage_class_counts=manifest[
            "duplicate_linkage_class_counts"
        ],

        guardrails=list(
            manifest[
                "guardrails"
            ]
        ),

        records=records,
    )
