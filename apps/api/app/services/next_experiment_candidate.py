import json
import math
from pathlib import Path

from app.core.paths import (
    CURATED_DATA_DIR,
)

from app.schemas.next_experiment import (
    ExperimentCondition,
    GravityCandidate,
    MatchedPairCandidate,
    NextExperimentCandidateResponse,
)


GAP_MAP_PATH = (
    CURATED_DATA_DIR
    / "thin_sheet"
    / "evidence_gap_map_v0.json"
)


class NextExperimentCandidateBuilder:

    def __init__(
        self,
        gap_map_path: Path = GAP_MAP_PATH,
    ) -> None:

        self.gap_map_path = (
            gap_map_path
        )

        self.gap_map = (
            self._load_json(
                self.gap_map_path
            )
        )

        self._validate()

    @staticmethod
    def _load_json(
        path: Path,
    ) -> dict:

        if not path.exists():

            raise FileNotFoundError(
                f"Missing gap-map artifact: "
                f"{path}"
            )

        return json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

    def _validate(
        self,
    ) -> None:

        if (
            self.gap_map.get(
                "status"
            )
            !=
            "empirical_coverage_gap_map_complete"
        ):

            raise ValueError(
                "Evidence gap map v0 "
                "is not complete."
            )

        if (
            self.gap_map.get(
                "gap_map_version"
            )
            != "v0"
        ):

            raise ValueError(
                "Unexpected gap-map version."
            )

        if (
            self.gap_map[
                "scope_policy"
            ][
                "uses_model_uncertainty"
            ]
            is not False
        ):

            raise ValueError(
                "Coverage candidate must not "
                "claim model uncertainty use."
            )

    def build(
        self,
    ) -> NextExperimentCandidateResponse:

        micro = (
            self.gap_map[
                "groups"
            ][
                "microgravity"
            ][
                "largest_internal_gap"
            ]
        )

        normal = (
            self.gap_map[
                "groups"
            ][
                "normal_gravity"
            ][
                "largest_internal_gap"
            ]
        )

        micro_candidate = float(
            micro[
                "coverage_candidate_thickness_um"
            ]
        )

        normal_candidate = float(
            normal[
                "coverage_candidate_thickness_um"
            ]
        )

        # Geometric mean is appropriate
        # because the coverage analysis was
        # performed in log-thickness space.

        paired_thickness = float(
            math.sqrt(
                micro_candidate
                * normal_candidate
            )
        )

        relative_difference = float(
            abs(
                micro_candidate
                - normal_candidate
            )
            / (
                (
                    micro_candidate
                    + normal_candidate
                )
                / 2.0
            )
        )

        similar = (
            relative_difference
            <= 0.10
        )

        gravity_candidates = [
            GravityCandidate(
                gravity_regime=(
                    "microgravity"
                ),

                candidate_thickness_um=(
                    micro_candidate
                ),

                gap_left_um=float(
                    micro[
                        "left_thickness_um"
                    ]
                ),

                gap_right_um=float(
                    micro[
                        "right_thickness_um"
                    ]
                ),

                log_gap_decades=float(
                    micro[
                        "log_gap_decades"
                    ]
                ),

                left_record_id=(
                    micro[
                        "left_record_id"
                    ]
                ),

                right_record_id=(
                    micro[
                        "right_record_id"
                    ]
                ),
            ),

            GravityCandidate(
                gravity_regime=(
                    "normal_gravity"
                ),

                candidate_thickness_um=(
                    normal_candidate
                ),

                gap_left_um=float(
                    normal[
                        "left_thickness_um"
                    ]
                ),

                gap_right_um=float(
                    normal[
                        "right_thickness_um"
                    ]
                ),

                log_gap_decades=float(
                    normal[
                        "log_gap_decades"
                    ]
                ),

                left_record_id=(
                    normal[
                        "left_record_id"
                    ]
                ),

                right_record_id=(
                    normal[
                        "right_record_id"
                    ]
                ),
            ),
        ]

        return (
            NextExperimentCandidateResponse(
                candidate_id=(
                    "NEXTEXP-COVERAGE-V0-001"
                ),

                basis=(
                    "empirical_coverage_gap"
                ),

                recommendation_status=(
                    "coverage_candidate_only"
                ),

                approval_status=(
                    "not_approved"
                ),

                experiment_condition=(
                    ExperimentCondition(
                        thickness_um=(
                            paired_thickness
                        ),

                        oxygen_fraction=(
                            0.21
                        ),

                        pressure_kpa=(
                            101.325
                        ),
                    )
                ),

                matched_pair=(
                    MatchedPairCandidate(
                        thickness_um=(
                            paired_thickness
                        ),

                        microgravity_thickness_um=(
                            micro_candidate
                        ),

                        normal_gravity_thickness_um=(
                            normal_candidate
                        ),

                        relative_difference=(
                            relative_difference
                        ),

                        similar_thickness=(
                            similar
                        ),
                    )
                ),

                gravity_candidates=(
                    gravity_candidates
                ),

                rationale=[
                    (
                        "The largest internal "
                        "microgravity evidence gap "
                        "lies between approximately "
                        "102 and 201 µm."
                    ),

                    (
                        "The largest internal "
                        "normal-gravity evidence gap "
                        "lies between approximately "
                        "100 and 200 µm."
                    ),

                    (
                        "The two independent "
                        "coverage-gap midpoints are "
                        "within approximately one "
                        "percent of each other."
                    ),

                    (
                        "A matched thickness near "
                        "the geometric mean of the "
                        "two candidates provides a "
                        "clean comparison target."
                    ),
                ],

                scientific_guardrails=[
                    (
                        "This candidate is derived "
                        "from evidence spacing only."
                    ),

                    (
                        "It is not a Bayesian "
                        "optimal experiment."
                    ),

                    (
                        "It is not an approved "
                        "experiment."
                    ),

                    (
                        "No expected information "
                        "gain has been calculated."
                    ),

                    (
                        "No experiment cost model "
                        "has been applied."
                    ),

                    (
                        "No Figure 2.22 unresolved "
                        "external evidence is used."
                    ),

                    (
                        "No theoretical curve is "
                        "treated as experimental "
                        "evidence."
                    ),
                ],

                required_before_bayesian_recommendation=[
                    (
                        "Define candidate search "
                        "space."
                    ),

                    (
                        "Fit a probabilistic model "
                        "with explicit predictive "
                        "uncertainty."
                    ),

                    (
                        "Define an acquisition "
                        "objective."
                    ),

                    (
                        "Evaluate candidate points "
                        "with Bayesian experimental "
                        "design."
                    ),
                ],

                required_before_experiment_approval=[
                    (
                        "Resolve practical sample "
                        "thickness availability."
                    ),

                    (
                        "Confirm experimental "
                        "hardware constraints."
                    ),

                    (
                        "Confirm atmosphere and "
                        "flow configuration."
                    ),

                    (
                        "Perform scientific and "
                        "safety review."
                    ),
                ],

                production_ready=False,
            )
        )