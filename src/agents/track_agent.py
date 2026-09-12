from src.schemas import (
    TelemetrySnapshot,
    TrackAction,
    TrackAssessment,
    TrackCondition,
    TrackRisk,
)


def analyze_track(data: dict) -> dict:
    """Evaluate observed track conditions without inferring unsupported weather forecasts."""

    telemetry = TelemetrySnapshot.model_validate(data)

    if telemetry.track_condition == TrackCondition.WET:
        risk = TrackRisk.ELEVATED
        action = TrackAction.ADAPT_TO_WET
        confidence = 0.95
        rationale = (
            "Wet track conditions increase operational uncertainty and reduce the margin for "
            "aggressive pace. Adapt the strategy to the observed surface condition and continue "
            "monitoring telemetry; no weather forecast is inferred from the current snapshot."
        )
    else:
        risk = TrackRisk.LOW
        action = TrackAction.MAINTAIN
        confidence = 0.95
        rationale = (
            "The observed track surface is dry, so no track-condition adaptation is required "
            "from this specialist. Continue monitoring for a change in the reported surface state."
        )

    assessment = TrackAssessment(
        condition=telemetry.track_condition,
        risk=risk,
        action=action,
        confidence=confidence,
        rationale=rationale,
    )

    return assessment.model_dump(mode="json")
