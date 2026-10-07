import json
import math
from pathlib import Path

from app.core.paths import (
    CURATED_DATA_DIR,
)

from app.schemas.prediction import (
    FireBehaviorPredictionRequest,
    FireBehaviorPredictionResponse,
    PredictionModelInfo,
    PredictionValue,
    SupportedDomain,
)


MODEL_PATH = (
    CURATED_DATA_DIR
    / "thin_sheet"
    / "models"
    / "physics_baseline_v0.json"
)

DIAGNOSTICS_PATH = (
    CURATED_DATA_DIR
    / "thin_sheet"
    / "models"
    / "physics_baseline_v0_diagnostics.json"
)


SUPPORTED_MATERIAL = "PMMA"
SUPPORTED_GEOMETRY = "thin_sheet"

SUPPORTED_OXYGEN_FRACTION = 0.21
SUPPORTED_PRESSURE_KPA = 101.325


OXYGEN_TOLERANCE = 1e-6
PRESSURE_TOLERANCE_KPA = 1e-3


class PhysicsBaselinePredictor:

    def __init__(
        self,
        model_path: Path = MODEL_PATH,
        diagnostics_path: Path = DIAGNOSTICS_PATH,
    ) -> None:

        self.model_path = (
            model_path
        )

        self.diagnostics_path = (
            diagnostics_path
        )

        self.model = self._load_json(
            self.model_path
        )

        self.diagnostics = (
            self._load_json(
                self.diagnostics_path
            )
        )

        self._validate_artifacts()

    @staticmethod
    def _load_json(
        path: Path,
    ) -> dict:

        if not path.exists():

            raise FileNotFoundError(
                f"Missing model artifact: "
                f"{path}"
            )

        return json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

    def _validate_artifacts(
        self,
    ) -> None:

        if (
            self.model.get(
                "status"
            )
            !=
            "exploratory_physics_baseline_fitted"
        ):

            raise ValueError(
                "Physics baseline model "
                "artifact is not valid."
            )

        if (
            self.diagnostics.get(
                "status"
            )
            !=
            "baseline_diagnostics_complete"
        ):

            raise ValueError(
                "Physics baseline diagnostics "
                "are not complete."
            )

        if (
            self.diagnostics.get(
                "external_validation"
            )
            != "not_performed"
        ):

            raise ValueError(
                "Unexpected external "
                "validation state."
            )

    def _domain_for(
        self,
        gravity_regime: str,
    ) -> SupportedDomain:

        group = (
            self.diagnostics[
                "groups"
            ][
                gravity_regime
            ]
        )

        domain = (
            group[
                "empirical_domain"
            ]
        )

        return SupportedDomain(
            material=SUPPORTED_MATERIAL,

            geometry=(
                SUPPORTED_GEOMETRY
            ),

            gravity_regime=(
                gravity_regime
            ),

            thickness_um_min=float(
                domain[
                    "thickness_um_min"
                ]
            ),

            thickness_um_max=float(
                domain[
                    "thickness_um_max"
                ]
            ),

            oxygen_fraction=(
                SUPPORTED_OXYGEN_FRACTION
            ),

            pressure_kpa=(
                SUPPORTED_PRESSURE_KPA
            ),
        )

    def _model_info_for(
        self,
        gravity_regime: str,
    ) -> PredictionModelInfo:

        group = (
            self.model[
                "groups"
            ][
                gravity_regime
            ]
        )

        physics = (
            group[
                "physics_inverse_baseline"
            ]
        )

        return PredictionModelInfo(
            model_name=(
                self.model[
                    "model_name"
                ]
            ),

            model_version=(
                self.model[
                    "model_version"
                ]
            ),

            formula=(
                "V = K / tau"
            ),

            coefficient_k=float(
                physics[
                    "coefficient_k"
                ]
            ),

            canonical_evidence_figure=(
                self.model[
                    "canonical_evidence_figure"
                ]
            ),

            external_validation_status=(
                "not_performed"
            ),

            production_ready=False,
        )

    def _residual_factor_for(
        self,
        gravity_regime: str,
    ) -> float:

        return float(
            self.diagnostics[
                "groups"
            ][
                gravity_regime
            ][
                "residual_description"
            ][
                "multiplicative_residual_factor"
            ]
        )

    def predict(
        self,
        request: FireBehaviorPredictionRequest,
    ) -> FireBehaviorPredictionResponse:

        reasons: list[str] = []

        domain = self._domain_for(
            request.gravity_regime
        )

        model_info = (
            self._model_info_for(
                request.gravity_regime
            )
        )

        # --------------------------------
        # Scientific scope guardrails
        # --------------------------------

        if (
            request.material.strip().upper()
            != SUPPORTED_MATERIAL
        ):

            reasons.append(
                "unsupported_material"
            )

        if (
            request.geometry.strip().lower()
            != SUPPORTED_GEOMETRY
        ):

            reasons.append(
                "unsupported_geometry"
            )

        if not math.isclose(
            request.oxygen_fraction,
            SUPPORTED_OXYGEN_FRACTION,
            rel_tol=0.0,
            abs_tol=OXYGEN_TOLERANCE,
        ):

            reasons.append(
                "unsupported_oxygen_fraction"
            )

        if not math.isclose(
            request.pressure_kpa,
            SUPPORTED_PRESSURE_KPA,
            rel_tol=0.0,
            abs_tol=PRESSURE_TOLERANCE_KPA,
        ):

            reasons.append(
                "unsupported_pressure"
            )

        if (
            request.thickness_um
            <
            domain.thickness_um_min
        ):

            reasons.append(
                "thickness_below_empirical_domain"
            )

        if (
            request.thickness_um
            >
            domain.thickness_um_max
        ):

            reasons.append(
                "thickness_above_empirical_domain"
            )

        # --------------------------------
        # Abstain
        # --------------------------------

        if reasons:

            return (
                FireBehaviorPredictionResponse(
                    decision="abstain",

                    prediction=None,

                    abstention_reasons=(
                        reasons
                    ),

                    supported_domain=(
                        domain
                    ),

                    model=(
                        model_info
                    ),

                    descriptive_residual_factor=None,

                    uncertainty_note=(
                        "No prediction returned. "
                        "The request is outside "
                        "the empirically supported "
                        "scope of Physics Baseline v0."
                    ),

                    warnings=[
                        (
                            "FireSense v0 does not "
                            "extrapolate beyond its "
                            "observed scientific domain."
                        ),
                        (
                            "External validation "
                            "has not yet been performed."
                        ),
                    ],
                )
            )

        # --------------------------------
        # Predict inside domain
        # --------------------------------

        k = (
            model_info.coefficient_k
        )

        prediction_value = (
            k
            / request.thickness_um
        )

        residual_factor = (
            self._residual_factor_for(
                request.gravity_regime
            )
        )

        return (
            FireBehaviorPredictionResponse(
                decision="predict",

                prediction=(
                    PredictionValue(
                        value=float(
                            prediction_value
                        )
                    )
                ),

                abstention_reasons=[],

                supported_domain=(
                    domain
                ),

                model=(
                    model_info
                ),

                descriptive_residual_factor=(
                    residual_factor
                ),

                uncertainty_note=(
                    "The residual factor is "
                    "descriptive training-residual "
                    "spread only. It is not a "
                    "calibrated confidence interval "
                    "or prediction interval."
                ),

                warnings=[
                    (
                        "Prediction is interpolation "
                        "within the Figure 2.21 "
                        "empirical domain."
                    ),
                    (
                        "External validation has "
                        "not yet been performed."
                    ),
                    (
                        "This model is exploratory "
                        "research decision support "
                        "and is not production-ready."
                    ),
                ],
            )
        )