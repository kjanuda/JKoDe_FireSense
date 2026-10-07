import hashlib
import json
from pathlib import Path

from app.core.paths import (
    CURATED_DATA_DIR,
)

from app.schemas.evidence_trace import (
    CoefficientDerivationInfo,
    DatasetIntegrityInfo,
    EvidenceRecordSummary,
    ExplainedPredictionResponse,
    PredictionEvidenceTrace,
)

from app.schemas.prediction import (
    FireBehaviorPredictionRequest,
)

from app.services.physics_baseline_predictor import (
    PhysicsBaselinePredictor,
)


DATASET_PATH = (
    CURATED_DATA_DIR
    / "thin_sheet"
    / "baseline_dataset_v0.jsonl"
)

MANIFEST_PATH = (
    CURATED_DATA_DIR
    / "thin_sheet"
    / "baseline_dataset_v0_manifest.json"
)


class PredictionExplainer:

    def __init__(
        self,
        predictor: PhysicsBaselinePredictor,
        dataset_path: Path = DATASET_PATH,
        manifest_path: Path = MANIFEST_PATH,
    ) -> None:

        self.predictor = predictor

        self.dataset_path = (
            dataset_path
        )

        self.manifest_path = (
            manifest_path
        )

        self.manifest = (
            self._load_json(
                self.manifest_path
            )
        )

        self.dataset_rows = (
            self._load_jsonl(
                self.dataset_path
            )
        )

        self.actual_sha256 = (
            self._sha256_file(
                self.dataset_path
            )
        )

        self._validate_artifacts()

    @staticmethod
    def _load_json(
        path: Path,
    ) -> dict:

        if not path.exists():

            raise FileNotFoundError(
                f"Missing required file: "
                f"{path}"
            )

        return json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

    @staticmethod
    def _load_jsonl(
        path: Path,
    ) -> list[dict]:

        if not path.exists():

            raise FileNotFoundError(
                f"Missing required file: "
                f"{path}"
            )

        rows = []

        with path.open(
            "r",
            encoding="utf-8",
        ) as file:

            for line_number, raw_line in enumerate(
                file,
                start=1,
            ):

                line = raw_line.strip()

                if not line:
                    continue

                try:

                    rows.append(
                        json.loads(
                            line
                        )
                    )

                except json.JSONDecodeError as exc:

                    raise ValueError(
                        f"Invalid JSONL at "
                        f"line {line_number}: "
                        f"{exc}"
                    ) from exc

        return rows

    @staticmethod
    def _sha256_file(
        path: Path,
    ) -> str:

        if not path.exists():

            raise FileNotFoundError(
                f"Missing artifact: "
                f"{path}"
            )

        digest = hashlib.sha256()

        with path.open(
            "rb"
        ) as file:

            while True:

                chunk = file.read(
                    1024 * 1024
                )

                if not chunk:
                    break

                digest.update(
                    chunk
                )

        return digest.hexdigest()

    def _verify_current_integrity(
        self,
    ) -> str:

        """
        Verify the frozen dataset on every
        explanation request.

        This prevents a cached service from
        silently continuing after the dataset
        file has been modified on disk.
        """

        expected_sha = str(
            self.manifest[
                "dataset_sha256"
            ]
        )

        current_sha = (
            self._sha256_file(
                self.dataset_path
            )
        )

        if current_sha != expected_sha:

            raise ValueError(
                "Baseline dataset SHA256 "
                "does not match the frozen "
                "manifest. Runtime artifact "
                "integrity check failed."
            )

        return current_sha

    def _validate_artifacts(
        self,
    ) -> None:

        if (
            self.manifest.get(
                "dataset_version"
            )
            != "v0"
        ):

            raise ValueError(
                "Unexpected baseline "
                "dataset version."
            )

        if (
            self.manifest.get(
                "record_count"
            )
            != 13
        ):

            raise ValueError(
                "Expected 13 frozen "
                "baseline records."
            )

        if (
            len(
                self.dataset_rows
            )
            != 13
        ):

            raise ValueError(
                "Frozen dataset does not "
                "contain 13 records."
            )

        expected_sha = str(
            self.manifest[
                "dataset_sha256"
            ]
        )

        if (
            expected_sha
            != self.actual_sha256
        ):

            raise ValueError(
                "Baseline dataset SHA256 "
                "does not match the frozen "
                "manifest. Artifact integrity "
                "check failed."
            )

        for row in (
            self.dataset_rows
        ):

            if (
                row.get(
                    "figure_ref"
                )
                != "2.21"
            ):

                raise ValueError(
                    "Baseline evidence contains "
                    "a non-Figure-2.21 record."
                )

    def _records_for_gravity(
        self,
        gravity_regime: str,
    ) -> list[dict]:

        rows = [
            row
            for row in self.dataset_rows
            if (
                row.get(
                    "gravity_regime"
                )
                == gravity_regime
            )
        ]

        return sorted(
            rows,
            key=lambda row: float(
                row[
                    "thickness_um"
                ]
            ),
        )

    def _summary(
        self,
        row: dict,
    ) -> EvidenceRecordSummary:

        return (
            EvidenceRecordSummary(
                record_id=(
                    row[
                        "record_id"
                    ]
                ),

                source_id=(
                    row.get(
                        "source_id",
                        self.manifest[
                            "source_id"
                        ],
                    )
                ),

                figure_ref=(
                    row[
                        "figure_ref"
                    ]
                ),

                gravity_regime=(
                    row[
                        "gravity_regime"
                    ]
                ),

                thickness_um=float(
                    row[
                        "thickness_um"
                    ]
                ),

                observed_spread_rate_mm_s=float(
                    row[
                        "spread_rate_mm_s"
                    ]
                ),

                digitization_uncertainty_mm_s=float(
                    row[
                        "digitization_uncertainty_mm_s"
                    ]
                ),
            )
        )

    def explain(
        self,
        request: FireBehaviorPredictionRequest,
    ) -> ExplainedPredictionResponse:

        # --------------------------------
        # Runtime integrity gate
        # --------------------------------

        current_sha = (
            self._verify_current_integrity()
        )

        result = (
            self.predictor.predict(
                request
            )
        )

        gravity_rows = (
            self._records_for_gravity(
                request.gravity_regime
            )
        )

        if not gravity_rows:

            raise ValueError(
                "No evidence rows found "
                "for requested gravity regime."
            )

        contributing_records = [
            self._summary(
                row
            )
            for row in gravity_rows
        ]

        nearest_rows = sorted(
            gravity_rows,
            key=lambda row: abs(
                float(
                    row[
                        "thickness_um"
                    ]
                )
                - request.thickness_um
            ),
        )[:3]

        nearest_records = [
            self._summary(
                row
            )
            for row in nearest_rows
        ]

        coefficient_k = float(
            result.model.coefficient_k
        )

        expected_sha = str(
            self.manifest[
                "dataset_sha256"
            ]
        )

        trace = (
            PredictionEvidenceTrace(
                canonical_source_id=(
                    self.manifest[
                        "source_id"
                    ]
                ),

                canonical_figure_ref=(
                    self.manifest[
                        "canonical_evidence_figure"
                    ]
                ),

                gravity_regime=(
                    request.gravity_regime
                ),

                dataset_integrity=(
                    DatasetIntegrityInfo(
                        dataset_name=(
                            self.manifest[
                                "dataset_name"
                            ]
                        ),

                        dataset_version=(
                            self.manifest[
                                "dataset_version"
                            ]
                        ),

                        expected_sha256=(
                            expected_sha
                        ),

                        actual_sha256=(
                            current_sha
                        ),

                        integrity_verified=True,
                    )
                ),

                coefficient_derivation=(
                    CoefficientDerivationInfo(
                        formula=(
                            "V = K / tau"
                        ),

                        coefficient_k=(
                            coefficient_k
                        ),

                        exponent=-1.0,

                        fit_space=(
                            "natural_log"
                        ),

                        derivation=(
                            "K is fitted in natural-log "
                            "space using the geometric "
                            "mean relationship between "
                            "observed spread rate and "
                            "fuel thickness for all "
                            "Figure 2.21 records in the "
                            "selected gravity group."
                        ),

                        contributing_record_count=(
                            len(
                                contributing_records
                            )
                        ),

                        contributing_record_ids=[
                            record.record_id
                            for record
                            in contributing_records
                        ],
                    )
                ),

                nearest_evidence_records=(
                    nearest_records
                ),

                contributing_evidence_records=(
                    contributing_records
                ),

                evidence_policy=[
                    (
                        "Figure 2.21 is the canonical "
                        "modeling evidence for "
                        "Physics Baseline v0."
                    ),
                    (
                        "Every Figure 2.21 record "
                        "within the selected gravity "
                        "group contributes to the "
                        "fitted K coefficient."
                    ),
                    (
                        "Nearest evidence records "
                        "are shown for context only; "
                        "they are not the sole basis "
                        "of the prediction."
                    ),
                    (
                        "Figure 2.19 is retained as "
                        "context/validation evidence "
                        "and is not independently "
                        "weighted in this fit."
                    ),
                    (
                        "Figure 2.22 BASS, NASA, "
                        "and Astra observations are "
                        "comparison/validation only "
                        "because of duplicate risk."
                    ),
                    (
                        "Figure 2.22 unresolved "
                        "external series are not "
                        "used for model fitting."
                    ),
                    (
                        "Theoretical curves are "
                        "never treated as "
                        "experimental training rows."
                    ),
                ],

                uncertainty_state=[
                    (
                        "Digitization uncertainty "
                        "is preserved for every "
                        "experimental record."
                    ),
                    (
                        "Digitization uncertainty "
                        "is not used as statistical "
                        "weight because it is not "
                        "the complete experimental "
                        "uncertainty."
                    ),
                    (
                        "Experimental uncertainty "
                        "has not yet been fully "
                        "quantified."
                    ),
                    (
                        "The descriptive residual "
                        "factor is not a calibrated "
                        "prediction interval."
                    ),
                    (
                        "External validation has "
                        "not yet been performed."
                    ),
                ],

                external_validation_status=(
                    "not_performed"
                ),

                production_ready=False,
            )
        )

        return (
            ExplainedPredictionResponse(
                result=result,
                evidence_trace=trace,
            )
        )