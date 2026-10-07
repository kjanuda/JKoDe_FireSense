import csv
import io
import math

from app.schemas.validation_candidate import (
    ValidationCandidateRequest,
    ValidationCandidateSource,
    ValidationCandidateRecord,
)

from app.schemas.validation_csv_import import (
    ValidationCsvImportRequest,
    ValidationCsvImportResponse,
)

from app.services.validation_candidate_evaluator import (
    evaluate_validation_candidate,
)

from app.services.validation_performance_acceptance import (
    evaluate_performance_acceptance,
)

from app.services.validation_source_registry import (
    check_validation_source,
)


class ValidationCsvImportError(
    RuntimeError
):
    pass


REQUIRED_COLUMNS = {
    "record_id",
    "source_id",
    "experiment_id",
    "material",
    "geometry_family",
    "thickness_um",
    "oxygen_percent",
    "pressure_kpa",
    "gravity_regime",
    "transport_configuration",
    "flow_mm_s",
    "observed_spread_rate_mm_s",
    "experimental_uncertainty_mm_s",
    "digitization_uncertainty_mm_s",
    "measurement_method",
    "source_reference",
}


MAX_IMPORTED_ROWS = 10_000


def _optional_float(
    value: str | None,
) -> float | None:

    if value is None:
        return None

    cleaned = value.strip()

    if not cleaned:
        return None

    try:
        parsed = float(
            cleaned
        )

    except ValueError as exc:
        raise ValidationCsvImportError(
            f"Invalid numeric value: {value}"
        ) from exc

    if not math.isfinite(
        parsed
    ):
        raise ValidationCsvImportError(
            f"Non-finite numeric value: {value}"
        )

    return parsed


def _required_float(
    row: dict[str, str],
    column: str,
) -> float:

    value = (
        row.get(
            column,
            "",
        )
        .strip()
    )

    if not value:
        raise ValidationCsvImportError(
            f"Missing required numeric "
            f"value for {column}."
        )

    try:
        parsed = float(
            value
        )

    except ValueError as exc:
        raise ValidationCsvImportError(
            f"Invalid numeric value for "
            f"{column}: {value}"
        ) from exc

    if not math.isfinite(
        parsed
    ):
        raise ValidationCsvImportError(
            f"Non-finite numeric value for "
            f"{column}: {value}"
        )

    return parsed


def _parse_records(
    request: ValidationCsvImportRequest,
) -> list[ValidationCandidateRecord]:

    raw = request.csv_text.lstrip(
        "\ufeff"
    )

    reader = csv.DictReader(
        io.StringIO(
            raw
        )
    )

    if reader.fieldnames is None:
        raise ValidationCsvImportError(
            "CSV header is missing."
        )

    columns = {
        column.strip()
        for column
        in reader.fieldnames
        if column is not None
    }

    missing = (
        REQUIRED_COLUMNS
        - columns
    )

    if missing:
        raise ValidationCsvImportError(
            "CSV is missing required columns: "
            + ", ".join(
                sorted(
                    missing
                )
            )
        )


    records: list[
        ValidationCandidateRecord
    ] = []

    seen_record_ids: set[str] = set()


    for row_number, row in enumerate(
        reader,
        start=2,
    ):
        if (
            len(records)
            >= MAX_IMPORTED_ROWS
        ):
            raise ValidationCsvImportError(
                "CSV exceeds the maximum "
                "allowed row count of "
                f"{MAX_IMPORTED_ROWS}."
            )

        record_id = (
            row.get(
                "record_id",
                "",
            )
            .strip()
        )

        if not record_id:
            raise ValidationCsvImportError(
                f"CSV row {row_number} "
                "has no record_id."
            )

        if record_id in seen_record_ids:
            raise ValidationCsvImportError(
                f"Duplicate record_id: "
                f"{record_id}"
            )

        seen_record_ids.add(
            record_id
        )


        row_source_id = (
            row.get(
                "source_id",
                "",
            )
            .strip()
        )

        if (
            row_source_id.casefold()
            != request.source_id
            .strip()
            .casefold()
        ):
            raise ValidationCsvImportError(
                f"CSV row {row_number} "
                "source_id does not match "
                "the requested source_id."
            )


        gravity = (
            row.get(
                "gravity_regime",
                "",
            )
            .strip()
        )

        if gravity not in {
            "microgravity",
            "normal_gravity",
        }:
            raise ValidationCsvImportError(
                f"CSV row {row_number} has "
                f"unsupported gravity_regime: "
                f"{gravity}"
            )


        source_reference = (
            row.get(
                "source_reference",
                "",
            )
            .strip()
        )

        if not source_reference:
            raise ValidationCsvImportError(
                f"CSV row {row_number} "
                "has no source_reference."
            )


        records.append(
            ValidationCandidateRecord(
                record_id=record_id,

                material=(
                    row.get(
                        "material",
                        "",
                    )
                    .strip()
                ),

                geometry_family=(
                    row.get(
                        "geometry_family",
                        "",
                    )
                    .strip()
                ),

                thickness_um=(
                    _required_float(
                        row,
                        "thickness_um",
                    )
                ),

                oxygen_percent=(
                    _required_float(
                        row,
                        "oxygen_percent",
                    )
                ),

                pressure_kpa=(
                    _required_float(
                        row,
                        "pressure_kpa",
                    )
                ),

                gravity_regime=gravity,

                transport_configuration=(
                    row.get(
                        "transport_configuration",
                        "",
                    )
                    .strip()
                ),

                flow_mm_s=(
                    _optional_float(
                        row.get(
                            "flow_mm_s"
                        )
                    )
                ),

                observed_spread_rate_mm_s=(
                    _required_float(
                        row,
                        "observed_spread_rate_mm_s",
                    )
                ),

                experimental_uncertainty_mm_s=(
                    _optional_float(
                        row.get(
                            "experimental_uncertainty_mm_s"
                        )
                    )
                ),

                digitization_uncertainty_mm_s=(
                    _optional_float(
                        row.get(
                            "digitization_uncertainty_mm_s"
                        )
                    )
                ),

                # Validation imports are always
                # holdout and training-ineligible.
                training_eligible=False,

                validation_holdout=True,

                provenance_reference=(
                    source_reference
                ),
            )
        )


    if not records:
        raise ValidationCsvImportError(
            "CSV contains no data rows."
        )


    return records


