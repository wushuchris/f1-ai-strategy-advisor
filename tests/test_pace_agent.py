import pytest
from pydantic import ValidationError

from src.agents.pace_agent import analyze_pace


def make_telemetry(**overrides):
    telemetry = {
        "lap": 4,
        "lap_time": 85.4,
        "tire_temp": 96.0,
        "fuel_level": 80.0,
        "track_condition": "Dry",
    }
    telemetry.update(overrides)
    return telemetry


def make_history(track_condition="Dry", lap_times=(85.0, 85.2, 85.4)):
    return [
        {
            "lap": index,
            "lap_time": lap_time,
            "tire_temp": 95.0,
            "fuel_level": 90.0 - index,
            "track_condition": track_condition,
        }
        for index, lap_time in enumerate(lap_times, start=1)
    ]


def test_insufficient_history_returns_monitoring_state():
    result = analyze_pace(make_telemetry(), history=make_history(lap_times=(85.0, 85.2)))

    assert result["status"] == "Monitoring"
    assert result["action"] == "Monitor"
    assert result["history_laps"] == 2
    assert result["confidence"] == 0.60


def test_recent_baseline_on_target_returns_maintain():
    result = analyze_pace(make_telemetry(lap_time=85.4), history=make_history())

    assert result["status"] == "On Target"
    assert result["action"] == "Maintain"
    assert result["reference_lap_time"] == 85.2
    assert result["delta_to_reference"] == 0.2
    assert result["history_laps"] == 3


def test_recent_baseline_degradation_returns_review():
    result = analyze_pace(make_telemetry(lap_time=86.0), history=make_history())

    assert result["status"] == "Degraded"
    assert result["action"] == "Review Pace Loss"
    assert result["delta_to_reference"] == 0.8


def test_recent_baseline_critical_loss_returns_manage():
    result = analyze_pace(make_telemetry(lap_time=86.8), history=make_history())

    assert result["status"] == "Critical"
    assert result["action"] == "Manage and Reassess"
    assert result["delta_to_reference"] == 1.6
    assert result["confidence"] == 0.95


def test_only_same_condition_laps_form_reference_baseline():
    history = make_history(track_condition="Dry") + make_history(
        track_condition="Wet",
        lap_times=(89.0, 89.2, 89.4),
    )
    current = make_telemetry(track_condition="Wet", lap_time=89.5)

    result = analyze_pace(current, history=history)

    assert result["status"] == "On Target"
    assert result["reference_lap_time"] == 89.2
    assert result["delta_to_reference"] == 0.3
    assert result["history_laps"] == 3


def test_invalid_current_telemetry_is_rejected_before_pace_analysis():
    with pytest.raises(ValidationError):
        analyze_pace(make_telemetry(lap_time=-1.0), history=make_history())


def test_invalid_history_telemetry_is_rejected_before_pace_analysis():
    history = make_history()
    history[0]["fuel_level"] = 120.0

    with pytest.raises(ValidationError):
        analyze_pace(make_telemetry(), history=history)
