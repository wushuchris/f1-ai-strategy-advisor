import pytest
from pydantic import ValidationError

from src.orchestrator import run_strategy_orchestrator


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


def test_stable_state_publishes_maintain():
    result = run_strategy_orchestrator(make_telemetry())

    assert result["final_action"] == "Maintain"
    assert result["priority"] == "Normal"
    assert result["tire"]["risk"] == "Low"
    assert result["pace"]["status"] == "On Target"
    assert result["confidence"] == 0.90


def test_tire_pit_signal_controls_final_action():
    result = run_strategy_orchestrator(make_telemetry(tire_temp=105.0))

    assert result["final_action"] == "Prepare to Pit"
    assert result["priority"] == "High"
    assert result["tire"]["action"] == "Prepare to Pit"


def test_critical_pace_escalates_to_manage_and_reassess():
    result = run_strategy_orchestrator(make_telemetry(lap_time=88.0))

    assert result["final_action"] == "Manage and Reassess"
    assert result["priority"] == "High"
    assert result["pace"]["status"] == "Critical"


def test_high_priority_rules_escalate_without_forcing_pit():
    result = run_strategy_orchestrator(make_telemetry(fuel_level=15.0))

    assert result["rules"]["priority"] == "High"
    assert result["final_action"] == "Manage and Reassess"
    assert result["priority"] == "High"


def test_developing_specialist_concern_requests_review():
    result = run_strategy_orchestrator(make_telemetry(tire_temp=100.0))

    assert result["final_action"] == "Review Strategy"
    assert result["priority"] == "Normal"
    assert result["tire"]["risk"] == "Medium"


def test_invalid_telemetry_is_rejected_before_orchestration():
    with pytest.raises(ValidationError):
        run_strategy_orchestrator(make_telemetry(fuel_level=120.0))
