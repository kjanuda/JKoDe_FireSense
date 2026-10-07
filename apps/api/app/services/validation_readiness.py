import hashlib
import json
from pathlib import Path
from typing import Any

from app.schemas.validation_readiness import (
    MinimumValidationScope,
    ValidationReadinessResponse,
    ValidationTarget,
)


class ValidationReadinessError(
    RuntimeError
):
    pass


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[4]
)


ACCEPTANCE_PATH = (
    PROJECT_ROOT
    / "data/manifests/"
      "independent_validation_acceptance_criteria_v0.json"
)


SCREENING_PATH = (
    PROJECT_ROOT
    / "data/manifests/"
      "independent_validation_source_screening_v0.json"
)


EXPECTED_ACCEPTANCE_SHA256 = (
    "a3c7a88c3ad52efbb2a3170fd67d5d9219bb25ac7325f3950954dd8962c9e783"
)


EXPECTED_SCREENING_SHA256 = (
    "96ba875285756f03df3a582cd89e16d77695baf9b9eae8553762e8a449d8b484"
)


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
        raise ValidationReadinessError(
            f"Required validation artifact "
            f"is missing: {path}"
        )

    try:
        return json.loads(
            path.read_text(
                encoding="utf-8",
            )
        )
    except Exception as exc:
        raise ValidationReadinessError(
            f"Could not parse validation artifact: "
            f"{path}"
        ) from exc


def _verify_hash(
    path: Path,
    expected: str,
    label: str,
) -> str:
    if not path.exists():
        raise ValidationReadinessError(
            f"Required validation artifact "
            f"is missing: {path}"
        )

    actual = _sha256(
        path
    )

    if actual != expected:
        raise ValidationReadinessError(
            f"Integrity verification failed "
            f"for {label}. "
            f"Expected {expected}, "
            f"got {actual}."
        )

    return actual


