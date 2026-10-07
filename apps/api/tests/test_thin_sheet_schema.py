import pytest
from pydantic import ValidationError

from app.schemas.thin_sheet import (
    ThinSheetExperimentRecord,
)


def test_valid_thin_sheet_record():
    record = ThinSheetExperimentRecord(
        record_id="TS-001",
        source_id="SRC-NASA-20210011385",
        study_id="BASSII-CH2.3-THIN-SHEET",
        thickness_um=100,
        width_mm=20,
        length_mm=95,

        gravity_regime="microgravity",
        gravity_g=None,
        reported_gravity_label="0g",

        oxygen_fraction=0.207,
        pressure_kpa=101.325,

        flow_velocity_cm_s=3.0,
        flow_direction="opposed",

        flame_spread_rate_mm_s=2.2,
        sustained_flame=True,

        observation_type="spread_rate",

        outcome_summary_method=(
            "figure_digitized_point"
        ),

        value_source="figure_digitized",

        source_page=48,
        figure_ref="2.19",
        figure_panel="B",

        evidence_text=(
            "Example verified Figure 2.19 record."
        ),

        estimated_from_figure=True,
        overlay_verified=True,
    )

    assert record.material_name == "PMMA"

    assert record.geometry == "thin_sheet"

    assert (
        record.oxygen_partial_pressure_kpa
        == pytest.approx(20.974275)
    )


def test_microgravity_is_not_exact_zero_g():

    with pytest.raises(
        ValidationError
    ):
        ThinSheetExperimentRecord(
            record_id="TS-MG-INVALID",
            source_id="SRC-001",
            study_id="STUDY-001",
            thickness_um=100,

            gravity_regime="microgravity",
            gravity_g=0.0,

            flame_spread_rate_mm_s=2.2,

            observation_type="spread_rate",

            outcome_summary_method=(
                "source_reported_value"
            ),

            value_source="text",

            source_page=48,

            evidence_text="Test.",
        )


def test_record_requires_outcome():

    with pytest.raises(
        ValidationError
    ):
        ThinSheetExperimentRecord(
            record_id="TS-002",
            source_id="SRC-NASA-20210011385",
            study_id="BASSII-CH2.3-THIN-SHEET",
            thickness_um=100,

            gravity_regime="microgravity",
            gravity_g=None,

            oxygen_fraction=0.21,
            pressure_kpa=101.325,

            observation_type="spread_rate",

            outcome_summary_method=(
                "source_reported_value"
            ),

            value_source="text",

            source_page=48,

            evidence_text="No outcome.",
        )