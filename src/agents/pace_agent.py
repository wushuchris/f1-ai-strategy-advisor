from statistics import median

from src.schemas import (
    PaceAction,
    PaceAssessment,
    PaceStatus,
    TelemetrySnapshot,
)


MIN_REFERENCE_LAPS = 3
DEGRADED_DELTA_SECONDS = 0.75
CRITICAL_DELTA_SECONDS = 1.50


def analyze_pace(data: dict, history: list[dict] | None = None) -> dict:
    """Evaluate pace against recent comparable telemetry rather than a fixed lap-time target."""

    telemetry = TelemetrySnapshot.model_validate(data)
    validated_history = [
        TelemetrySnapshot.model_validate(item)
        for item in (history or [])
    ]

    comparable_history = [
        item
        for item in validated_history
        if item.lap < telemetry.lap and item.track_condition == telemetry.track_condition
    ][-MIN_REFERENCE_LAPS:]

    if len(comparable_history) < MIN_REFERENCE_LAPS:
        assessment = PaceAssessment(
            status=PaceStatus.MONITORING,
            action=PaceAction.MONITOR,
            reference_lap_time=telemetry.lap_time,
            delta_to_reference=0.0,
            history_laps=len(comparable_history),
            confidence=0.60,
            rationale=(
                "Not enough comparable prior laps are available to establish a reliable pace baseline. "
                "Continue collecting telemetry before classifying pace loss."
            ),
        )
        return assessment.model_dump(mode="json")

    reference_lap_time = round(median(item.lap_time for item in comparable_history), 2)
    delta_to_reference = round(telemetry.lap_time - reference_lap_time, 2)

    if delta_to_reference >= CRITICAL_DELTA_SECONDS:
        status = PaceStatus.CRITICAL
        action = PaceAction.MANAGE
        confidence = 0.95
        rationale = (
            "Current lap time is materially slower than the median of the three most recent comparable laps. "
            "Manage the car and reassess likely causes before demanding more pace."
        )
    elif delta_to_reference >= DEGRADED_DELTA_SECONDS:
        status = PaceStatus.DEGRADED
        action = PaceAction.REVIEW
        confidence = 0.90
        rationale = (
            "Current lap time is slower than the recent comparable-lap baseline. Review tire, fuel, "
            "and race-state contributors before changing pace instructions."
        )
    else:
        status = PaceStatus.ON_TARGET
        action = PaceAction.MAINTAIN
        confidence = 0.90
        rationale = (
            "Current lap time remains within the expected range of the recent comparable-lap baseline."
        )

    assessment = PaceAssessment(
        status=status,
        action=action,
        reference_lap_time=reference_lap_time,
        delta_to_reference=delta_to_reference,
        history_laps=len(comparable_history),
        confidence=confidence,
        rationale=rationale,
    )

    return assessment.model_dump(mode="json")
