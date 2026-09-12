from src.simulation import calculate_expected_lap_time


def test_lower_fuel_load_reduces_expected_dry_lap_time():
    heavy = calculate_expected_lap_time(
        fuel_level=100,
        tire_temp=96,
        track_condition="Dry",
    )
    light = calculate_expected_lap_time(
        fuel_level=20,
        tire_temp=96,
        track_condition="Dry",
    )

    assert light < heavy


def test_overheated_tires_increase_expected_lap_time():
    stable = calculate_expected_lap_time(
        fuel_level=50,
        tire_temp=98,
        track_condition="Dry",
    )
    overheated = calculate_expected_lap_time(
        fuel_level=50,
        tire_temp=106,
        track_condition="Dry",
    )

    assert overheated > stable


def test_wet_conditions_are_slower_than_dry_for_same_state():
    dry = calculate_expected_lap_time(
        fuel_level=50,
        tire_temp=96,
        track_condition="Dry",
    )
    wet = calculate_expected_lap_time(
        fuel_level=50,
        tire_temp=96,
        track_condition="Wet",
    )

    assert wet > dry
