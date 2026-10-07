import hashlib
import json
import math
from pathlib import Path

import pytest

from app.core.paths import CURATED_DATA_DIR


MODELS_DIR = (
    CURATED_DATA_DIR
    / "thin_sheet"
    / "models"
)

DECISION_PATH = (
    MODELS_DIR
    / "next_experiment_decision_v0.json"
)

COVERAGE_PATH = (
    MODELS_DIR
    / "coverage_next_experiment_candidate_v0.json"
)

BAYESIAN_PATH = (
    MODELS_DIR
    / "bayesian_next_experiment_candidate_v0.json"
)


def sha256_file(
    path: Path,
) -> str:
    hasher = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b"",
        ):
            hasher.update(chunk)

    return hasher.hexdigest()


@pytest.fixture
def decision():
    assert DECISION_PATH.exists()

    return json.loads(
        DECISION_PATH.read_text(
            encoding="utf-8"
        )
    )


def test_decision_status(
    decision,
):
    assert (
        decision["status"]
        == "next_experiment_decision_frozen"
    )

    assert (
        decision["decision_status"]
        == "research_priority_candidate"
    )

    assert (
        decision["approval_status"]
        == "not_approved"
    )

    assert (
        decision["production_ready"]
        is False
    )


def test_decision_uses_figure_221(
    decision,
):
    assert (
        decision[
            "canonical_evidence_figure"
        ]
        == "2.21"
    )

    assert (
        decision[
            "dataset_version"
        ]
        == "v0"
    )


def test_input_artifact_hashes_match(
    decision,
):
    inputs = (
        decision[
            "input_artifacts"
        ]
    )

    assert (
        inputs[
            "coverage_candidate"
        ][
            "sha256"
        ]
        == sha256_file(
            COVERAGE_PATH
        )
    )

    assert (
        inputs[
            "bayesian_candidate"
        ][
            "sha256"
        ]
        == sha256_file(
            BAYESIAN_PATH
        )
    )


def test_coverage_and_bayesian_values_match_sources(
    decision,
):
    coverage = json.loads(
        COVERAGE_PATH.read_text(
            encoding="utf-8"
        )
    )

    bayesian = json.loads(
        BAYESIAN_PATH.read_text(
            encoding="utf-8"
        )
    )

    expected_coverage = float(
        coverage[
            "candidate"
        ][
            "matched_pair"
        ][
            "thickness_um"
        ]
    )

    expected_bayesian = float(
        bayesian[
            "candidate"
        ][
            "thickness_um"
        ]
    )

    agreement = (
        decision[
            "agreement_analysis"
        ]
    )

    assert math.isclose(
        agreement[
            "coverage_thickness_um"
        ],
        expected_coverage,
        rel_tol=1e-12,
        abs_tol=1e-12,
    )

    assert math.isclose(
        agreement[
            "bayesian_thickness_um"
        ],
        expected_bayesian,
        rel_tol=1e-12,
        abs_tol=1e-12,
    )


def test_absolute_difference_is_correct(
    decision,
):
    agreement = (
        decision[
            "agreement_analysis"
        ]
    )

    expected = abs(
        agreement[
            "bayesian_thickness_um"
        ]
        -
        agreement[
            "coverage_thickness_um"
        ]
    )

    assert math.isclose(
        agreement[
            "absolute_difference_um"
        ],
        expected,
        rel_tol=1e-12,
        abs_tol=1e-12,
    )


def test_relative_difference_is_correct(
    decision,
):
    agreement = (
        decision[
            "agreement_analysis"
        ]
    )

    coverage = float(
        agreement[
            "coverage_thickness_um"
        ]
    )

    bayesian = float(
        agreement[
            "bayesian_thickness_um"
        ]
    )

    expected = (
        abs(
            bayesian
            - coverage
        )
        / (
            (
                bayesian
                + coverage
            )
            / 2.0
        )
    )

    assert math.isclose(
        agreement[
            "relative_difference"
        ],
        expected,
        rel_tol=1e-12,
        abs_tol=1e-12,
    )

    assert (
        agreement[
            "within_one_percent"
        ]
        is True
    )


def test_selected_candidate_is_bayesian_candidate(
    decision,
):
    selected = (
        decision[
            "selected_research_candidate"
        ]
    )

    agreement = (
        decision[
            "agreement_analysis"
        ]
    )

    assert math.isclose(
        selected[
            "thickness_um"
        ],
        agreement[
            "bayesian_thickness_um"
        ],
        rel_tol=1e-12,
        abs_tol=1e-12,
    )

    assert (
        selected[
            "selection_source"
        ]
        == (
            "bayesian_next_experiment_"
            "candidate_v0"
        )
    )


def test_selected_candidate_is_near_143_um(
    decision,
):
    thickness = float(
        decision[
            "selected_research_candidate"
        ][
            "thickness_um"
        ]
    )

    assert (
        140.0
        < thickness
        < 146.0
    )


def test_internal_convergence_not_external_validation(
    decision,
):
    evidence = (
        decision[
            "evidence_relationship"
        ]
    )

    assert (
        evidence[
            "shared_canonical_evidence"
        ]
        is True
    )

    assert (
        evidence[
            "independent_validation"
        ]
        is False
    )

    assert (
        evidence[
            "external_validation"
        ]
        == "not_performed"
    )


def test_scientific_guardrails_are_preserved(
    decision,
):
    guardrails = " ".join(
        decision[
            "scientific_guardrails"
        ]
    ).lower()

    assert (
        "not an approved experiment"
        in guardrails
    )

    assert (
        "not an external validation"
        in guardrails
    )

    assert (
        "figure 2.21"
        in guardrails
    )

    assert (
        "not externally calibrated"
        in guardrails
    )