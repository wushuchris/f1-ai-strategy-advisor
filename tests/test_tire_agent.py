import pytest
from pydantic import ValidationError

from src.agents.tire_agent import analyze_tires


def make_telemetry(**overrides):
    telemetry = {
        "lap": 5,
        "lap_time": 85.0,
        "tire_temp": 96.0,
        "fuel_level": 80.0,
        "track_condition": "Dry",
    }
    telemetry.update(overrides)
    return telemetry


def test_stable_dry_tires_return_low_risk_maintain():
    result = analyze_tires(make_telemetry())

    assert result["risk"] == "Low"
    assert result["action"] == "Maintain"
    assert result["estimated_remaining_laps"] == 8
    assert result["confidence"] == 0.90


def test_elevated_temperature_returns_medium_risk_manage():
    result = analyze_tires(make_telemetry(tire_temp=100.0))

    assert result["risk"] == "Medium"
    assert result["action"] == "Manage"
    assert result["estimated_remaining_laps"] == 5


def test_long_stint_returns_medium_risk_manage():
    result = analyze_tires(make_telemetry(lap=20, tire_temp=97.0))

    assert result["risk"] == "Medium"
    assert result["action"] == "Manage"


def test_high_temperature_returns_high_risk_prepare_to_pit():
    result = analyze_tires(make_telemetry(tire_temp=105.0))

    assert result["risk"] == "High"
    assert result["action"] == "Prepare to Pit"
    assert result["estimated_remaining_laps"] == 2
    assert result["confidence"] == 0.95


def test_wet_conditions_raise_otherwise_low_risk_to_medium():
    result = analyze_tires(make_telemetry(track_condition="Wet", tire_temp=95.0))

    assert result["risk"] == "Medium"
    assert result["action"] == "Manage"
    assert result["estimated_remaining_laps"] == 5
    assert result["confidence"] == 0.80


def test_invalid_telemetry_is_rejected_before_analysis():
    with pytest.raises(ValidationError):
        analyze_tires(make_telemetry(fuel_level=120.0))
