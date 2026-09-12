import pytest
from pydantic import ValidationError

from src.agents.pace_agent import analyze_pace


def make_telemetry(**overrides):
    telemetry = {
        "lap": 5,
        "lap_time": 85.5,
        "tire_temp": 96.0,
        "fuel_level": 80.0,
        "track_condition": "Dry",
    }
    telemetry.update(overrides)
    return telemetry


def test_dry_pace_on_target_returns_maintain():
    result = analyze_pace(make_telemetry(lap_time=85.8))

    assert result["status"] == "On Target"
    assert result["action"] == "Maintain"
    assert result["target_lap_time"] == 85.5
    assert result["delta_to_target"] == 0.3


def test_dry_pace_degradation_returns_review():
    result = analyze_pace(make_telemetry(lap_time=86.5))

    assert result["status"] == "Degraded"
    assert result["action"] == "Review Pace Loss"
    assert result["delta_to_target"] == 1.0


def test_dry_critical_pace_loss_returns_manage():
    result = analyze_pace(make_telemetry(lap_time=87.5))

    assert result["status"] == "Critical"
    assert result["action"] == "Manage and Reassess"
    assert result["delta_to_target"] == 2.0
    assert result["confidence"] == 0.95


def test_wet_conditions_use_wet_target():
    result = analyze_pace(
        make_telemetry(track_condition="Wet", lap_time=89.7)
    )

    assert result["status"] == "On Target"
    assert result["target_lap_time"] == 89.5
    assert result["delta_to_target"] == 0.2


def test_wet_pace_degradation_is_track_aware():
    result = analyze_pace(
        make_telemetry(track_condition="Wet", lap_time=90.5)
    )

    assert result["status"] == "Degraded"
    assert result["action"] == "Review Pace Loss"


def test_invalid_telemetry_is_rejected_before_pace_analysis():
    with pytest.raises(ValidationError):
        analyze_pace(make_telemetry(lap_time=-1.0))
