from app.schemas.validation_uncertainty import (
    ValidationUncertaintyAssessmentRequest,
    ValidationUncertaintyAssessmentResponse,
    ValidationUncertaintyRowDiagnostic,
)

from app.services.validation_candidate_evaluator import (
    evaluate_validation_candidate,
)


class ValidationUncertaintyAssessmentError(
    RuntimeError
):
    pass


SUPPORTED_EXPERIMENTAL_KINDS = {
    "standard_deviation",
    "standard_error",
    "confidence_interval_half_width",
    "range_half_width",
}


def assess_validation_uncertainty(
    request: ValidationUncertaintyAssessmentRequest,
) -> ValidationUncertaintyAssessmentResponse:

    candidate = request.candidate

    evaluation = (
        evaluate_validation_candidate(
            candidate
        )
    )

    records_by_id = {
        record.record_id: record
        for record
        in candidate.records
    }


    rows_with_experimental = sum(
        1
        for record
        in candidate.records
        if (
            record.experimental_uncertainty_mm_s
            is not None
        )
    )

    rows_with_digitization = sum(
        1
        for record
        in candidate.records
        if (
            record.digitization_uncertainty_mm_s
            is not None
        )
    )

    total = len(
        candidate.records
    )

    experimental_fraction = (
        rows_with_experimental
        / total
        if total
        else 0.0
    )

    digitization_fraction = (
        rows_with_digitization
        / total
        if total
        else 0.0
    )


    categories_separate = all(
        [
            candidate.source
            .digitization_uncertainty_separate,

            candidate.source
            .experimental_uncertainty_separate,

            candidate.source
            .model_uncertainty_separate,
        ]
    )


    diagnostics: list[
        ValidationUncertaintyRowDiagnostic
    ] = []


    for result in evaluation.evaluations:

        record = records_by_id[
            result.record_id
        ]

        absolute_error = (
            result.absolute_error_mm_s
        )

        experimental = (
            record.experimental_uncertainty_mm_s
        )

        digitization = (
            record.digitization_uncertainty_mm_s
        )


        experimental_ratio = None

        if (
            absolute_error is not None
            and experimental is not None
            and experimental > 0
            and (
                request
                .experimental_uncertainty_kind
                in SUPPORTED_EXPERIMENTAL_KINDS
            )
        ):
            experimental_ratio = (
                absolute_error
                / experimental
            )


        digitization_ratio = None

        if (
            absolute_error is not None
            and digitization is not None
            and digitization > 0
            and request.digitization_uncertainty_kind
            not in {
                "source_reported_unspecified",
                "not_available",
            }
        ):
            digitization_ratio = (
                absolute_error
                / digitization
            )


        diagnostics.append(
            ValidationUncertaintyRowDiagnostic(
                record_id=result.record_id,

                absolute_model_error_mm_s=(
                    absolute_error
                ),

                experimental_uncertainty_mm_s=(
                    experimental
                ),

                digitization_uncertainty_mm_s=(
                    digitization
                ),

                absolute_error_to_experimental_uncertainty_ratio=(
                    experimental_ratio
                ),

                absolute_error_to_digitization_uncertainty_ratio=(
                    digitization_ratio
                ),
            )
        )


    if (
        evaluation.direct_validation_gate_passed
        is not True
    ):
        status = (
            "blocked_compatibility_gate"
        )

    elif experimental_fraction < 1.0:
        status = (
            "blocked_incomplete_"
            "experimental_uncertainty"
        )

    elif (
        request.experimental_uncertainty_kind
        not in SUPPORTED_EXPERIMENTAL_KINDS
    ):
        status = (
            "blocked_experimental_"
            "uncertainty_semantics"
        )

    else:
        # Physics Baseline v0 currently exposes
        # only a descriptive residual factor.
        # It has no calibrated prediction interval.
        status = (
            "blocked_no_calibrated_"
            "prediction_interval"
        )


    calibrated_prediction_interval_available = (
        False
    )

    coverage_verification_passed = (
        False
    )


    return (
        ValidationUncertaintyAssessmentResponse(
            compatibility_gate_passed=(
                evaluation
                .direct_validation_gate_passed
            ),

            evaluated_point_count=(
                evaluation
                .evaluated_point_count
            ),

            rows_with_experimental_uncertainty=(
                rows_with_experimental
            ),

            rows_with_digitization_uncertainty=(
                rows_with_digitization
            ),

            experimental_uncertainty_completeness_fraction=(
                experimental_fraction
            ),

            digitization_uncertainty_completeness_fraction=(
                digitization_fraction
            ),

            uncertainty_categories_separate=(
                categories_separate
            ),

            calibrated_prediction_interval_available=(
                calibrated_prediction_interval_available
            ),

            uncertainty_readiness_status=(
                status
            ),

            coverage_verification_passed=(
                coverage_verification_passed
            ),

            uncertainty_calibration_claim_allowed=False,

            external_validation_claim_allowed=False,

            production_ready_claim_allowed=False,

            certification_claim_allowed=False,

            diagnostics=diagnostics,

            guardrails=[
                (
                    "Experimental uncertainty, "
                    "digitization uncertainty and "
                    "model uncertainty are never "
                    "merged implicitly."
                ),
                (
                    "Reported error bars are not "
                    "interpreted as standard "
                    "deviations unless the source "
                    "explicitly defines them that way."
                ),
                (
                    "Ratios in this response are "
                    "descriptive diagnostics and "
                    "not probabilities or "
                    "confidence levels."
                ),
                (
                    "Physics Baseline v0 does not "
                    "currently provide a calibrated "
                    "prediction interval."
                ),
                (
                    "Coverage verification remains "
                    "blocked until a calibrated "
                    "model interval exists."
                ),
                (
                    "A descriptive residual factor "
                    "must not be presented as a "
                    "prediction interval."
                ),
            ],
        )
    )
