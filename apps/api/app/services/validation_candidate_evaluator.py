import math

from app.schemas.prediction import (
    FireBehaviorPredictionRequest,
)

from app.schemas.validation_candidate import (
    ValidationCandidateEvaluationResponse,
    ValidationCandidateRequest,
    ValidationEvaluationRecord,
    ValidationGateCheck,
    ValidationMetrics,
)

from app.services.physics_baseline_predictor import (
    PhysicsBaselinePredictor,
)

from app.services.validation_readiness import (
    get_validation_readiness,
)


class ValidationCandidateEvaluationError(
    RuntimeError
):
    pass


FLOW_REFERENCE_MM_S = 50.0

TARGET_OXYGEN_PERCENT = 21.0

TARGET_PRESSURE_KPA = 101.325


def _close(
    left: float,
    right: float,
    tolerance: float = 1e-9,
) -> bool:
    return math.isclose(
        left,
        right,
        rel_tol=0.0,
        abs_tol=tolerance,
    )


def _check(
    checks: list[ValidationGateCheck],
    check_id: str,
    passed: bool,
    pass_detail: str,
    fail_detail: str,
) -> bool:
    checks.append(
        ValidationGateCheck(
            check_id=check_id,
            passed=passed,
            detail=(
                pass_detail
                if passed
                else fail_detail
            ),
        )
    )

    return passed


def _calculate_metrics(
    records: list[
        ValidationEvaluationRecord
    ],
) -> ValidationMetrics | None:

    usable = [
        record
        for record in records
        if (
            record.predicted_spread_rate_mm_s
            is not None
            and record.absolute_error_mm_s
            is not None
            and record.prediction_minus_observed_mm_s
            is not None
            and record.relative_error_vs_observed_percent
            is not None
        )
    ]

    if not usable:
        return None

    count = len(
        usable
    )

    absolute_errors = [
        float(
            record.absolute_error_mm_s
        )
        for record in usable
    ]

    signed_errors = [
        float(
            record.prediction_minus_observed_mm_s
        )
        for record in usable
    ]

    relative_errors = [
        abs(
            float(
                record.relative_error_vs_observed_percent
            )
        )
        for record in usable
    ]

    squared_errors = [
        error ** 2
        for error in signed_errors
    ]

    return ValidationMetrics(
        evaluated_point_count=count,

        mae_mm_s=(
            sum(
                absolute_errors
            )
            / count
        ),

        rmse_mm_s=math.sqrt(
            sum(
                squared_errors
            )
            / count
        ),

        mean_bias_mm_s=(
            sum(
                signed_errors
            )
            / count
        ),

        mean_absolute_percentage_error_percent=(
            sum(
                relative_errors
            )
            / count
        ),

        max_absolute_error_mm_s=max(
            absolute_errors
        ),
    )


