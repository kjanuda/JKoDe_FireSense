import json

import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

ENDPOINT = "/api/recommendations/next-experiment/explain"


def get_response():
    response = client.get(ENDPOINT)
    assert response.status_code == 200
    return response


def test_explanation_endpoint_returns_200():
    response = client.get(ENDPOINT)

    assert response.status_code == 200


def test_explanation_candidate_identity():
    data = get_response().json()

    assert data["candidate_id"] == "NEXTEXP-BAYES-V0-001"
    assert data["decision_status"] == "research_priority_candidate"
    assert data["approval_status"] == "not_approved"
    assert data["production_ready"] is False


def test_explanation_selected_thickness():
    data = get_response().json()

    assert data["thickness_um"] == pytest.approx(
        143.3092934322342
    )

    assert "143.309 um" in data["title"]


def test_explanation_summary_wording():
    data = get_response().json()

    summary = data["summary"]

    assert "143.309 um" in summary
    assert "separate coverage-gap heuristic" in summary

    assert (
        "independent coverage-gap heuristic"
        not in summary
    )

    assert (
        "research-priority candidate"
        in summary
    )


def test_explanation_why_this_thickness():
    data = get_response().json()

    reasons = data["why_this_thickness"]

    assert len(reasons) == 4

    assert (
        "highest modeled joint posterior uncertainty"
        in reasons[0]
    )

    assert "142.557 um" in reasons[1]
    assert "0.526%" in reasons[2]

    assert (
        "method uses evidence spacing only"
        in reasons[3]
    )


def test_explanation_decision_trace():
    data = get_response().json()

    trace = data["decision_trace"]

    assert len(trace) == 5

    assert [
        item["order"]
        for item in trace
    ] == [1, 2, 3, 4, 5]

    assert [
        item["stage"]
        for item in trace
    ] == [
        "evidence",
        "coverage",
        "bayesian",
        "agreement",
        "decision",
    ]


def test_explanation_uncertainty():
    data = get_response().json()

    uncertainty = data["uncertainty"]

    assert (
        uncertainty[
            "microgravity_posterior_sd_log_residual"
        ]
        == pytest.approx(
            0.2901885957642983
        )
    )

    assert (
        uncertainty[
            "normal_gravity_posterior_sd_log_residual"
        ]
        == pytest.approx(
            0.0775430128597582
        )
    )

    assert (
        uncertainty[
            "matched_pair_joint_sd_log"
        ]
        == pytest.approx(
            0.30037033800797297
        )
    )

    assert (
        uncertainty["calibration_status"]
        == "not_externally_calibrated"
    )


def test_explanation_evidence_provenance():
    data = get_response().json()

    evidence = data["evidence"]

    assert (
        evidence["source_id"]
        == "SRC-NASA-20210011385"
    )

    assert evidence["figure"] == "2.21"
    assert evidence["dataset_version"] == "v0"

    assert (
        evidence["dataset_sha256"]
        == (
            "4024475ca9f0bf5d703ce1cb375e6d9e"
            "11897ead4dfc3f5e0fe6369879798ab4"
        )
    )

    assert (
        evidence["shared_canonical_evidence"]
        is True
    )

    assert (
        evidence["independent_validation"]
        is False
    )

    assert (
        evidence["external_validation"]
        == "not_performed"
    )

    assert (
        evidence["interpretation"]
        == (
            "The coverage and Bayesian results share "
            "the same frozen Figure 2.21 evidence base. "
            "Their agreement is internal convergence "
            "and must not be described as independent "
            "or external validation."
        )
    )


def test_explanation_has_no_malformed_text():
    data = get_response().json()

    blob = json.dumps(
        data,
        ensure_ascii=False,
    )

    malformed_patterns = [
        "Âµm",
        "143.309um",
        "methoduses",
        "GPlog-space",
        "resultsshare",
        "describedas",
        "nota calibrated",
        "independent coverage-gap",
    ]

    for pattern in malformed_patterns:
        assert pattern not in blob


def test_explanation_preserves_scientific_guardrails():
    data = get_response().json()

    caveats = data["scientific_caveats"]
    requirements = (
        data[
            "required_before_experiment_approval"
        ]
    )

    assert len(caveats) >= 8
    assert len(requirements) >= 6

    assert any(
        "not an approved experiment"
        in item
        for item in caveats
    )

    assert any(
        "not externally calibrated"
        in item
        for item in caveats
    )

    assert any(
        "cabin-fire probability"
        in item
        for item in caveats
    )

    assert any(
        "scientific and safety review"
        in item.lower()
        for item in requirements
    )
