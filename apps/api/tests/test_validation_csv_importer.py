from fastapi.testclient import (
    TestClient,
)

from app.main import app


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


def csv_for(
    source_id: str,
) -> str:

    rows = [
        (
            f"R1,{source_id},E1,PMMA,thin_sheet,"
            "200,21,101.325,microgravity,"
            "opposed_flow,50,1.10,0.05,,"
            "test_method,test-reference"
        ),
        (
            f"R2,{source_id},E2,PMMA,thin_sheet,"
            "200,21,101.325,microgravity,"
            "opposed_flow,50,1.11,0.05,,"
            "test_method,test-reference"
        ),
        (
            f"R3,{source_id},E3,PMMA,thin_sheet,"
            "200,21,101.325,microgravity,"
            "opposed_flow,50,1.09,0.05,,"
            "test_method,test-reference"
        ),
    ]

    return (
        HEADER
        + "\n"
        + "\n".join(
            rows
        )
        + "\n"
    )


def payload(
    source_id: str,
):
    return {
        "dataset_id": (
            "TEST-CSV-IMPORT-V0"
        ),
        "dataset_version": "test-v0",
        "source_id": source_id,
        "source_title": (
            "Synthetic parser test"
        ),
        "provenance_reference": (
            "pytest-only"
        ),
        "csv_text": csv_for(
            source_id
        ),
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


def test_ries_import_remains_comparison_only():
    response = client.post(
        ENDPOINT,
        json=payload(
            "RIES-2024-PROCI-105358"
        ),
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data[
            "imported_row_count"
        ]
        == 3
    )

    assert (
        data[
            "import_status"
        ]
        == "comparison_only_source"
    )

    assert (
        data[
            "registry_direct_validation_eligible"
        ]
        is False
    )

    assert (
        data[
            "validation_evaluation"
        ]
        is None
    )


def test_unknown_source_requires_review():
    response = client.post(
        ENDPOINT,
        json=payload(
            "NEW-INDEPENDENT-SOURCE"
        ),
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data[
            "import_status"
        ]
        == "provenance_review_required"
    )

    assert (
        data[
            "source_known"
        ]
        is False
    )


def test_bassii_source_is_rejected():
    response = client.post(
        ENDPOINT,
        json=payload(
            "BHATTACHARJEE-2016-BASSII"
        ),
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data[
            "import_status"
        ]
        == "rejected_non_independent_source"
    )

    assert (
        data[
            "source_independence_status"
        ]
        == "same_campaign_as_training"
    )


def test_missing_required_column_returns_422():
    request = payload(
        "RIES-2024-PROCI-105358"
    )

    request[
        "csv_text"
    ] = (
        "record_id,source_id\n"
        "R1,RIES-2024-PROCI-105358\n"
    )

    response = client.post(
        ENDPOINT,
        json=request,
    )

    assert (
        response.status_code
        == 422
    )


def test_duplicate_record_id_returns_422():
    request = payload(
        "RIES-2024-PROCI-105358"
    )

    request[
        "csv_text"
    ] = (
        HEADER
        + "\n"
        + (
            "R1,RIES-2024-PROCI-105358,E1,"
            "PMMA,thin_sheet,200,21,101.325,"
            "microgravity,opposed_flow,50,"
            "1.10,0.05,,method,reference"
        )
        + "\n"
        + (
            "R1,RIES-2024-PROCI-105358,E2,"
            "PMMA,thin_sheet,200,21,101.325,"
            "microgravity,opposed_flow,50,"
            "1.12,0.05,,method,reference"
        )
        + "\n"
    )

    response = client.post(
        ENDPOINT,
        json=request,
    )

    assert (
        response.status_code
        == 422
    )
