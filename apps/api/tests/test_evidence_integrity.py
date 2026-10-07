import shutil

import pytest

from app.core.paths import (
    CURATED_DATA_DIR,
)

from app.schemas.prediction import (
    FireBehaviorPredictionRequest,
)

from app.services.physics_baseline_predictor import (
    PhysicsBaselinePredictor,
)

from app.services.prediction_explainer import (
    PredictionExplainer,
)


SOURCE_DATASET = (
    CURATED_DATA_DIR
    / "thin_sheet"
    / "baseline_dataset_v0.jsonl"
)

SOURCE_MANIFEST = (
    CURATED_DATA_DIR
    / "thin_sheet"
    / "baseline_dataset_v0_manifest.json"
)


def valid_request():
    return (
        FireBehaviorPredictionRequest(
            material="PMMA",
            geometry="thin_sheet",
            thickness_um=200.0,
            gravity_regime="microgravity",
            oxygen_fraction=0.21,
            pressure_kpa=101.325,
        )
    )


def test_tampered_dataset_rejected_at_initialization(
    tmp_path,
):

    dataset_path = (
        tmp_path
        / "baseline_dataset_v0.jsonl"
    )

    manifest_path = (
        tmp_path
        / "baseline_dataset_v0_manifest.json"
    )

    shutil.copy2(
        SOURCE_DATASET,
        dataset_path,
    )

    shutil.copy2(
        SOURCE_MANIFEST,
        manifest_path,
    )

    with dataset_path.open(
        "a",
        encoding="utf-8",
    ) as file:

        file.write(
            "\n"
        )

        file.write(
            " "
        )

    predictor = (
        PhysicsBaselinePredictor()
    )

    with pytest.raises(
        ValueError,
        match="SHA256",
    ):

        PredictionExplainer(
            predictor=predictor,
            dataset_path=dataset_path,
            manifest_path=manifest_path,
        )


def test_runtime_tampering_is_detected(
    tmp_path,
):

    dataset_path = (
        tmp_path
        / "baseline_dataset_v0.jsonl"
    )

    manifest_path = (
        tmp_path
        / "baseline_dataset_v0_manifest.json"
    )

    shutil.copy2(
        SOURCE_DATASET,
        dataset_path,
    )

    shutil.copy2(
        SOURCE_MANIFEST,
        manifest_path,
    )

    predictor = (
        PhysicsBaselinePredictor()
    )

    explainer = (
        PredictionExplainer(
            predictor=predictor,
            dataset_path=dataset_path,
            manifest_path=manifest_path,
        )
    )

    first_response = (
        explainer.explain(
            valid_request()
        )
    )

    assert (
        first_response.evidence_trace
        .dataset_integrity
        .integrity_verified
        is True
    )

    # Modify the frozen dataset after
    # the explainer has already loaded.
    with dataset_path.open(
        "a",
        encoding="utf-8",
    ) as file:

        file.write(
            "\n"
        )

    with pytest.raises(
        ValueError,
        match="Runtime artifact integrity",
    ):

        explainer.explain(
            valid_request()
        )