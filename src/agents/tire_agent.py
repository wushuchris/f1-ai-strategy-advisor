from src.schemas import (
    TelemetrySnapshot,
    TireAction,
    TireAssessment,
    TireRisk,
    TrackCondition,
)


def analyze_tires(data: dict) -> dict:
    """Evaluate tire stress using deterministic application-owned policy."""

    telemetry = TelemetrySnapshot.model_validate(data)

    if telemetry.tire_temp >= 105:
        risk = TireRisk.HIGH
        action = TireAction.PREPARE_TO_PIT
        estimated_remaining_laps = 2
        confidence = 0.95
        rationale = (
            "Tire temperature is at or above the high-risk threshold, increasing the "
            "likelihood of rapid degradation."
        )
    elif telemetry.tire_temp >= 100 or telemetry.lap >= 20:
        risk = TireRisk.MEDIUM
        action = TireAction.MANAGE
        estimated_remaining_laps = 5
        confidence = 0.85
        rationale = (
            "Tire stress is elevated due to temperature or stint length. Pace management "
            "and continued monitoring are recommended."
        )
    else:
        risk = TireRisk.LOW
        action = TireAction.MAINTAIN
        estimated_remaining_laps = 8
        confidence = 0.90
        rationale = "Current tire temperature and stint length remain within the stable operating range."

    if telemetry.track_condition == TrackCondition.WET and risk == TireRisk.LOW:
        risk = TireRisk.MEDIUM
        action = TireAction.MANAGE
        estimated_remaining_laps = min(estimated_remaining_laps, 5)
        confidence = 0.80
        rationale = (
            "Wet conditions increase tire-management uncertainty even though temperature "
            "and stint length are otherwise stable."
        )

    assessment = TireAssessment(
        risk=risk,
        action=action,
        estimated_remaining_laps=estimated_remaining_laps,
        confidence=confidence,
        rationale=rationale,
    )

    return assessment.model_dump(mode="json")
