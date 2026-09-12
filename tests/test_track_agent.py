import pytest
from pydantic import ValidationError

from src.agents.track_agent import analyze_track


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


def test_dry_track_is_low_risk_and_maintain():
    result = analyze_track(make_telemetry())

    assert result["condition"] == "Dry"
    assert result["risk"] == "Low"
    assert result["action"] == "Maintain"
    assert result["confidence"] == 0.95


def test_wet_track_is_elevated_and_requires_adaptation():
    result = analyze_track(make_telemetry(track_condition="Wet"))

    assert result["condition"] == "Wet"
    assert result["risk"] == "Elevated"
    assert result["action"] == "Adapt to Wet Conditions"
    assert result["confidence"] == 0.95
    assert "no weather forecast is inferred" in result["rationale"]


def test_invalid_track_condition_is_rejected():
    with pytest.raises(ValidationError):
        analyze_track(make_telemetry(track_condition="Damp"))


def test_extra_telemetry_field_is_rejected():
    with pytest.raises(ValidationError):
        analyze_track(make_telemetry(weather_forecast="Rain in 5 minutes"))
