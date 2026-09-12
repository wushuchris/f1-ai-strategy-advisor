from src.rules import generate_strategy


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


def test_stable_state_returns_normal_priority():
    result = generate_strategy(make_telemetry())

    assert result["priority"] == "Normal"
    assert "Conditions are stable" in result["recommendation"]


def test_race_lap_does_not_imply_tire_stint_age():
    result = generate_strategy(make_telemetry(lap=25, tire_temp=100.0))

    assert result["priority"] == "Normal"
    assert "stint" not in result["recommendation"].lower()
    assert "degradation" not in result["recommendation"].lower()


def test_high_tire_temperature_is_high_priority():
    result = generate_strategy(make_telemetry(tire_temp=105.0))

    assert result["priority"] == "High"
    assert "High tire temperatures" in result["recommendation"]


def test_low_fuel_uses_fuel_saving_guidance_without_implying_refueling():
    result = generate_strategy(make_telemetry(fuel_level=15.0))

    assert result["priority"] == "High"
    assert "fuel-saving" in result["recommendation"]
    assert "pit window" not in result["recommendation"].lower()


def test_wet_track_is_high_priority():
    result = generate_strategy(make_telemetry(track_condition="Wet"))

    assert result["priority"] == "High"
    assert "Wet conditions" in result["recommendation"]
