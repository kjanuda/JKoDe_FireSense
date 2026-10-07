import pytest
from pydantic import ValidationError

from app.schemas.experiment import ExperimentRecord


def test_valid_experiment_record():
    record = ExperimentRecord(
        record_id="EXP-001",
        study_id="STUDY-001",
        source_id="SOURCE-001",
        material_name="PMMA",
        geometry="thin_sheet",
        thickness_mm=0.075,
        gravity_g=0.0,
        oxygen_fraction=0.21,
        pressure_kpa=100.0,
        oxygen_partial_pressure_kpa=21.0,
        flow_velocity_cm_s=5.0,
        flow_direction="opposed",
        sustained_flame=True,
        extinguished=False,
        flame_spread_rate_mm_s=0.8,
        value_source="table",
        source_page=12,
        evidence_text="Example experimental evidence.",
        verified=True,
    )

    assert record.material_name == "PMMA"
    assert record.oxygen_partial_pressure_kpa == 21.0


def test_partial_pressure_is_calculated_automatically():
    record = ExperimentRecord(
        record_id="EXP-002",
        study_id="STUDY-001",
        source_id="SOURCE-001",
        material_name="PMMA",
        gravity_g=0.16,
        oxygen_fraction=0.235,
        pressure_kpa=70.0,
        value_source="text",
        source_page=5,
        evidence_text="Example Moon-condition record.",
    )

    assert record.oxygen_partial_pressure_kpa == pytest.approx(
        16.45
    )


def test_incorrect_partial_pressure_is_rejected():
    with pytest.raises(ValidationError):
        ExperimentRecord(
            record_id="EXP-003",
            study_id="STUDY-001",
            source_id="SOURCE-001",
            material_name="PMMA",
            gravity_g=0.16,
            oxygen_fraction=0.235,
            pressure_kpa=70.0,
            oxygen_partial_pressure_kpa=25.0,
            value_source="table",
            source_page=5,
            evidence_text="Invalid test record.",
        )