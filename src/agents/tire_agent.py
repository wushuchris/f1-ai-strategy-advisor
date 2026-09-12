from src.schemas import (
    TelemetrySnapshot,
    TireAction,
    TireAssessment,
    TireRisk,
    TrackCondition,
)


def analyze_tires(data: dict) -> dict:
    """Evaluate observed tire stress without inferring unsupported tire life."""

    telemetry = TelemetrySnapshot.model_validate(data)

    if telemetry.tire_temp >= 105:
        risk = TireRisk.HIGH
        action = TireAction.PREPARE_TO_PIT
        confidence = 0.95
        rationale = (
            "Tire temperature is at or above the high-risk threshold, increasing the "
            "likelihood of rapid degradation. Prepare for a pit stop and continue monitoring."
        )
    elif telemetry.tire_temp >= 100:
        risk = TireRisk.MEDIUM
        action = TireAction.MANAGE
        confidence = 0.85
        rationale = (
            "Tire temperature is elevated. Pace management and continued monitoring are "
            "recommended, but remaining tire life cannot be estimated from the available telemetry."
        )
    else:
        risk = TireRisk.LOW
        action = TireAction.MAINTAIN
        confidence = 0.90
        rationale = (
            "Current tire temperature remains within the stable operating range. Continue monitoring; "
            "the available telemetry does not include tire age, compound, or wear measurements."
        )

    if telemetry.track_condition == TrackCondition.WET and risk == TireRisk.LOW:
        risk = TireRisk.MEDIUM
        action = TireAction.MANAGE
        confidence = 0.80
        rationale = (
            "Wet conditions increase tire-management uncertainty even though the observed tire "
            "temperature is otherwise stable. No tire-life estimate is inferred from the current data."
        )

    assessment = TireAssessment(
        risk=risk,
        action=action,
        confidence=confidence,
        rationale=rationale,
    )

    return assessment.model_dump(mode="json")
