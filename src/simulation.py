import random

from src.schemas import TelemetrySnapshot


def initialize_race_state() -> dict:
    """Create the first validated telemetry snapshot for a race session."""

    snapshot = TelemetrySnapshot(
        lap=1,
        lap_time=round(random.uniform(84.0, 87.0), 2),
        tire_temp=random.randint(92, 98),
        fuel_level=100,
        track_condition=random.choice(["Dry", "Wet"]),
    )

    return snapshot.model_dump(mode="json")


def calculate_expected_lap_time(
    fuel_level: float,
    tire_temp: float,
    track_condition: str,
) -> float:
    """Return the deterministic mean lap time before random lap-to-lap variation."""

    if track_condition == "Dry":
        base_lap_time = 84.5
        fuel_load_penalty = fuel_level * 0.015
        tire_temp_penalty = max(0, tire_temp - 100) * 0.08
    else:
        base_lap_time = 88.5
        fuel_load_penalty = fuel_level * 0.02
        tire_temp_penalty = max(0, tire_temp - 100) * 0.10

    return round(base_lap_time + fuel_load_penalty + tire_temp_penalty, 2)


def simulate_next_lap(previous: dict) -> dict:
    """Advance the simulation by one lap and validate the resulting telemetry."""

    previous_snapshot = TelemetrySnapshot.model_validate(previous)

    lap = previous_snapshot.lap + 1

    fuel_drop = random.randint(2, 4)
    new_fuel = max(0, previous_snapshot.fuel_level - fuel_drop)

    tire_temp_change = random.randint(-1, 3)
    new_tire_temp = min(110, max(85, previous_snapshot.tire_temp + tire_temp_change))

    expected_lap_time = calculate_expected_lap_time(
        fuel_level=new_fuel,
        tire_temp=new_tire_temp,
        track_condition=previous_snapshot.track_condition.value,
    )

    new_lap_time = round(
        expected_lap_time + random.uniform(-0.8, 0.8),
        2,
    )

    snapshot = TelemetrySnapshot(
        lap=lap,
        lap_time=new_lap_time,
        tire_temp=new_tire_temp,
        fuel_level=new_fuel,
        track_condition=previous_snapshot.track_condition,
    )

    return snapshot.model_dump(mode="json")
