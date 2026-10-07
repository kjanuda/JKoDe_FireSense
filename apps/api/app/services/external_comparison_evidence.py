import hashlib
import json
from pathlib import Path
from typing import Any

from app.schemas.external_comparison_evidence import (
    ExternalComparisonEvidenceResponse,
    ExternalComparisonRecord,
)


class ExternalComparisonEvidenceError(
    RuntimeError
):
    pass


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[4]
)


COMPARISON_PATH = (
    PROJECT_ROOT
    / "data/manifests/"
      "ries_2024_figure4_firesense_comparison_v0.json"
)

COMPATIBILITY_PATH = (
    PROJECT_ROOT
    / "data/manifests/"
      "ries_2024_figure4_validation_compatibility_v1.json"
)

MEASUREMENT_PATH = (
    PROJECT_ROOT
    / "data/manifests/"
      "ries_2024_bassii_measurement_compatibility_v0.json"
)

FLOW_PATH = (
    PROJECT_ROOT
    / "data/manifests/"
      "ries_2024_flow_transport_applicability_v0.json"
)

SCREENING_PATH = (
    PROJECT_ROOT
    / "data/manifests/"
      "independent_validation_source_screening_v0.json"
)

POINTS_PATH = (
    PROJECT_ROOT
    / "data/parsed/external/ries_2024/"
      "figure4_vector_points_v1.jsonl"
)


EXPECTED_HASHES = {
    "comparison": (
        "704388a360a592cb304511f29efb046ba"
        "b4c571d013766ae17b33c4e3040036f"
    ),
    "compatibility": (
        "39594b51280db4e8ee8d98b43f601804"
        "e92492663fc447205b7dee7d6aa0cc24"
    ),
    "measurement": (
        "a722cd84b0f453ffafb8bb709e7880a2"
        "5c1d2045c7b9a98493e5010c8dfea009"
    ),
    "flow_transport": (
        "bee2baea33fbaf3b59c5c002ef4aa9d8"
        "3027ee84396c23147cc786d8084013a7"
    ),
    "source_screening": (
        "96ba875285756f03df3a582cd89e16d77"
        "695baf9b9eae8553762e8a449d8b484"
    ),
    "vector_points": (
        "8d31ad600a5b933a4b5756978617384d2"
        "c78e4d5697e34a8cb6f8121682ac34c"
    ),
}


def _sha256(
    path: Path,
) -> str:
    digest = hashlib.sha256()

    with path.open(
        "rb",
    ) as handle:
        for chunk in iter(
            lambda: handle.read(
                1024 * 1024
            ),
            b"",
        ):
            digest.update(
                chunk
            )

    return digest.hexdigest()


def _load_json(
    path: Path,
) -> dict[str, Any]:
    if not path.exists():
        raise ExternalComparisonEvidenceError(
            f"Required evidence artifact "
            f"is missing: {path}"
        )

    try:
        return json.loads(
            path.read_text(
                encoding="utf-8",
            )
        )
    except Exception as exc:
        raise ExternalComparisonEvidenceError(
            f"Could not parse evidence artifact: "
            f"{path}"
        ) from exc


def _verify_hash(
    name: str,
    path: Path,
) -> str:
    if not path.exists():
        raise ExternalComparisonEvidenceError(
            f"Required evidence artifact "
            f"is missing: {path}"
        )

    actual = _sha256(
        path
    )

    expected = EXPECTED_HASHES[
        name
    ]

    if actual != expected:
        raise ExternalComparisonEvidenceError(
            f"Integrity verification failed "
            f"for {name}. "
            f"Expected {expected}, "
            f"got {actual}."
        )

    return actual


