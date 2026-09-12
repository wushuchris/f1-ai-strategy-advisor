from src.schemas import (
    PaceAction,
    PaceAssessment,
    PaceStatus,
    TelemetrySnapshot,
    TrackCondition,
)


def analyze_pace(data: dict) -> dict:
    """Evaluate current lap pace using deterministic, track-aware thresholds."""

    telemetry = TelemetrySnapshot.model_validate(data)

    if telemetry.track_condition == TrackCondition.DRY:
        target_lap_time = 85.5
        degraded_threshold = 1.0
        critical_threshold = 2.0
    else:
        target_lap_time = 89.5
        degraded_threshold = 1.0
        critical_threshold = 2.0

    delta_to_target = round(telemetry.lap_time - target_lap_time, 2)

    if delta_to_target >= critical_threshold:
        status = PaceStatus.CRITICAL
        action = PaceAction.MANAGE
        confidence = 0.95
        rationale = (
            "Lap time is materially slower than the track-condition target. Preserve the car, "
            "review likely causes of pace loss, and reassess strategy before demanding more pace."
        )
    elif delta_to_target >= degraded_threshold:
        status = PaceStatus.DEGRADED
        action = PaceAction.REVIEW
        confidence = 0.90
        rationale = (
            "Lap time is slower than the expected target for the current track condition. "
            "Review tire, fuel, and race-state contributors before changing pace instructions."
        )
    else:
        status = PaceStatus.ON_TARGET
        action = PaceAction.MAINTAIN
        confidence = 0.90
        rationale = (
            "Lap time remains within the expected operating range for the current track condition."
        )

    assessment = PaceAssessment(
        status=status,
        action=action,
        target_lap_time=target_lap_time,
        delta_to_target=delta_to_target,
        confidence=confidence,
        rationale=rationale,
    )

    return assessment.model_dump(mode="json")
