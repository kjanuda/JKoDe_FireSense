import json
import shutil

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routers.recommendation import (
    get_recommendation_service,
)
from app.services.next_experiment_recommendation import (
    NextExperimentRecommendationService,
)


ENDPOINT = "/api/recommendations/next-experiment"


def _write_json(path, data):
    path.write_text(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


@pytest.fixture
def isolated_service(tmp_path):
    source = NextExperimentRecommendationService()
    service = NextExperimentRecommendationService()

    path_attributes = (
        "dataset_path",
        "coverage_path",
        "bayesian_path",
        "decision_path",
    )

    for attribute in path_attributes:
        original_path = getattr(
            source,
            attribute,
        )

        temporary_path = (
            tmp_path
            / original_path.name
        )

        shutil.copy2(
            original_path,
            temporary_path,
        )

        setattr(
            service,
            attribute,
            temporary_path,
        )

    return service


def _request_with_service(service):
    app.dependency_overrides[
        get_recommendation_service
    ] = lambda: service

    try:
        with TestClient(app) as client:
            return client.get(
                ENDPOINT
            )

    finally:
        app.dependency_overrides.pop(
            get_recommendation_service,
            None,
        )


def test_fails_closed_when_coverage_artifact_is_tampered(
    isolated_service,
):
    coverage = json.loads(
        isolated_service
        .coverage_path
        .read_text(
            encoding="utf-8"
        )
    )

    coverage[
        "_tampered_for_test"
    ] = True

    _write_json(
        isolated_service.coverage_path,
        coverage,
    )

    response = _request_with_service(
        isolated_service
    )

    assert response.status_code == 503

    detail = response.json()["detail"]

    assert (
        "Coverage candidate artifact "
        "SHA256 mismatch."
        in detail
    )


def test_fails_closed_when_bayesian_artifact_is_tampered(
    isolated_service,
):
    bayesian = json.loads(
        isolated_service
        .bayesian_path
        .read_text(
            encoding="utf-8"
        )
    )

    bayesian[
        "_tampered_for_test"
    ] = True

    _write_json(
        isolated_service.bayesian_path,
        bayesian,
    )

    response = _request_with_service(
        isolated_service
    )

    assert response.status_code == 503

    detail = response.json()["detail"]

    assert (
        "Bayesian candidate artifact "
        "SHA256 mismatch."
        in detail
    )


def test_fails_closed_when_dataset_is_tampered(
    isolated_service,
):
    current_bytes = (
        isolated_service
        .dataset_path
        .read_bytes()
    )

    isolated_service.dataset_path.write_bytes(
        current_bytes + b"\n"
    )

    response = _request_with_service(
        isolated_service
    )

    assert response.status_code == 503

    detail = response.json()["detail"]

    assert (
        "Frozen baseline dataset "
        "SHA256 mismatch."
        in detail
    )


def test_fails_closed_when_selected_thickness_disagrees_with_bayesian(
    isolated_service,
):
    decision = json.loads(
        isolated_service
        .decision_path
        .read_text(
            encoding="utf-8"
        )
    )

    selected = decision[
        "selected_research_candidate"
    ]

    assert (
        "thickness_um"
        in selected
    ), (
        "Expected thickness_um in "
        "selected_research_candidate. "
        f"Found keys: {list(selected)}"
    )

    selected["thickness_um"] = (
        float(
            selected["thickness_um"]
        )
        + 10.0
    )

    _write_json(
        isolated_service.decision_path,
        decision,
    )

    response = _request_with_service(
        isolated_service
    )

    assert response.status_code == 503

    detail = (
        response
        .json()["detail"]
        .lower()
    )

    assert (
        "selected thickness"
        in detail
    )

    assert (
        "bayesian thickness"
        in detail
    )
