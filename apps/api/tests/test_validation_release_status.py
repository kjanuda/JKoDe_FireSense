from pathlib import Path

import pytest

from fastapi.testclient import (
    TestClient,
)

from app.main import app

from app.schemas.validation_candidate import (
    ValidationCandidateRequest,
)

from app.services.validation_artifact_freezer import (
    ValidationArtifactFreezeError,
    freeze_validation_candidate,
)


client = TestClient(
    app,
)


def test_release_status_is_fail_closed_without_real_artifact():
    response = client.get(
        "/api/evidence/"
        "validation-release-status"
    )

    assert (
        response.status_code
        == 200
    )

    data = response.json()

    assert (
        data[
            "scientific_status"
        ]
        == (
            "independent_external_validation_"
            "not_yet_available"
        )
    )

    assert (
        data[
            "independent_external_validation_available"
        ]
        is False
    )

    assert (
        data[
            "production_ready_claim_allowed"
        ]
        is False
    )

    assert (
        data[
            "certification_claim_allowed"
        ]
        is False
    )


def test_synthetic_candidate_cannot_be_frozen(
    tmp_path: Path,
):
    candidate = ValidationCandidateRequest(
        dataset_id=(
            "TEST-SYNTHETIC-"
            "VALIDATION"
        ),
        dataset_version="test-v0",

        source={
            "source_id": "TEST-SOURCE",
            "source_title": (
                "Synthetic software fixture"
            ),
            "provenance_reference": (
                "pytest-only"
            ),
            "independent_publication_or_dataset": True,
            "independent_experimental_campaign": True,
            "not_firesense_training_source": True,
            "not_reused_bass_ii_rows": True,
            "experimental_data_only": True,
            "measurement_quantity": (
                "flame_spread_rate"
            ),
            "measurement_definition_matches": True,
            "cross_calibration_available": False,
            "normal_gravity_transport_equivalence_established": True,
            "uncertainty_or_variability_metadata_preserved": True,
            "digitization_uncertainty_separate": True,
            "experimental_uncertainty_separate": True,
            "model_uncertainty_separate": True,
        },

        records=[
            {
                "record_id": "ROW-001",
                "material": "PMMA",
                "geometry_family": "thin_sheet",
                "thickness_um": 150.0,
                "oxygen_percent": 21.0,
                "pressure_kpa": 101.325,
                "gravity_regime": "microgravity",
                "transport_configuration": "opposed_flow",
                "flow_mm_s": 50.0,
                "observed_spread_rate_mm_s": 1.36,
                "training_eligible": False,
                "validation_holdout": True,
                "provenance_reference": "pytest-row",
            },
            {
                "record_id": "ROW-002",
                "material": "PMMA",
                "geometry_family": "thin_sheet",
                "thickness_um": 200.0,
                "oxygen_percent": 21.0,
                "pressure_kpa": 101.325,
                "gravity_regime": "microgravity",
                "transport_configuration": "opposed_flow",
                "flow_mm_s": 50.0,
                "observed_spread_rate_mm_s": 1.02,
                "training_eligible": False,
                "validation_holdout": True,
                "provenance_reference": "pytest-row",
            },
            {
                "record_id": "ROW-003",
                "material": "PMMA",
                "geometry_family": "thin_sheet",
                "thickness_um": 300.0,
                "oxygen_percent": 21.0,
                "pressure_kpa": 101.325,
                "gravity_regime": "microgravity",
                "transport_configuration": "opposed_flow",
                "flow_mm_s": 50.0,
                "observed_spread_rate_mm_s": 0.68,
                "training_eligible": False,
                "validation_holdout": True,
                "provenance_reference": "pytest-row",
            },
        ],
    )

    with pytest.raises(
        ValidationArtifactFreezeError,
        match=(
            "Synthetic/test candidate data"
        ),
    ):
        freeze_validation_candidate(
            candidate,
            tmp_path,
        )


def test_release_status_endpoint_is_registered():
    paths = app.openapi()[
        "paths"
    ]

    assert (
        "/api/evidence/"
        "validation-release-status"
        in paths
    )
