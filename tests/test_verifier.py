import pytest
from pydantic import ValidationError

from src.orchestrator import run_strategy_orchestrator
from src.verifier import verify_strategy


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


def test_valid_orchestrated_strategy_is_approved():
    strategy = run_strategy_orchestrator(make_telemetry(), history=make_history())

    result = verify_strategy(strategy)

    assert result["status"] == "Approved"
    assert result["publishable"] is True
    assert result["violations"] == []
    assert result["checks_run"] == 6


def test_monitoring_pace_state_can_be_approved_with_lower_confidence():
    strategy = run_strategy_orchestrator(
        make_telemetry(),
        history=make_history(lap_times=(85.0, 85.2)),
    )

    result = verify_strategy(strategy)

    assert strategy["pace"]["status"] == "Monitoring"
    assert strategy["confidence"] == 0.60
    assert result["status"] == "Approved"
    assert result["publishable"] is True


def test_prepare_to_pit_without_tire_signal_is_rejected():
    strategy = run_strategy_orchestrator(make_telemetry(), history=make_history())
    strategy["final_action"] = "Prepare to Pit"
    strategy["priority"] = "High"

    result = verify_strategy(strategy)

    assert result["status"] == "Rejected"
    assert result["publishable"] is False
    assert any("Prepare to Pit may only" in item for item in result["violations"])


def test_tire_pit_signal_cannot_be_downgraded():
    strategy = run_strategy_orchestrator(
        make_telemetry(tire_temp=105.0),
        history=make_history(),
    )
    strategy["final_action"] = "Manage and Reassess"

    result = verify_strategy(strategy)

    assert result["status"] == "Rejected"
    assert any("must be preserved" in item for item in result["violations"])


def test_high_priority_signal_requires_high_priority_publication():
    strategy = run_strategy_orchestrator(
        make_telemetry(fuel_level=15.0),
        history=make_history(),
    )
    strategy["priority"] = "Normal"

    result = verify_strategy(strategy)

    assert result["status"] == "Rejected"
    assert any("require High publication priority" in item for item in result["violations"])


def test_wet_track_signal_requires_high_priority_publication():
    strategy = run_strategy_orchestrator(
        make_telemetry(track_condition="Wet", lap_time=89.5),
        history=make_history(track_condition="Wet", lap_times=(89.0, 89.2, 89.4)),
    )
    strategy["priority"] = "Normal"

    result = verify_strategy(strategy)

    assert result["status"] == "Rejected"
    assert any("require High publication priority" in item for item in result["violations"])


def test_maintain_with_developing_concern_is_rejected():
    strategy = run_strategy_orchestrator(
        make_telemetry(tire_temp=100.0),
        history=make_history(),
    )
    strategy["final_action"] = "Maintain"

    result = verify_strategy(strategy)

    assert result["status"] == "Rejected"
    assert any("Maintain may only" in item for item in result["violations"])


def test_maintain_with_elevated_track_risk_is_rejected():
    strategy = run_strategy_orchestrator(
        make_telemetry(track_condition="Wet", lap_time=89.5),
        history=make_history(track_condition="Wet", lap_times=(89.0, 89.2, 89.4)),
    )
    strategy["final_action"] = "Maintain"

    result = verify_strategy(strategy)

    assert result["status"] == "Rejected"
    assert any("Maintain may only" in item for item in result["violations"])


def test_tampered_confidence_is_rejected():
    strategy = run_strategy_orchestrator(make_telemetry(), history=make_history())
    strategy["confidence"] = 0.99

    result = verify_strategy(strategy)

    assert result["status"] == "Rejected"
    assert any("Published confidence" in item for item in result["violations"])


def test_invalid_orchestrated_strategy_schema_is_rejected_before_verification():
    strategy = run_strategy_orchestrator(make_telemetry(), history=make_history())
    strategy["unexpected_field"] = "not allowed"

    with pytest.raises(ValidationError):
        verify_strategy(strategy)