def evaluate_validation_candidate(
    candidate: ValidationCandidateRequest,
) -> ValidationCandidateEvaluationResponse:

    # Verifies the frozen acceptance protocol
    # and its SHA-256 before evaluating anything.
    readiness = get_validation_readiness()

    predictor = (
        PhysicsBaselinePredictor()
    )

    checks: list[
        ValidationGateCheck
    ] = []


    # ---------------------------------
    # Source independence
    # ---------------------------------

    source = candidate.source

    source_independence = all(
        [
            source.independent_publication_or_dataset,
            source.independent_experimental_campaign,
            source.not_firesense_training_source,
            source.not_reused_bass_ii_rows,
        ]
    )

    _check(
        checks,
        "source_independence",
        source_independence,
        (
            "Source independence requirements "
            "are satisfied."
        ),
        (
            "Source is not sufficiently "
            "independent from FireSense "
            "training evidence."
        ),
    )


    # ---------------------------------
    # Experimental evidence
    # ---------------------------------

    experimental_pass = (
        source.experimental_data_only
    )

    _check(
        checks,
        "experimental_evidence",
        experimental_pass,
        (
            "Candidate contains experimental "
            "evidence."
        ),
        (
            "Theory-only or simulation-only "
            "evidence cannot satisfy direct "
            "external validation."
        ),
    )


    # ---------------------------------
    # Minimum validation scope
    # ---------------------------------

    minimum_points = (
        readiness
        .minimum_validation_scope
        .minimum_independent_numeric_points
    )

    scope_pass = (
        len(
            candidate.records
        )
        >= minimum_points
    )

    _check(
        checks,
        "minimum_numeric_scope",
        scope_pass,
        (
            f"Candidate contains at least "
            f"{minimum_points} numeric points."
        ),
        (
            f"At least {minimum_points} "
            f"independent numeric points are "
            f"required."
        ),
    )


    # ---------------------------------
    # Material / geometry
    # ---------------------------------

    material_pass = all(
        record.material.upper()
        == "PMMA"
        for record
        in candidate.records
    )

    _check(
        checks,
        "material_match",
        material_pass,
        "All rows use PMMA.",
        (
            "Every direct-validation row "
            "must use PMMA."
        ),
    )


    geometry_pass = all(
        record.geometry_family
        == "thin_sheet"
        for record
        in candidate.records
    )

    _check(
        checks,
        "geometry_match",
        geometry_pass,
        (
            "All rows use the thin-sheet "
            "geometry family."
        ),
        (
            "Every direct-validation row "
            "must use thin-sheet geometry."
        ),
    )


    # ---------------------------------
    # Environment
    # ---------------------------------

    oxygen_pass = all(
        _close(
            record.oxygen_percent,
            TARGET_OXYGEN_PERCENT,
        )
        for record
        in candidate.records
    )

    _check(
        checks,
        "oxygen_condition",
        oxygen_pass,
        (
            "All rows match the FireSense v0 "
            "21% oxygen condition."
        ),
        (
            "At least one row does not match "
            "the FireSense v0 21% oxygen "
            "validation condition."
        ),
    )


    pressure_pass = all(
        _close(
            record.pressure_kpa,
            TARGET_PRESSURE_KPA,
        )
        for record
        in candidate.records
    )

    _check(
        checks,
        "pressure_condition",
        pressure_pass,
        (
            "All rows match the FireSense v0 "
            "101.325 kPa condition."
        ),
        (
            "At least one row does not match "
            "the FireSense v0 101.325 kPa "
            "validation condition."
        ),
    )


    # ---------------------------------
    # Microgravity transport
    # ---------------------------------

    microgravity_records = [
        record
        for record
        in candidate.records
        if (
            record.gravity_regime
            == "microgravity"
        )
    ]

    microgravity_transport_pass = all(
        (
            record.transport_configuration
            == "opposed_flow"
            and record.flow_mm_s
            is not None
            and _close(
                record.flow_mm_s,
                FLOW_REFERENCE_MM_S,
            )
        )
        for record
        in microgravity_records
    )

    _check(
        checks,
        "microgravity_transport",
        microgravity_transport_pass,
        (
            "Microgravity rows match the "
            "50 mm/s opposed-flow reference."
        ),
        (
            "Microgravity rows must use "
            "50 mm/s opposed flow."
        ),
    )


    # ---------------------------------
    # Normal-gravity transport
    # ---------------------------------

    normal_gravity_records = [
        record
        for record
        in candidate.records
        if (
            record.gravity_regime
            == "normal_gravity"
        )
    ]

    normal_transport_pass = (
        not normal_gravity_records
        or (
            source
            .normal_gravity_transport_equivalence_established
        )
    )

    _check(
        checks,
        "normal_gravity_transport",
        normal_transport_pass,
        (
            "Normal-gravity transport "
            "equivalence is established or "
            "not applicable."
        ),
        (
            "Normal-gravity transport "
            "equivalence has not been "
            "established."
        ),
    )


    # ---------------------------------
    # Measurement compatibility
    # ---------------------------------

    quantity_pass = (
        source.measurement_quantity
        == "flame_spread_rate"
    )

    _check(
        checks,
        "measurement_quantity",
        quantity_pass,
        (
            "Measured quantity is flame "
            "spread rate."
        ),
        (
            "Measured quantity does not "
            "match FireSense."
        ),
    )


    measurement_pass = (
        source.measurement_definition_matches
        or source.cross_calibration_available
    )

    _check(
        checks,
        "measurement_definition",
        measurement_pass,
        (
            "Measurement definition matches "
            "or empirical cross-calibration "
            "is available."
        ),
        (
            "Operational measurement "
            "definition differs and no "
            "cross-calibration is available."
        ),
    )


    # ---------------------------------
    # Holdout / provenance
    # ---------------------------------

    holdout_pass = all(
        (
            record.training_eligible
            is False
            and record.validation_holdout
            is True
        )
        for record
        in candidate.records
    )

    _check(
        checks,
        "holdout_integrity",
        holdout_pass,
        (
            "All rows remain holdout and "
            "training-ineligible."
        ),
        (
            "Validation rows must not be "
            "training eligible."
        ),
    )


    provenance_pass = all(
        bool(
            record.provenance_reference.strip()
        )
        for record
        in candidate.records
    )

    _check(
        checks,
        "record_provenance",
        provenance_pass,
        (
            "Every row preserves a provenance "
            "reference."
        ),
        (
            "Every validation row requires "
            "provenance."
        ),
    )


    # ---------------------------------
    # Uncertainty separation
    # ---------------------------------

    uncertainty_pass = all(
        [
            source.uncertainty_or_variability_metadata_preserved,
            source.digitization_uncertainty_separate,
            source.experimental_uncertainty_separate,
            source.model_uncertainty_separate,
        ]
    )

    _check(
        checks,
        "uncertainty_separation",
        uncertainty_pass,
        (
            "Digitization, experimental and "
            "model uncertainty remain "
            "separate."
        ),
        (
            "Uncertainty categories are not "
            "sufficiently separated."
        ),
    )


    # ---------------------------------
    # Frozen predictor evaluation
    # ---------------------------------

    evaluations: list[
        ValidationEvaluationRecord
    ] = []

    model_domain_pass = True

    for record in candidate.records:

        request = (
            FireBehaviorPredictionRequest(
                material=record.material,
                geometry=record.geometry_family,
                thickness_um=record.thickness_um,
                gravity_regime=record.gravity_regime,
                oxygen_fraction=(
                    record.oxygen_percent
                    / 100.0
                ),
                pressure_kpa=record.pressure_kpa,
            )
        )

        prediction_result = (
            predictor.predict(
                request
            )
        )

        if (
            prediction_result.decision
            != "predict"
            or prediction_result.prediction
            is None
        ):
            model_domain_pass = False

            evaluations.append(
                ValidationEvaluationRecord(
                    record_id=record.record_id,
                    gravity_regime=record.gravity_regime,
                    thickness_um=record.thickness_um,
                    observed_spread_rate_mm_s=(
                        record.observed_spread_rate_mm_s
                    ),
                    predicted_spread_rate_mm_s=None,
                    prediction_decision="abstain",
                    prediction_minus_observed_mm_s=None,
                    absolute_error_mm_s=None,
                    relative_error_vs_observed_percent=None,
                    abstention_reasons=list(
                        prediction_result
                        .abstention_reasons
                    ),
                )
            )

            continue


        predicted = float(
            prediction_result
            .prediction
            .value
        )

        observed = float(
            record.observed_spread_rate_mm_s
        )

        error = (
            predicted
            - observed
        )

        absolute_error = abs(
            error
        )

        relative_error = (
            error
            / observed
            * 100.0
        )

        evaluations.append(
            ValidationEvaluationRecord(
                record_id=record.record_id,
                gravity_regime=record.gravity_regime,
                thickness_um=record.thickness_um,
                observed_spread_rate_mm_s=observed,
                predicted_spread_rate_mm_s=predicted,
                prediction_decision="predict",
                prediction_minus_observed_mm_s=error,
                absolute_error_mm_s=absolute_error,
                relative_error_vs_observed_percent=(
                    relative_error
                ),
                abstention_reasons=[],
            )
        )


    _check(
        checks,
        "firesense_v0_model_domain",
        model_domain_pass,
        (
            "All candidate rows are inside "
            "the frozen FireSense v0 "
            "prediction domain."
        ),
        (
            "At least one candidate row is "
            "outside the frozen FireSense v0 "
            "prediction domain."
        ),
    )


    # ---------------------------------
    # Final compatibility gate
    # ---------------------------------

    direct_gate_passed = all(
        check.passed
        for check
        in checks
    )

    metrics = _calculate_metrics(
        evaluations
    )

    evaluated_count = sum(
        1
        for record
        in evaluations
        if (
            record.prediction_decision
            == "predict"
        )
    )

    blocked_count = (
        len(
            candidate.records
        )
        - evaluated_count
    )


    if not source_independence:
        classification = (
            "non_independent_rejected"
        )

    elif not scope_pass:
        classification = (
            "insufficient_validation_scope"
        )

    elif not model_domain_pass:
        classification = (
            "outside_firesense_v0_domain"
        )

    elif direct_gate_passed:
        classification = (
            "compatible_independent_"
            "validation_candidate"
        )

    else:
        classification = (
            "independent_external_"
            "comparison_only"
        )


    if metrics is None:
        metrics_role = (
            "not_available"
        )

    elif direct_gate_passed:
        metrics_role = (
            "validation_candidate_metrics"
        )

    else:
        metrics_role = (
            "comparison_only_metrics"
        )


    guardrails = [
        (
            "Passing the compatibility gate "
            "does not by itself prove model "
            "performance is acceptable."
        ),
        (
            "No external-validation claim is "
            "allowed until quantitative "
            "performance acceptance thresholds "
            "are frozen and satisfied."
        ),
        (
            "Candidate validation rows remain "
            "holdout and must never be added "
            "to model training."
        ),
        (
            "MAE, RMSE, bias and percentage "
            "error are evaluation metrics, "
            "not uncertainty intervals."
        ),
        (
            "Digitization uncertainty, "
            "experimental uncertainty and "
            "model uncertainty remain separate."
        ),
        (
            "Synthetic software-test fixtures "
            "are never scientific evidence."
        ),
        (
            "Production-ready and certification "
            "claims remain blocked."
        ),
    ]


    return ValidationCandidateEvaluationResponse(
        dataset_id=candidate.dataset_id,

        dataset_version=(
            candidate.dataset_version
        ),

        source_id=(
            candidate.source.source_id
        ),

        classification=classification,

        direct_validation_gate_passed=(
            direct_gate_passed
        ),

        holdout_evaluation_completed=(
            evaluated_count
            == len(
                candidate.records
            )
        ),

        external_validation_claim_allowed=False,

        production_ready_claim_allowed=False,

        certification_claim_allowed=False,

        performance_acceptance_status=(
            "thresholds_not_yet_frozen"
            if direct_gate_passed
            else "not_applicable_gate_failed"
        ),

        submitted_point_count=len(
            candidate.records
        ),

        evaluated_point_count=(
            evaluated_count
        ),

        blocked_point_count=(
            blocked_count
        ),

        gate_checks=checks,

        metrics_role=metrics_role,

        metrics=metrics,

        evaluations=evaluations,

        guardrails=guardrails,
    )
