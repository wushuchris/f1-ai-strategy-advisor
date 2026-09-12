import pytest
from pydantic import ValidationError

from src.orchestrator import run_strategy_orchestrator
from src.verifier import verify_strategy


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


def test_valid_orchestrated_strategy_is_approved():
    strategy = run_strategy_orchestrator(make_telemetry())

    result = verify_strategy(strategy)

    assert result["status"] == "Approved"
    assert result["publishable"] is True
    assert result["violations"] == []
    assert result["checks_run"] == 6


def test_prepare_to_pit_without_tire_signal_is_rejected():
    strategy = run_strategy_orchestrator(make_telemetry())
    strategy["final_action"] = "Prepare to Pit"
    strategy["priority"] = "High"

    result = verify_strategy(strategy)

    assert result["status"] == "Rejected"
    assert result["publishable"] is False
    assert any("Prepare to Pit may only" in item for item in result["violations"])


def test_tire_pit_signal_cannot_be_downgraded():
    strategy = run_strategy_orchestrator(make_telemetry(tire_temp=105.0))
    strategy["final_action"] = "Manage and Reassess"

    result = verify_strategy(strategy)

    assert result["status"] == "Rejected"
    assert any("must be preserved" in item for item in result["violations"])


def test_high_priority_signal_requires_high_priority_publication():
    strategy = run_strategy_orchestrator(make_telemetry(fuel_level=15.0))
    strategy["priority"] = "Normal"

    result = verify_strategy(strategy)

    assert result["status"] == "Rejected"
    assert any("require High publication priority" in item for item in result["violations"])


def test_maintain_with_developing_concern_is_rejected():
    strategy = run_strategy_orchestrator(make_telemetry(tire_temp=100.0))
    strategy["final_action"] = "Maintain"

    result = verify_strategy(strategy)

    assert result["status"] == "Rejected"
    assert any("Maintain may only" in item for item in result["violations"])


def test_tampered_confidence_is_rejected():
    strategy = run_strategy_orchestrator(make_telemetry())
    strategy["confidence"] = 0.99

    result = verify_strategy(strategy)

    assert result["status"] == "Rejected"
    assert any("Published confidence" in item for item in result["violations"])


def test_invalid_orchestrated_strategy_schema_is_rejected_before_verification():
    strategy = run_strategy_orchestrator(make_telemetry())
    strategy["unexpected_field"] = "not allowed"

    with pytest.raises(ValidationError):
        verify_strategy(strategy)
