import pytest
from pydantic import ValidationError

from src.orchestrator import run_strategy_orchestrator


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


def test_stable_state_publishes_maintain():
    result = run_strategy_orchestrator(make_telemetry(), history=make_history())

    assert result["final_action"] == "Maintain"
    assert result["priority"] == "Normal"
    assert result["tire"]["risk"] == "Low"
    assert result["pace"]["status"] == "On Target"
    assert result["pace"]["reference_lap_time"] == 85.2
    assert result["track"]["risk"] == "Low"
    assert result["confidence"] == 0.90


def test_insufficient_pace_history_can_publish_bounded_maintain():
    result = run_strategy_orchestrator(
        make_telemetry(),
        history=make_history(lap_times=(85.0, 85.2)),
    )

    assert result["pace"]["status"] == "Monitoring"
    assert result["final_action"] == "Maintain"
    assert result["priority"] == "Normal"
    assert result["confidence"] == 0.60
    assert "baseline" in result["summary"].lower()


def test_tire_pit_signal_controls_final_action():
    result = run_strategy_orchestrator(
        make_telemetry(tire_temp=105.0),
        history=make_history(),
    )

    assert result["final_action"] == "Prepare to Pit"
    assert result["priority"] == "High"
    assert result["tire"]["action"] == "Prepare to Pit"


def test_critical_pace_escalates_to_manage_and_reassess():
    result = run_strategy_orchestrator(
        make_telemetry(lap_time=87.0),
        history=make_history(),
    )

    assert result["final_action"] == "Manage and Reassess"
    assert result["priority"] == "High"
    assert result["pace"]["status"] == "Critical"


def test_wet_track_escalates_to_manage_and_reassess():
    result = run_strategy_orchestrator(
        make_telemetry(track_condition="Wet", lap_time=89.5),
        history=make_history(track_condition="Wet", lap_times=(89.0, 89.2, 89.4)),
    )

    assert result["track"]["risk"] == "Elevated"
    assert result["track"]["action"] == "Adapt to Wet Conditions"
    assert result["final_action"] == "Manage and Reassess"
    assert result["priority"] == "High"


def test_high_priority_rules_escalate_without_forcing_pit():
    result = run_strategy_orchestrator(
        make_telemetry(fuel_level=15.0),
        history=make_history(),
    )

    assert result["rules"]["priority"] == "High"
    assert result["final_action"] == "Manage and Reassess"
    assert result["priority"] == "High"


def test_developing_specialist_concern_requests_review():
    result = run_strategy_orchestrator(
        make_telemetry(tire_temp=100.0),
        history=make_history(),
    )

    assert result["final_action"] == "Review Strategy"
    assert result["priority"] == "Normal"
    assert result["tire"]["risk"] == "Medium"


def test_tire_specialist_failure_uses_conservative_fallback(monkeypatch):
    def fail_tire(_):
        raise RuntimeError("simulated tire specialist failure")

    monkeypatch.setattr("src.orchestrator.analyze_tires", fail_tire)

    result = run_strategy_orchestrator(make_telemetry(), history=make_history())

    assert result["tire"]["risk"] == "High"
    assert result["tire"]["action"] == "Manage"
    assert result["tire"]["confidence"] == 0.0
    assert "fallback" in result["tire"]["rationale"].lower()
    assert result["final_action"] == "Manage and Reassess"
    assert result["priority"] == "High"


def test_pace_specialist_failure_uses_conservative_fallback(monkeypatch):
    def fail_pace(_, history=None):
        raise RuntimeError("simulated pace specialist failure")

    monkeypatch.setattr("src.orchestrator.analyze_pace", fail_pace)

    result = run_strategy_orchestrator(make_telemetry(), history=make_history())

    assert result["pace"]["status"] == "Critical"
    assert result["pace"]["action"] == "Manage and Reassess"
    assert result["pace"]["confidence"] == 0.0
    assert "fallback" in result["pace"]["rationale"].lower()
    assert result["final_action"] == "Manage and Reassess"
    assert result["priority"] == "High"


def test_track_specialist_failure_uses_neutral_reassessment_fallback(monkeypatch):
    def fail_track(_):
        raise RuntimeError("simulated track specialist failure")

    monkeypatch.setattr("src.orchestrator.analyze_track", fail_track)

    result = run_strategy_orchestrator(make_telemetry(), history=make_history())

    assert result["track"]["condition"] == "Dry"
    assert result["track"]["risk"] == "Elevated"
    assert result["track"]["action"] == "Reassess Track State"
    assert result["track"]["confidence"] == 0.0
    assert "fallback" in result["track"]["rationale"].lower()
    assert result["final_action"] == "Manage and Reassess"
    assert result["priority"] == "High"


def test_invalid_telemetry_is_rejected_before_orchestration():
    with pytest.raises(ValidationError):
        run_strategy_orchestrator(
            make_telemetry(fuel_level=120.0),
            history=make_history(),
        )
