import random


def initialize_race_state():
    return {
        "lap": 1,
        "lap_time": round(random.uniform(84.0, 87.0), 2),
        "tire_temp": random.randint(92, 98),
        "fuel_level": 100,
        "track_condition": random.choice(["Dry", "Wet"])
    }


def simulate_next_lap(previous: dict) -> dict:
    lap = previous["lap"] + 1

    fuel_drop = random.randint(2, 4)
    new_fuel = max(0, previous["fuel_level"] - fuel_drop)

    tire_temp_change = random.randint(-1, 3)
    new_tire_temp = min(110, max(85, previous["tire_temp"] + tire_temp_change))

    if previous["track_condition"] == "Dry":
        base_lap_time = 84.5
        lap_time_penalty = (100 - new_fuel) * 0.015 + max(0, new_tire_temp - 100) * 0.08
    else:
        base_lap_time = 88.5
        lap_time_penalty = (100 - new_fuel) * 0.02 + max(0, new_tire_temp - 100) * 0.10

    new_lap_time = round(base_lap_time + lap_time_penalty + random.uniform(-0.8, 0.8), 2)

    return {
        "lap": lap,
        "lap_time": new_lap_time,
        "tire_temp": new_tire_temp,
        "fuel_level": new_fuel,
        "track_condition": previous["track_condition"]
    }
