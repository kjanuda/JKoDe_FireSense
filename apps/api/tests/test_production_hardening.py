from types import SimpleNamespace

from fastapi.testclient import (
    TestClient,
)

from app.main import app

from app.services.validation_artifact_freezer import (
    _looks_synthetic,
)


client = TestClient(
    app,
)

ENDPOINT = (
    "/api/evidence/"
    "validation-dataset/import-csv"
)


HEADER = (
    "record_id,source_id,experiment_id,"
    "material,geometry_family,thickness_um,"
    "oxygen_percent,pressure_kpa,"
    "gravity_regime,transport_configuration,"
    "flow_mm_s,observed_spread_rate_mm_s,"
    "experimental_uncertainty_mm_s,"
    "digitization_uncertainty_mm_s,"
    "measurement_method,source_reference"
)


def request(
    csv_text: str,
):
    return {
        "dataset_id": "IMPORT-HARDENING-V0",
        "dataset_version": "v0",

        "source_id": (
            "RIES-2024-PROCI-105358"
        ),

        "source_title": (
            "External scientific source"
        ),

        "provenance_reference": (
            "doi-reference"
        ),

        "csv_text": csv_text,

        "experimental_data_only": True,

        "measurement_quantity": (
            "flame_spread_rate"
        ),

        "measurement_definition_matches": True,

        "cross_calibration_available": False,

        "normal_gravity_transport_equivalence_established": False,

        "uncertainty_or_variability_metadata_preserved": True,

        "digitization_uncertainty_separate": True,

        "experimental_uncertainty_separate": True,

        "model_uncertainty_separate": True,
    }


def test_legitimate_test_campaign_title_is_not_synthetic():
    candidate = SimpleNamespace(
        dataset_id=(
            "ZARM-DROP-TOWER-2026"
        ),

        dataset_version="v1",

        source=SimpleNamespace(
            source_id="ZARM-REAL-001",

            source_title=(
                "PMMA drop tower test campaign"
            ),

            provenance_reference=(
                "published experimental dataset"
            ),
        ),
    )

    assert (
        _looks_synthetic(
            candidate
        )
        is False
    )


def test_explicit_test_fixture_is_synthetic():
    candidate = SimpleNamespace(
        dataset_id=(
            "TEST-SYNTHETIC-V0"
        ),

        dataset_version="test-v0",

        source=SimpleNamespace(
            source_id="TEST-SOURCE",

            source_title=(
                "Synthetic software fixture"
            ),

            provenance_reference=(
                "pytest-only"
            ),
        ),
    )

    assert (
        _looks_synthetic(
            candidate
        )
        is True
    )


def test_non_finite_csv_value_is_rejected():
    csv_text = (
        HEADER
        + "\n"
        + (
            "R1,RIES-2024-PROCI-105358,E1,"
            "PMMA,thin_sheet,200,21,101.325,"
            "microgravity,opposed_flow,50,nan,"
            "0.05,,method,reference"
        )
        + "\n"
    )

    response = client.post(
        ENDPOINT,
        json=request(
            csv_text
        ),
    )

    assert (
        response.status_code
        == 422
    )

    assert (
        "Non-finite"
        in response.json()[
            "detail"
        ]
    )


def test_oversized_csv_payload_is_rejected():
    payload = request(
        "x" * 2_000_001
    )

    response = client.post(
        ENDPOINT,
        json=payload,
    )

    assert (
        response.status_code
        == 422
    )
