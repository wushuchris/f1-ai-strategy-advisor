from src.schemas import RulesStrategy, StrategyPriority, TelemetrySnapshot


def generate_strategy(data: dict) -> dict:
    """Generate a deterministic race-strategy recommendation from validated telemetry."""

    telemetry = TelemetrySnapshot.model_validate(data)

    actions = []
    priority = StrategyPriority.NORMAL

    if telemetry.tire_temp >= 105:
        actions.append("High tire temperatures detected. Advise tire management.")
        priority = StrategyPriority.HIGH

    if telemetry.fuel_level <= 20:
        actions.append("Fuel is low. Evaluate pit window and fuel-saving modes.")
        priority = StrategyPriority.HIGH

    if telemetry.track_condition.value == "Wet":
        actions.append("Wet conditions detected. Review compound choice and reduce push laps.")
        priority = StrategyPriority.HIGH

    if telemetry.lap >= 20 and telemetry.tire_temp >= 100:
        actions.append("Long stint degradation risk is rising. Consider a stop soon.")
        priority = StrategyPriority.HIGH

    if not actions:
        actions.append("Conditions are stable. Maintain pace and monitor trends.")

    strategy = RulesStrategy(
        priority=priority,
        recommendation=" ".join(actions),
    )

    return strategy.model_dump(mode="json")
