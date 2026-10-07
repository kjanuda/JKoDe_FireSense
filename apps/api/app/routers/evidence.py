from app.services.validation_scientific_review import (
    ValidationScientificReviewError,
    get_validation_scientific_review_status,
)

from app.schemas.validation_scientific_review import (
    ValidationScientificReviewStatusResponse,
)

from app.services.validation_uncertainty_assessment import (
    ValidationUncertaintyAssessmentError,
    assess_validation_uncertainty,
)

from app.schemas.validation_uncertainty import (
    ValidationUncertaintyAssessmentRequest,
    ValidationUncertaintyAssessmentResponse,
)

from app.services.validation_csv_importer import (
    ValidationCsvImportError,
    import_validation_csv,
)

from app.schemas.validation_csv_import import (
    ValidationCsvImportRequest,
    ValidationCsvImportResponse,
)

from app.services.validation_source_registry import (
    ValidationSourceRegistryError,
    check_validation_source,
    get_validation_source_registry,
)

from app.schemas.validation_source_registry import (
    ValidationSourceCheckRequest,
    ValidationSourceCheckResponse,
    ValidationSourceRegistryResponse,
)

from fastapi import (
    APIRouter,
    HTTPException,
)

from app.schemas.external_comparison_evidence import (
    ExternalComparisonEvidenceResponse,
)

from app.schemas.figure_2_22_evidence import (
    Figure222EvidenceResponse,
)

from app.schemas.validation_candidate import (
    ValidationCandidateEvaluationResponse,
    ValidationCandidateRequest,
)

from app.schemas.validation_readiness import (
    ValidationReadinessResponse,
)

from app.schemas.validation_release_status import (
    ValidationReleaseStatusResponse,
)

from app.services.external_comparison_evidence import (
    ExternalComparisonEvidenceError,
    get_external_comparison_evidence,
)

from app.services.figure_2_22_evidence import (
    Figure222EvidenceError,
    get_figure_2_22_evidence,
)

from app.services.validation_candidate_evaluator import (
    ValidationCandidateEvaluationError,
    evaluate_validation_candidate,
)

from app.services.validation_readiness import (
    ValidationReadinessError,
    get_validation_readiness,
)

from app.services.validation_performance_acceptance import (
    ValidationPerformanceError,
    evaluate_performance_acceptance,
)

from app.services.validation_release_status import (
    ValidationReleaseStatusError,
    get_validation_release_status,
)


router = APIRouter(
    prefix="/api/evidence",
    tags=["Evidence"],
)


@router.get(
    "/figure-2-22",
    response_model=Figure222EvidenceResponse,
    summary=(
        "Return frozen Figure 2.22 "
        "comparison evidence"
    ),
    description=(
        "Returns frozen Figure 2.22 "
        "comparison-only experimental evidence."
    ),
)
def figure_2_22_evidence_api(
) -> Figure222EvidenceResponse:
    try:
        return get_figure_2_22_evidence()

    except Figure222EvidenceError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc


@router.get(
    "/external-comparison",
    response_model=ExternalComparisonEvidenceResponse,
    summary=(
        "Return independent external "
        "comparison evidence"
    ),
    description=(
        "Returns the frozen Ries 2024 "
        "comparison against FireSense v0. "
        "It is not completed independent "
        "external validation."
    ),
)
def external_comparison_evidence_api(
) -> ExternalComparisonEvidenceResponse:
    try:
        return get_external_comparison_evidence()

    except ExternalComparisonEvidenceError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc


@router.get(
    "/validation-readiness",
    response_model=ValidationReadinessResponse,
    summary=(
        "Return independent validation "
        "readiness status"
    ),
    description=(
        "Evaluates the frozen independent-"
        "validation acceptance protocol and "
        "screened external evidence."
    ),
)
def validation_readiness_api(
) -> ValidationReadinessResponse:
    try:
        return get_validation_readiness()

    except ValidationReadinessError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc


@router.post(
    "/validation-candidate/evaluate",
    response_model=ValidationCandidateEvaluationResponse,
    summary=(
        "Evaluate an independent external "
        "validation candidate"
    ),
    description=(
        "Checks a candidate holdout dataset "
        "against the frozen FireSense v0 "
        "scientific acceptance gate and runs "
        "the frozen Physics Baseline v0 on "
        "eligible rows. Passing this gate does "
        "not by itself authorize an external-"
        "validation or production-ready claim."
    ),
)
def validation_candidate_evaluation_api(
    request: ValidationCandidateRequest,
) -> ValidationCandidateEvaluationResponse:
    try:
        return evaluate_validation_candidate(
            request
        )

    except (
        ValidationCandidateEvaluationError,
        ValidationReadinessError,
    ) as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