def get_external_comparison_evidence(
) -> ExternalComparisonEvidenceResponse:

    paths = {
        "comparison": COMPARISON_PATH,
        "compatibility": COMPATIBILITY_PATH,
        "measurement": MEASUREMENT_PATH,
        "flow_transport": FLOW_PATH,
        "source_screening": SCREENING_PATH,
        "vector_points": POINTS_PATH,
    }

    verified_hashes = {
        name: _verify_hash(
            name,
            path,
        )
        for name, path
        in paths.items()
    }

    comparison = _load_json(
        COMPARISON_PATH
    )

    compatibility = _load_json(
        COMPATIBILITY_PATH
    )

    measurement = _load_json(
        MEASUREMENT_PATH
    )

    flow = _load_json(
        FLOW_PATH
    )

    screening = _load_json(
        SCREENING_PATH
    )


    # ---------------------------------
    # Fail-closed scientific assertions
    # ---------------------------------

    interpretation = comparison[
        "interpretation"
    ]

    if (
        interpretation[
            "independent_external_source"
        ]
        is not True
    ):
        raise ExternalComparisonEvidenceError(
            "External source independence "
            "was not confirmed."
        )

    if (
        interpretation[
            "numeric_comparison_available"
        ]
        is not True
    ):
        raise ExternalComparisonEvidenceError(
            "Numeric external comparison "
            "is not available."
        )

    if (
        interpretation[
            "direct_external_validation_ready"
        ]
        is not False
    ):
        raise ExternalComparisonEvidenceError(
            "Unexpected validation state."
        )

    if (
        compatibility[
            "summary"
        ][
            "direct_validation_eligible_count"
        ]
        != 0
    ):
        raise ExternalComparisonEvidenceError(
            "Compatibility artifact contains "
            "unexpected validation-eligible rows."
        )

    if (
        measurement[
            "validation_policy"
        ][
            "measurement_definition_exact_match"
        ]
        is not False
    ):
        raise ExternalComparisonEvidenceError(
            "Unexpected measurement-definition "
            "exact-match state."
        )

    if (
        flow[
            "correction_policy"
        ][
            "apply_flow_correction_to_"
            "ries_21_percent"
        ]
        is not False
    ):
        raise ExternalComparisonEvidenceError(
            "Unexpected flow-correction state."
        )

    if (
        flow[
            "validation_decision"
        ][
            "direct_external_validation_"
            "with_ries_figure4"
        ]
        is not False
    ):
        raise ExternalComparisonEvidenceError(
            "Ries Figure 4 must remain "
            "comparison-only."
        )

    screening_summary = screening[
        "screening_summary"
    ]

    if (
        screening_summary[
            "exact_independent_validation_sources"
        ]
        != 0
    ):
        raise ExternalComparisonEvidenceError(
            "Unexpected exact-validation "
            "source count."
        )


    # ---------------------------------
    # Comparison records
    # ---------------------------------

    records = [
        ExternalComparisonRecord(
            gravity_context=item[
                "gravity_context"
            ],
            external_record_id=item[
                "external_record_id"
            ],
            thickness_um=item[
                "thickness_um"
            ],
            firesense_v0_rate_mm_s=item[
                "firesense_v0_rate_mm_s"
            ],
            ries_2024_rate_mm_s=item[
                "ries_2024_rate_mm_s"
            ],
            external_minus_model_mm_s=item[
                "external_minus_model_mm_s"
            ],
            relative_gap_vs_model_percent=item[
                "relative_gap_vs_model_percent"
            ],
            relative_gap_vs_external_percent=item[
                "relative_gap_vs_external_percent"
            ],
            comparison_status=item[
                "comparison_status"
            ],
            direct_validation_eligible=False,
        )
        for item
        in comparison[
            "comparisons"
        ]
    ]


    blockers = list(
        compatibility[
            "remaining_blocker_classes"
        ]
    )


    guardrails = [
        (
            "Ries 2024 Figure 4 is independent "
            "external comparison evidence, "
            "not completed external validation."
        ),
        (
            "The Ries microgravity condition "
            "uses 100 mm/s opposed flow while "
            "the BASS-II reference condition "
            "uses 50 mm/s."
        ),
        (
            "FireSense v0 does not model flow "
            "velocity as an input."
        ),
        (
            "BASS-II and Ries propagation-rate "
            "measurements are conceptually "
            "aligned but operationally different."
        ),
        (
            "No empirical flow correction is "
            "applied."
        ),
        (
            "External comparison records are "
            "never training rows."
        ),
        (
            "Independent external validation "
            "is not yet available for the "
            "current release."
        ),
    ]


    return ExternalComparisonEvidenceResponse(
        evidence_id=(
            "EXTVAL-RIES-FIG4-"
            "FIRESENSE-COMP-V0"
        ),
        evidence_version="v0",

        source_name=(
            "Ries, Eigenbrod, Meyer 2024"
        ),
        source_doi=(
            "10.1016/j.proci.2024.105358"
        ),
        figure_ref="4",

        scientific_role=(
            "independent_external_comparison_only"
        ),

        independent_external_source=True,

        numeric_external_comparison_available=True,

        independent_external_validation_available=False,

        direct_external_validation_ready=False,

        training_eligible_count=0,

        independent_validation_eligible_count=0,

        comparison_count=len(
            records
        ),

        measurement_definition_classification=(
            measurement[
                "comparison"
            ][
                "classification"
            ]
        ),

        measurement_definition_exact_match=False,

        flow_condition_match=False,

        flow_correction_allowed=False,

        exact_independent_validation_source_found=False,

        release_validation_status=(
            screening[
                "decision"
            ][
                "current_release_validation_status"
            ]
        ),

        release_comparison_status=(
            screening[
                "decision"
            ][
                "current_release_comparison_status"
            ]
        ),

        blocking_reasons=blockers,

        artifact_sha256=verified_hashes,

        artifact_sha256_verified=True,

        guardrails=guardrails,

        comparisons=records,
    )
