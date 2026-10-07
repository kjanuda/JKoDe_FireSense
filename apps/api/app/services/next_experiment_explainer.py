from app.schemas.next_experiment_explanation import (
    DecisionTraceStep,
    NextExperimentExplanationResponse,
    RatioRangeSummary,
    RecommendationEvidenceExplanation,
    RecommendationUncertaintyExplanation,
)

from app.services.next_experiment_recommendation import (
    NextExperimentRecommendationService,
)


class NextExperimentExplainer:

    def __init__(
        self,
        recommendation_service: NextExperimentRecommendationService,
    ) -> None:
        self.recommendation_service = recommendation_service

    def explain(
        self,
    ) -> NextExperimentExplanationResponse:

        recommendation = (
            self.recommendation_service
            .get_recommendation()
        )

        agreement = recommendation.agreement
        uncertainty = recommendation.joint_uncertainty

        predicted_ratio = float(
            uncertainty.predicted_mg_to_ng_spread_ratio
        )

        one_sd_factor = float(
            uncertainty.one_sd_ratio_uncertainty_factor
        )

        descriptive_lower = (
            predicted_ratio
            / one_sd_factor
        )

        descriptive_upper = (
            predicted_ratio
            * one_sd_factor
        )

        thickness = float(
            recommendation.thickness_um
        )

        coverage_thickness = float(
            agreement.coverage_candidate_um
        )

        bayesian_thickness = float(
            agreement.bayesian_candidate_um
        )

        relative_difference = float(
            agreement.relative_difference_percent
        )

        why_this_thickness = [
            (
                f"The Bayesian matched-pair pure-exploration search "
                f"selected {thickness:.3f} um because this location "
                f"has the highest modeled joint posterior uncertainty "
                f"for the microgravity versus normal-gravity comparison "
                f"inside the shared empirical thickness domain."
            ),
            (
                f"A separate empirical coverage heuristic selected "
                f"{coverage_thickness:.3f} um."
            ),
            (
                f"The coverage and Bayesian candidates differ by only "
                f"{relative_difference:.3f}% in thickness, so two "
                f"different internal selection methods point to nearly "
                f"the same region."
            ),
            (
                "The Bayesian candidate is used as the current "
                "research-priority value because it directly uses "
                "posterior model uncertainty, while the coverage "
                "method uses evidence spacing only."
            ),
        ]

        decision_trace = [
            DecisionTraceStep(
                order=1,
                stage="evidence",
                title="Start from frozen evidence",
                explanation=(
                    "The v0 analysis uses the frozen PMMA thin-sheet "
                    "experimental dataset derived from canonical "
                    "Figure 2.21."
                ),
            ),
            DecisionTraceStep(
                order=2,
                stage="coverage",
                title="Locate sparse evidence",
                explanation=(
                    f"The empirical coverage-gap analysis identifies "
                    f"a matched candidate at "
                    f"{coverage_thickness:.3f} um based on spacing "
                    f"between existing observations."
                ),
            ),
            DecisionTraceStep(
                order=3,
                stage="bayesian",
                title="Search model uncertainty",
                explanation=(
                    "Separate physics-informed Gaussian-process "
                    "residual models are evaluated for microgravity "
                    "and normal gravity. Their posterior standard "
                    "deviations are combined for matched-pair pure "
                    "exploration."
                ),
            ),
            DecisionTraceStep(
                order=4,
                stage="agreement",
                title="Compare the two methods",
                explanation=(
                    f"The Bayesian candidate is "
                    f"{bayesian_thickness:.3f} um and the coverage "
                    f"candidate is {coverage_thickness:.3f} um. "
                    f"Their relative difference is "
                    f"{relative_difference:.3f}%."
                ),
            ),
            DecisionTraceStep(
                order=5,
                stage="decision",
                title="Set research priority",
                explanation=(
                    f"{thickness:.3f} um is frozen as the current "
                    f"research-priority matched-pair candidate. "
                    f"It is not an approved experiment."
                ),
            ),
        ]

        scientific_caveats = list(
            recommendation.scientific_guardrails
        )

        scientific_caveats.extend(
            [
                (
                    "The descriptive one-standard-deviation ratio "
                    "range is computed from the GP log-space posterior "
                    "uncertainty. It is not a calibrated confidence "
                    "interval."
                ),
                (
                    "The v0 matched-pair uncertainty calculation "
                    "assumes the microgravity and normal-gravity "
                    "Gaussian-process models are independent."
                ),
            ]
        )

        return NextExperimentExplanationResponse(
            candidate_id=recommendation.candidate_id,

            title=(
                f"Why FireSense prioritizes "
                f"{thickness:.3f} um"
            ),

           summary=(
    f"FireSense v0 prioritizes a matched PMMA thin-sheet "
    f"experiment near {thickness:.3f} um in microgravity "
    f"and normal gravity because the Bayesian "
    f"pure-exploration model assigns high joint uncertainty "
    f"to this region, while the separate coverage-gap "
    f"heuristic points to almost the same thickness. "
    f"This is a research-priority candidate, not "
    f"experiment approval."
),

            thickness_um=thickness,

            decision_status=(
                recommendation.decision_status
            ),

            approval_status=(
                recommendation.approval_status
            ),

            production_ready=False,

            why_this_thickness=why_this_thickness,

            decision_trace=decision_trace,

            uncertainty=(
                RecommendationUncertaintyExplanation(
                    microgravity_posterior_sd_log_residual=float(
                        recommendation
                        .microgravity
                        .posterior_sd_log_residual
                    ),

                    normal_gravity_posterior_sd_log_residual=float(
                        recommendation
                        .normal_gravity
                        .posterior_sd_log_residual
                    ),

                    matched_pair_joint_sd_log=float(
                        uncertainty
                        .matched_pair_joint_sd_log
                    ),

                    ratio_range=(
                        RatioRangeSummary(
                            predicted_ratio=predicted_ratio,

                            one_sd_factor=one_sd_factor,

                            descriptive_lower=(
                                descriptive_lower
                            ),

                            descriptive_upper=(
                                descriptive_upper
                            ),

                            interpretation=(
                                "A one-standard-deviation movement "
                                "in modeled log-ratio space corresponds "
                                "to multiplying or dividing the "
                                "predicted MG/normal spread-rate ratio "
                                f"by {one_sd_factor:.4f}."
                            ),
                        )
                    ),

                    uncertainty_target=(
                        "Modeled log spread-rate difference between "
                        "microgravity and normal gravity."
                    ),

                    interpretation=(
                        "The joint value combines the two "
                        "gravity-regime posterior standard deviations "
                        "by quadrature under the v0 independent-model "
                        "assumption."
                    ),

                    calibration_status=(
                        "not_externally_calibrated"
                    ),
                )
            ),

            evidence=(
                RecommendationEvidenceExplanation(
                    source_id=(
                        recommendation
                        .evidence
                        .source_id
                    ),

                    figure=(
                        recommendation
                        .evidence
                        .figure
                    ),

                    dataset_version=(
                        recommendation
                        .evidence
                        .dataset_version
                    ),

                    dataset_sha256=(
                        recommendation
                        .evidence
                        .dataset_sha256
                    ),

                    shared_canonical_evidence=(
                        recommendation
                        .evidence
                        .shared_canonical_evidence
                    ),

                    independent_validation=(
                        recommendation
                        .evidence
                        .independent_validation
                    ),

                    external_validation=(
                        recommendation
                        .evidence
                        .external_validation
                    ),

                    interpretation=(
                        "The coverage and Bayesian results share the same "
                        "frozen Figure 2.21 evidence base. Their agreement "
                        "is internal convergence and must not be described "
                        "as independent or external validation."
                    ),
                )
            ),

            scientific_caveats=(
                scientific_caveats
            ),

            required_before_experiment_approval=list(
                recommendation
                .required_before_experiment_approval
            ),
        )