@router.get(
    "/validation-release-status",
    response_model=ValidationReleaseStatusResponse,
    summary=(
        "Return trusted independent "
        "validation release status"
    ),
    description=(
        "Returns the fail-closed FireSense "
        "independent-validation release state. "
        "Validation can only be promoted from "
        "a scientifically reviewed frozen "
        "artifact whose SHA-256 is pinned "
        "in source code."
    ),
)
def validation_release_status_api(
) -> ValidationReleaseStatusResponse:
    try:
        return get_validation_release_status()

    except ValidationReleaseStatusError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

@router.post(
    "/validation-candidate/performance",
    summary=(
        "Evaluate validation candidate "
        "performance thresholds"
    ),
    description=(
        "Runs the FireSense v0 candidate "
        "compatibility evaluator and then "
        "checks the resulting holdout metrics "
        "against the frozen pre-registered "
        "performance acceptance protocol. "
        "Passing this endpoint does not "
        "automatically promote scientific "
        "validation status."
    ),
)
def validation_candidate_performance_api(
    request: ValidationCandidateRequest,
) -> dict:
    try:
        evaluation = (
            evaluate_validation_candidate(
                request
            )
        )

        return (
            evaluate_performance_acceptance(
                evaluation
            )
        )

    except (
        ValidationCandidateEvaluationError,
        ValidationReadinessError,
        ValidationPerformanceError,
    ) as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

@router.get(
    "/validation-source-registry",
    response_model=ValidationSourceRegistryResponse,
    summary=(
        "Return frozen validation "
        "source provenance registry"
    ),
)
def validation_source_registry_api(
) -> ValidationSourceRegistryResponse:
    try:
        return get_validation_source_registry()

    except ValidationSourceRegistryError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc


@router.post(
    "/validation-source-check",
    response_model=ValidationSourceCheckResponse,
    summary=(
        "Check validation-source "
        "provenance status"
    ),
)
def validation_source_check_api(
    request: ValidationSourceCheckRequest,
) -> ValidationSourceCheckResponse:
    try:
        return check_validation_source(
            request.source_id
        )

    except ValidationSourceRegistryError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

@router.post(
    "/validation-dataset/import-csv",
    response_model=ValidationCsvImportResponse,
    summary=(
        "Import trusted external "
        "validation CSV evidence"
    ),
    description=(
        "Parses a candidate external holdout "
        "dataset, verifies source provenance "
        "through the frozen validation-source "
        "registry, preserves training exclusion, "
        "and only enters the direct validation "
        "and performance gates when the source "
        "has been scientifically approved."
    ),
)
def validation_dataset_import_csv_api(
    request: ValidationCsvImportRequest,
) -> ValidationCsvImportResponse:
    try:
        return import_validation_csv(
            request
        )

    except ValidationCsvImportError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

@router.post(
    "/validation-candidate/uncertainty",
    response_model=ValidationUncertaintyAssessmentResponse,
    summary=(
        "Assess independent-validation "
        "uncertainty readiness"
    ),
    description=(
        "Checks uncertainty completeness and "
        "semantics while preserving separation "
        "between experimental, digitization and "
        "model uncertainty. FireSense v0 fails "
        "closed because its current baseline "
        "does not provide a calibrated "
        "prediction interval."
    ),
)
def validation_candidate_uncertainty_api(
    request: ValidationUncertaintyAssessmentRequest,
) -> ValidationUncertaintyAssessmentResponse:
    try:
        return assess_validation_uncertainty(
            request
        )

    except ValidationUncertaintyAssessmentError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

@router.get(
    "/validation-scientific-review-status",
    response_model=ValidationScientificReviewStatusResponse,
    summary=(
        "Return scientific validation "
        "review status"
    ),
    description=(
        "Verifies the frozen validation "
        "package, performance gate, calibrated "
        "uncertainty coverage, scientific-review "
        "checks and SHA-256 bindings. This "
        "endpoint does not itself promote "
        "external-validation status."
    ),
)
def validation_scientific_review_status_api(
) -> ValidationScientificReviewStatusResponse:
    try:
        return (
            get_validation_scientific_review_status()
        )

    except ValidationScientificReviewError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

