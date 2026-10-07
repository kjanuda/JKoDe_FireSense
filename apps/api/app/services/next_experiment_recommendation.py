import hashlib
import json
import math
from pathlib import Path

from app.core.paths import (
    CURATED_DATA_DIR,
)

from app.schemas.next_experiment_recommendation import (
    AgreementSummary,
    ArtifactIntegritySummary,
    EvidenceSummary,
    ExistingObservationSummary,
    ExperimentFamilySummary,
    GravityRecommendationSummary,
    JointUncertaintySummary,
    NextExperimentRecommendationResponse,
)


class RecommendationIntegrityError(
    RuntimeError
):
    pass


class NextExperimentRecommendationService:

    def __init__(
        self,
    ) -> None:

        self.thin_sheet_dir = (
            CURATED_DATA_DIR
            / "thin_sheet"
        )

        self.models_dir = (
            self.thin_sheet_dir
            / "models"
        )

        self.dataset_path = (
            self.thin_sheet_dir
            / "baseline_dataset_v0.jsonl"
        )

        self.coverage_path = (
            self.models_dir
            / (
                "coverage_next_experiment_"
                "candidate_v0.json"
            )
        )

        self.bayesian_path = (
            self.models_dir
            / (
                "bayesian_next_experiment_"
                "candidate_v0.json"
            )
        )

        self.decision_path = (
            self.models_dir
            / "next_experiment_decision_v0.json"
        )

    @staticmethod
    def _load_json(
        path: Path,
    ) -> dict:

        if not path.exists():
            raise RecommendationIntegrityError(
                f"Required artifact is missing: "
                f"{path}"
            )

        try:
            return json.loads(
                path.read_text(
                    encoding="utf-8"
                )
            )

        except json.JSONDecodeError as exc:
            raise RecommendationIntegrityError(
                f"Invalid JSON artifact: {path}"
            ) from exc

    @staticmethod
    def _sha256_file(
        path: Path,
    ) -> str:

        if not path.exists():
            raise RecommendationIntegrityError(
                f"Required artifact is missing: "
                f"{path}"
            )

        hasher = hashlib.sha256()

        with path.open(
            "rb"
        ) as file:

            for chunk in iter(
                lambda: file.read(
                    1024 * 1024
                ),
                b"",
            ):
                hasher.update(
                    chunk
                )

        return hasher.hexdigest()

    @staticmethod
    def _assert_close(
        left: float,
        right: float,
        label: str,
    ) -> None:

        if not math.isclose(
            left,
            right,
            rel_tol=1e-12,
            abs_tol=1e-12,
        ):
            raise RecommendationIntegrityError(
                f"Inconsistent artifact value: "
                f"{label}"
            )

    def _load_verified_artifacts(
        self,
    ) -> tuple[
        dict,
        dict,
        dict,
    ]:

        decision = self._load_json(
            self.decision_path
        )

        coverage = self._load_json(
            self.coverage_path
        )

        bayesian = self._load_json(
            self.bayesian_path
        )

        if (
            decision.get("status")
            !=
            "next_experiment_decision_frozen"
        ):
            raise RecommendationIntegrityError(
                "Decision record is not in "
                "the expected frozen state."
            )

        if (
            decision.get(
                "decision_status"
            )
            !=
            "research_priority_candidate"
        ):
            raise RecommendationIntegrityError(
                "Unexpected decision status."
            )

        if (
            decision.get(
                "approval_status"
            )
            != "not_approved"
        ):
            raise RecommendationIntegrityError(
                "Unexpected approval status."
            )

        input_artifacts = (
            decision[
                "input_artifacts"
            ]
        )

        expected_coverage_sha = (
            input_artifacts[
                "coverage_candidate"
            ][
                "sha256"
            ]
        )

        expected_bayesian_sha = (
            input_artifacts[
                "bayesian_candidate"
            ][
                "sha256"
            ]
        )

        current_coverage_sha = (
            self._sha256_file(
                self.coverage_path
            )
        )

        current_bayesian_sha = (
            self._sha256_file(
                self.bayesian_path
            )
        )

        if (
            current_coverage_sha
            != expected_coverage_sha
        ):
            raise RecommendationIntegrityError(
                "Coverage candidate artifact "
                "SHA256 mismatch."
            )

        if (
            current_bayesian_sha
            != expected_bayesian_sha
        ):
            raise RecommendationIntegrityError(
                "Bayesian candidate artifact "
                "SHA256 mismatch."
            )

        expected_dataset_sha = (
            decision[
                "dataset_sha256"
            ]
        )

        current_dataset_sha = (
            self._sha256_file(
                self.dataset_path
            )
        )

        if (
            current_dataset_sha
            != expected_dataset_sha
        ):
            raise RecommendationIntegrityError(
                "Frozen baseline dataset "
                "SHA256 mismatch."
            )

        for artifact in (
            coverage,
            bayesian,
        ):

            if (
                artifact[
                    "source_id"
                ]
                != decision[
                    "source_id"
                ]
            ):
                raise RecommendationIntegrityError(
                    "Source ID mismatch "
                    "between artifacts."
                )

            if (
                artifact[
                    "dataset_version"
                ]
                != decision[
                    "dataset_version"
                ]
            ):
                raise RecommendationIntegrityError(
                    "Dataset version mismatch "
                    "between artifacts."
                )

            if (
                artifact[
                    "canonical_evidence_figure"
                ]
                != decision[
                    "canonical_evidence_figure"
                ]
            ):
                raise RecommendationIntegrityError(
                    "Canonical evidence figure "
                    "mismatch."
                )

        selected_thickness = float(
            decision[
                "selected_research_candidate"
            ][
                "thickness_um"
            ]
        )

        bayesian_thickness = float(
            bayesian[
                "candidate"
            ][
                "thickness_um"
            ]
        )

        self._assert_close(
            selected_thickness,
            bayesian_thickness,
            (
                "selected thickness vs "
                "Bayesian thickness"
            ),
        )

        return (
            decision,
            coverage,
            bayesian,
        )

    def get_recommendation(
        self,
    ) -> (
        NextExperimentRecommendationResponse
    ):

        (
            decision,
            coverage,
            bayesian,
        ) = (
            self._load_verified_artifacts()
        )

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

        bayesian_candidate = (
            bayesian[
                "candidate"
            ]
        )

        mg = (
            bayesian_candidate[
                "microgravity"
            ]
        )

        ng = (
            bayesian_candidate[
                "normal_gravity"
            ]
        )

        evidence = (
            decision[
                "evidence_relationship"
            ]
        )

        family = (
            bayesian[
                "experiment_family"
            ]
        )

        return (
            NextExperimentRecommendationResponse(
                candidate_id=(
                    bayesian[
                        "candidate_id"
                    ]
                ),

                decision_status=(
                    decision[
                        "decision_status"
                    ]
                ),

                recommendation_status=(
                    bayesian[
                        "recommendation_status"
                    ]
                ),

                approval_status=(
                    decision[
                        "approval_status"
                    ]
                ),

                production_ready=False,

                thickness_um=float(
                    selected[
                        "thickness_um"
                    ]
                ),

                why_selected=(
                    selected[
                        "selection_basis"
                    ]
                ),

                experiment_family=(
                    ExperimentFamilySummary(
                        material=(
                            family[
                                "material"
                            ]
                        ),

                        geometry_family=(
                            family[
                                "geometry_family"
                            ]
                        ),

                        oxygen_percent=float(
                            family[
                                "oxygen_percent"
                            ]
                        ),

                        pressure_kpa=float(
                            family[
                                "pressure_kpa"
                            ]
                        ),

                        matched_variable=(
                            family[
                                "matched_variable"
                            ]
                        ),

                        gravity_regimes=list(
                            family[
                                "gravity_regimes"
                            ]
                        ),
                    )
                ),

                agreement=(
                    AgreementSummary(
                        coverage_candidate_um=float(
                            agreement[
                                "coverage_thickness_um"
                            ]
                        ),

                        bayesian_candidate_um=float(
                            agreement[
                                "bayesian_thickness_um"
                            ]
                        ),

                        absolute_difference_um=float(
                            agreement[
                                "absolute_difference_um"
                            ]
                        ),

                        relative_difference_percent=float(
                            agreement[
                                "relative_difference_percent"
                            ]
                        ),

                        within_one_percent=bool(
                            agreement[
                                "within_one_percent"
                            ]
                        ),
                    )
                ),

                microgravity=(
                    GravityRecommendationSummary(
                        predicted_spread_rate_mm_s=float(
                            mg[
                                "gp_corrected_prediction_mm_s"
                            ]
                        ),

                        posterior_sd_log_residual=float(
                            mg[
                                "posterior_sd_log_residual"
                            ]
                        ),

                        nearest_existing_observation=(
                            ExistingObservationSummary(
                                **mg[
                                    "nearest_existing_observation"
                                ]
                            )
                        ),
                    )
                ),

                normal_gravity=(
                    GravityRecommendationSummary(
                        predicted_spread_rate_mm_s=float(
                            ng[
                                "gp_corrected_prediction_mm_s"
                            ]
                        ),

                        posterior_sd_log_residual=float(
                            ng[
                                "posterior_sd_log_residual"
                            ]
                        ),

                        nearest_existing_observation=(
                            ExistingObservationSummary(
                                **ng[
                                    "nearest_existing_observation"
                                ]
                            )
                        ),
                    )
                ),

                joint_uncertainty=(
                    JointUncertaintySummary(
                        matched_pair_joint_sd_log=float(
                            bayesian_candidate[
                                "matched_pair_joint_sd_log"
                            ]
                        ),

                        one_sd_ratio_uncertainty_factor=float(
                            bayesian_candidate[
                                "one_sd_ratio_uncertainty_factor"
                            ]
                        ),

                        predicted_mg_to_ng_spread_ratio=float(
                            bayesian_candidate[
                                "predicted_mg_to_ng_spread_ratio"
                            ]
                        ),
                    )
                ),

                evidence=(
                    EvidenceSummary(
                        source_id=(
                            decision[
                                "source_id"
                            ]
                        ),

                        figure=(
                            decision[
                                "canonical_evidence_figure"
                            ]
                        ),

                        dataset_version=(
                            decision[
                                "dataset_version"
                            ]
                        ),

                        dataset_sha256=(
                            decision[
                                "dataset_sha256"
                            ]
                        ),

                        shared_canonical_evidence=bool(
                            evidence[
                                "shared_canonical_evidence"
                            ]
                        ),

                        independent_validation=bool(
                            evidence[
                                "independent_validation"
                            ]
                        ),

                        external_validation=(
                            evidence[
                                "external_validation"
                            ]
                        ),
                    )
                ),

                integrity=(
                    ArtifactIntegritySummary(
                        dataset_sha256_verified=True,
                        coverage_artifact_sha256_verified=True,
                        bayesian_artifact_sha256_verified=True,
                    )
                ),

                scientific_guardrails=list(
                    decision[
                        "scientific_guardrails"
                    ]
                ),

                required_before_experiment_approval=list(
                    decision[
                        "required_before_experiment_approval"
                    ]
                ),
            )
        )