def import_validation_csv(
    request: ValidationCsvImportRequest,
) -> ValidationCsvImportResponse:

    records = _parse_records(
        request
    )

    source_check = (
        check_validation_source(
            request.source_id
        )
    )


    guardrails = [
        (
            "CSV import cannot promote "
            "scientific validation status."
        ),
        (
            "Imported rows are permanently "
            "training-ineligible holdout "
            "evidence."
        ),
        (
            "Source independence comes from "
            "the frozen provenance registry, "
            "not from CSV metadata."
        ),
        (
            "Unknown sources require scientific "
            "provenance review before direct "
            "validation evaluation."
        ),
        (
            "A comparison-only source cannot "
            "enter the direct validation gate."
        ),
    ]


    if not source_check.known_source:
        return ValidationCsvImportResponse(
            dataset_id=request.dataset_id,
            dataset_version=request.dataset_version,
            source_id=request.source_id,

            imported_row_count=len(
                records
            ),

            import_status=(
                "provenance_review_required"
            ),

            source_known=False,

            source_independence_status=(
                source_check
                .independence_status
            ),

            registry_direct_validation_eligible=False,

            validation_evaluation=None,

            performance_evaluation=None,

            external_validation_claim_allowed=False,
            production_ready_claim_allowed=False,
            certification_claim_allowed=False,

            guardrails=guardrails,
        )


    if (
        source_check.independence_status
        != "independent_external"
    ):
        return ValidationCsvImportResponse(
            dataset_id=request.dataset_id,
            dataset_version=request.dataset_version,
            source_id=request.source_id,

            imported_row_count=len(
                records
            ),

            import_status=(
                "rejected_non_independent_source"
            ),

            source_known=True,

            source_independence_status=(
                source_check
                .independence_status
            ),

            registry_direct_validation_eligible=False,

            validation_evaluation=None,

            performance_evaluation=None,

            external_validation_claim_allowed=False,
            production_ready_claim_allowed=False,
            certification_claim_allowed=False,

            guardrails=guardrails,
        )


    if (
        source_check.direct_validation_eligible
        is not True
    ):
        return ValidationCsvImportResponse(
            dataset_id=request.dataset_id,
            dataset_version=request.dataset_version,
            source_id=request.source_id,

            imported_row_count=len(
                records
            ),

            import_status=(
                "comparison_only_source"
            ),

            source_known=True,

            source_independence_status=(
                source_check
                .independence_status
            ),

            registry_direct_validation_eligible=False,

            validation_evaluation=None,

            performance_evaluation=None,

            external_validation_claim_allowed=False,
            production_ready_claim_allowed=False,
            certification_claim_allowed=False,

            guardrails=guardrails,
        )


    candidate = ValidationCandidateRequest(
        dataset_id=request.dataset_id,

        dataset_version=(
            request.dataset_version
        ),

        source=ValidationCandidateSource(
            source_id=request.source_id,

            source_title=(
                request.source_title
            ),

            provenance_reference=(
                request.provenance_reference
            ),

            # These independence facts are now
            # derived from the trusted registry.
            independent_publication_or_dataset=True,

            independent_experimental_campaign=True,

            not_firesense_training_source=True,

            not_reused_bass_ii_rows=True,

            experimental_data_only=(
                request.experimental_data_only
            ),

            measurement_quantity=(
                request.measurement_quantity
            ),

            measurement_definition_matches=(
                request
                .measurement_definition_matches
            ),

            cross_calibration_available=(
                request
                .cross_calibration_available
            ),

            normal_gravity_transport_equivalence_established=(
                request
                .normal_gravity_transport_equivalence_established
            ),

            uncertainty_or_variability_metadata_preserved=(
                request
                .uncertainty_or_variability_metadata_preserved
            ),

            digitization_uncertainty_separate=(
                request
                .digitization_uncertainty_separate
            ),

            experimental_uncertainty_separate=(
                request
                .experimental_uncertainty_separate
            ),

            model_uncertainty_separate=(
                request
                .model_uncertainty_separate
            ),
        ),

        records=records,
    )


    evaluation = (
        evaluate_validation_candidate(
            candidate
        )
    )

    performance = (
        evaluate_performance_acceptance(
            evaluation
        )
    )


    return ValidationCsvImportResponse(
        dataset_id=request.dataset_id,

        dataset_version=(
            request.dataset_version
        ),

        source_id=request.source_id,

        imported_row_count=len(
            records
        ),

        import_status=(
            "evaluated_direct_validation_candidate"
        ),

        source_known=True,

        source_independence_status=(
            source_check
            .independence_status
        ),

        registry_direct_validation_eligible=True,

        validation_evaluation=(
            evaluation
        ),

        performance_evaluation=(
            performance
        ),

        external_validation_claim_allowed=False,

        production_ready_claim_allowed=False,

        certification_claim_allowed=False,

        guardrails=guardrails,
    )
