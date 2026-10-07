import hashlib
import json
from pathlib import Path
from typing import Any

from app.schemas.validation_source_registry import (
    ValidationSourceCheckResponse,
    ValidationSourceRegistryEntry,
    ValidationSourceRegistryResponse,
)


class ValidationSourceRegistryError(
    RuntimeError
):
    pass


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[4]
)


REGISTRY_PATH = (
    PROJECT_ROOT
    / "data/manifests/"
      "independent_validation_"
      "source_registry_v0.json"
)


EXPECTED_REGISTRY_SHA256 = (
    "c6302ad47feb44c71a101c14871d76b30db69e5fd1db3d67b3fb8fd45f933ceb"
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


def _load_registry(
) -> dict[str, Any]:

    if not REGISTRY_PATH.exists():
        raise ValidationSourceRegistryError(
            "Independent validation source "
            "registry is missing."
        )

    actual = _sha256(
        REGISTRY_PATH
    )

    if (
        actual
        != EXPECTED_REGISTRY_SHA256
    ):
        raise ValidationSourceRegistryError(
            "Independent validation source "
            "registry integrity verification "
            "failed."
        )

    try:
        registry = json.loads(
            REGISTRY_PATH.read_text(
                encoding="utf-8",
            )
        )
    except Exception as exc:
        raise ValidationSourceRegistryError(
            "Could not parse independent "
            "validation source registry."
        ) from exc


    if (
        registry.get(
            "registry_id"
        )
        != (
            "FIRESENSE-INDEPENDENT-"
            "VALIDATION-SOURCE-REGISTRY-V0"
        )
    ):
        raise ValidationSourceRegistryError(
            "Unexpected validation source "
            "registry identity."
        )


    if (
        registry.get(
            "version"
        )
        != "v0"
    ):
        raise ValidationSourceRegistryError(
            "Unexpected validation source "
            "registry version."
        )


    return registry


def get_validation_source_registry(
) -> ValidationSourceRegistryResponse:

    registry = _load_registry()

    sources = [
        ValidationSourceRegistryEntry(
            **source
        )
        for source
        in registry[
            "sources"
        ]
    ]

    return ValidationSourceRegistryResponse(
        registry_id=registry[
            "registry_id"
        ],

        version=registry[
            "version"
        ],

        registry_sha256=(
            EXPECTED_REGISTRY_SHA256
        ),

        artifact_sha256_verified=True,

        firesense_training_source_ids=list(
            registry[
                "firesense_training_source_ids"
            ]
        ),

        sources=sources,

        guardrails=list(
            registry[
                "guardrails"
            ]
        ),
    )


def check_validation_source(
    source_id: str,
) -> ValidationSourceCheckResponse:

    registry = _load_registry()

    normalized = (
        source_id
        .strip()
        .casefold()
    )

    source = next(
        (
            item
            for item
            in registry[
                "sources"
            ]
            if (
                item[
                    "source_id"
                ]
                .casefold()
                == normalized
            )
        ),
        None,
    )


    if source is None:

        policy = registry[
            "unknown_source_policy"
        ]

        return ValidationSourceCheckResponse(
            source_id=source_id,

            known_source=False,

            independence_status=(
                policy[
                    "required_status"
                ]
            ),

            current_role=(
                "unreviewed_source"
            ),

            direct_validation_eligible=False,

            blocking_reasons=[
                policy[
                    "reason"
                ]
            ],

            registry_sha256=(
                EXPECTED_REGISTRY_SHA256
            ),

            artifact_sha256_verified=True,
        )


    return ValidationSourceCheckResponse(
        source_id=source[
            "source_id"
        ],

        known_source=True,

        independence_status=source[
            "independence_status"
        ],

        current_role=source[
            "current_role"
        ],

        direct_validation_eligible=source[
            "direct_validation_eligible"
        ],

        blocking_reasons=list(
            source[
                "blocking_reasons"
            ]
        ),

        registry_sha256=(
            EXPECTED_REGISTRY_SHA256
        ),

        artifact_sha256_verified=True,
    )