def get_validation_readiness(
) -> ValidationReadinessResponse:

    acceptance_sha = _verify_hash(
        ACCEPTANCE_PATH,
        EXPECTED_ACCEPTANCE_SHA256,
        "independent validation acceptance criteria",
    )

    screening_sha = _verify_hash(
        SCREENING_PATH,
        EXPECTED_SCREENING_SHA256,
        "independent validation source screening",
    )

    acceptance = _load_json(
        ACCEPTANCE_PATH
    )

    screening = _load_json(
        SCREENING_PATH
    )


    # ---------------------------------
    # Frozen protocol identity
    # ---------------------------------

    if (
        acceptance[
            "criteria_id"
        ]
        != (
            "FIRESENSE-INDEPENDENT-"
            "VALIDATION-ACCEPTANCE-V0"
        )
    ):
        raise ValidationReadinessError(
            "Unexpected validation "
            "acceptance protocol identity."
        )

    if (
        acceptance[
            "version"
        ]
        != "v0"
    ):
        raise ValidationReadinessError(
            "Unexpected validation "
            "acceptance protocol version."
        )


    # ---------------------------------
    # Target compatibility assertions
    # ---------------------------------

    required = acceptance[
        "required"
    ]

    target = screening[
        "target"
    ]

    if (
        required[
            "material_geometry"
        ][
            "material"
        ]
        != target[
            "material"
        ]
    ):
        raise ValidationReadinessError(
            "Validation material target "
            "does not match protocol."
        )

    if (
        required[
            "material_geometry"
        ][
            "geometry_family"
        ]
        != target[
            "geometry_family"
        ]
    ):
        raise ValidationReadinessError(
            "Validation geometry target "
            "does not match protocol."
        )

    if (
        float(
            required[
                "microgravity_transport"
            ][
                "reference_flow_mm_s"
            ]
        )
        != float(
            target[
                "microgravity_flow_mm_s"
            ]
        )
    ):
        raise ValidationReadinessError(
            "Validation microgravity flow "
            "target does not match protocol."
        )

    if (
        target[
            "independent_campaign_required"
        ]
        is not True
    ):
        raise ValidationReadinessError(
            "Independent campaign requirement "
            "must remain enabled."
        )


    # ---------------------------------
    # Current evidence state
    # ---------------------------------

    summary = screening[
        "screening_summary"
    ]

    decision = screening[
        "decision"
    ]

    ries = acceptance[
        "current_ries_2024_status"
    ]

    release_policy = acceptance[
        "release_policy"
    ]

    if (
        summary[
            "exact_independent_validation_sources"
        ]
        != 0
    ):
        raise ValidationReadinessError(
            "Unexpected exact external "
            "validation source count."
        )

    if (
        summary[
            "exact_source_found_in_current_screening"
        ]
        is not False
    ):
        raise ValidationReadinessError(
            "Unexpected exact-source state."
        )

    if (
        decision[
            "current_release_validation_status"
        ]
        != (
            "independent_external_validation_"
            "not_yet_available"
        )
    ):
        raise ValidationReadinessError(
            "Unexpected current validation "
            "release status."
        )

    if (
        decision[
            "current_release_comparison_status"
        ]
        != (
            "independent_external_comparison_"
            "available"
        )
    ):
        raise ValidationReadinessError(
            "Unexpected current comparison "
            "release status."
        )

    if (
        ries[
            "direct_validation_eligible"
        ]
        is not False
    ):
        raise ValidationReadinessError(
            "Ries 2024 must remain "
            "comparison-only."
        )


    # ---------------------------------
    # Claim-policy assertions
    # ---------------------------------

    if (
        release_policy[
            "production_ready_claim_allowed"
        ]
        is not False
    ):
        raise ValidationReadinessError(
            "Production-ready claim must "
            "remain disabled."
        )

    if (
        release_policy[
            "certification_claim_allowed"
        ]
        is not False
    ):
        raise ValidationReadinessError(
            "Certification claim must "
            "remain disabled."
        )

    if (
        release_policy[
            "comparison_must_not_be_labeled_validation"
        ]
        is not True
    ):
        raise ValidationReadinessError(
            "Comparison/validation separation "
            "guardrail was disabled."
        )


    minimum_scope = acceptance[
        "minimum_validation_scope"
    ]


    guardrails = [
        (
            "Independent external comparison "
            "must not be labelled independent "
            "external validation."
        ),
        (
            "At least three compatible "
            "independent numeric points are "
            "required before FireSense labels "
            "the model externally validated."
        ),
        (
            "Validation evidence must remain "
            "holdout and must never become "
            "FireSense training evidence."
        ),
        (
            "The microgravity validation target "
            "uses 50 mm/s opposed flow."
        ),
        (
            "Measurement definitions must match "
            "or be supported by empirical "
            "cross-calibration."
        ),
        (
            "Digitization, experimental and "
            "model uncertainty must remain "
            "separate."
        ),
        (
            "Production-ready and certification "
            "claims remain disabled."
        ),
    ]


    return ValidationReadinessResponse(
        readiness_id=(
            "FIRESENSE-VALIDATION-"
            "READINESS-V0"
        ),

        version="v0",

        validation_protocol_id=acceptance[
            "criteria_id"
        ],

        scientific_status=decision[
            "current_release_validation_status"
        ],

        independent_external_validation_available=False,

        independent_external_comparison_available=True,

        exact_source_found=False,

        exact_validation_source_count=0,

        screened_candidate_count=summary[
            "candidate_count"
        ],

        independent_comparison_source_count=summary[
            "independent_comparison_sources"
        ],

        target=ValidationTarget(
            material=target[
                "material"
            ],
            geometry_family=target[
                "geometry_family"
            ],
            thickness_um=target[
                "thickness_um"
            ],
            oxygen_percent=target[
                "oxygen_percent"
            ],
            pressure_kpa=target[
                "pressure_kpa"
            ],
            microgravity_configuration=target[
                "microgravity_configuration"
            ],
            microgravity_flow_mm_s=target[
                "microgravity_flow_mm_s"
            ],
            independent_campaign_required=target[
                "independent_campaign_required"
            ],
        ),

        minimum_validation_scope=MinimumValidationScope(
            independent_source_count=minimum_scope[
                "independent_source_count"
            ],
            minimum_independent_numeric_points=minimum_scope[
                "minimum_independent_numeric_points"
            ],
            note=minimum_scope[
                "note"
            ],
        ),

        ries_2024_classification=ries[
            "classification"
        ],

        ries_2024_direct_validation_eligible=False,

        ries_2024_blocking_reasons=list(
            ries[
                "blocking_reasons"
            ]
        ),

        production_ready_claim_allowed=False,

        certification_claim_allowed=False,

        acceptance_criteria_sha256=acceptance_sha,

        source_screening_sha256=screening_sha,

        artifact_sha256_verified=True,

        guardrails=guardrails,
    )
