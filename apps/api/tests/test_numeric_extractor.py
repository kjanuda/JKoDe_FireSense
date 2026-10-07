
import pytest

from app.analysis.numeric_extractor import (
    detect_gravity_regime,
    extract_flow,
    extract_oxygen,
    extract_pressure,
    extract_spread_rate,
    extract_thickness,
)


def test_extract_oxygen():
    values = extract_oxygen(
        "The test used 20.7 percent O2."
    )

    assert len(values) == 1

    assert (
        values[0].normalized_value
        == pytest.approx(0.207)
    )


def test_extract_pressure_atm():
    values = extract_pressure(
        "The experiment was conducted at 1 atm."
    )

    assert len(values) == 1

    assert (
        values[0].normalized_value
        == pytest.approx(101.325)
    )


def test_extract_flow():
    values = extract_flow(
        "Opposed flow velocity was 2.5 cm/s."
    )

    assert values[0].value == 2.5


def test_extract_spread_rate():
    values = extract_spread_rate(
        "Average spread rate was 2.0 mm/s."
    )

    assert values[0].value == 2.0


def test_convert_mm_min():
    values = extract_spread_rate(
        "Spread rate was 2.2 mm/min."
    )

    assert (
        values[0].normalized_value
        == pytest.approx(
            2.2 / 60.0
        )
    )


def test_extract_thickness():
    values = extract_thickness(
        "100 µm-thick PMMA sheet."
    )

    assert values[0].value == 100


def test_microgravity_detection():
    value = detect_gravity_regime(
        "The PMMA experiment was performed "
        "on the International Space Station."
    )

    assert value == "microgravity"


def test_mixed_gravity_detection():
    value = detect_gravity_regime(
        "Microgravity results were compared "
        "with normal-gravity experiments."
    )

    assert value == "mixed"


# ============================================================
# Critical regression tests
# ============================================================

def test_oxygen_does_not_capture_nitrogen():
    values = extract_oxygen(
        "The atmosphere contained "
        "20.7 percent O2 and "
        "79 percent N2."
    )

    assert len(values) == 1

    assert (
        values[0].value
        == pytest.approx(20.7)
    )


def test_oxygen_after_label():
    values = extract_oxygen(
        "The O2 level can be adjusted "
        "to 21 percent."
    )

    assert len(values) == 1

    assert (
        values[0].value
        == pytest.approx(21.0)
    )


def test_extract_spaced_micrometer():
    values = extract_thickness(
        "A 100µ m-thick PMMA sheet "
        "was tested."
    )

    assert len(values) == 1

    assert (
        values[0].value
        == pytest.approx(100.0)
    )
