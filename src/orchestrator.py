from src.agents.pace_agent import analyze_pace
from src.agents.tire_agent import analyze_tires
from src.agents.track_agent import analyze_track
from src.rules import generate_strategy
from src.schemas import (
    OrchestratedStrategy,
    PaceAction,
    PaceAssessment,
    PaceStatus,
    RulesStrategy,
    StrategyAction,
    StrategyPriority,
    TelemetrySnapshot,
    TireAction,
    TireAssessment,
    TireRisk,
    TrackAction,
    TrackAssessment,
    TrackRisk,
)


def _run_tire_analysis(telemetry_data: dict) -> TireAssessment:
    try:
        return TireAssessment.model_validate(analyze_tires(telemetry_data))
    except Exception:
        return TireAssessment(
            risk=TireRisk.HIGH,
            action=TireAction.MANAGE,
            confidence=0.0,
            rationale=(
                "Tire specialist analysis failed. A conservative deterministic fallback is active, "
                "so the car should be managed and the tire state reassessed before escalation."
            ),
        )


def _run_pace_analysis(telemetry_data: dict, history: list[dict] | None) -> PaceAssessment:
    try:
        return PaceAssessment.model_validate(analyze_pace(telemetry_data, history=history))
    except Exception:
        return PaceAssessment(
            status=PaceStatus.CRITICAL,
            action=PaceAction.MANAGE,
            reference_lap_time=telemetry_data["lap_time"],
            delta_to_reference=0.0,
            history_laps=0,
            confidence=0.0,
            rationale=(
                "Pace specialist analysis failed. A conservative deterministic fallback is active, "
                "so the car should be managed while pace evidence is rebuilt."
            ),
        )


def _run_track_analysis(telemetry_data: dict) -> TrackAssessment:
    try:
        return TrackAssessment.model_validate(analyze_track(telemetry_data))
    except Exception:
        return TrackAssessment(
            condition=telemetry_data["track_condition"],
            risk=TrackRisk.ELEVATED,
            action=TrackAction.ADAPT_TO_WET,
            confidence=0.0,
            rationale=(
                "Track-condition specialist analysis failed. A conservative deterministic fallback "
                "is active, so the strategy should be managed until the surface state is reassessed."
            ),
        )


def run_strategy_orchestrator(data: dict, history: list[dict] | None = None) -> dict:
    """Run specialist analysis and publish one application-governed strategy state."""

    telemetry = TelemetrySnapshot.model_validate(data)
    telemetry_data = telemetry.model_dump(mode="json")

    rules = RulesStrategy.model_validate(generate_strategy(telemetry_data))
    tire = _run_tire_analysis(telemetry_data)
    pace = _run_pace_analysis(telemetry_data, history)
    track = _run_track_analysis(telemetry_data)

    if tire.action == TireAction.PREPARE_TO_PIT:
        final_action = StrategyAction.PREPARE_TO_PIT
        priority = StrategyPriority.HIGH
        summary = (
            "Tire condition is the controlling constraint. Prepare for a pit stop while "
            "maintaining a managed pace until the stop can be executed safely."
        )
    elif (
        tire.risk == TireRisk.HIGH
        or pace.status == PaceStatus.CRITICAL
        or track.risk == TrackRisk.ELEVATED
        or rules.priority == StrategyPriority.HIGH
    ):
        final_action = StrategyAction.MANAGE
        priority = StrategyPriority.HIGH
        summary = (
            "At least one high-priority strategy signal is active. Manage the car and "
            "reassess the combined tire, pace, fuel, and track state before escalating."
        )
    elif tire.risk == TireRisk.MEDIUM or pace.status == PaceStatus.DEGRADED:
        final_action = StrategyAction.REVIEW
        priority = StrategyPriority.NORMAL
        summary = (
            "Specialist analysis shows a developing concern without an immediate critical "
            "constraint. Review strategy inputs and continue close monitoring."
        )
    else:
        final_action = StrategyAction.MAINTAIN
        priority = StrategyPriority.NORMAL
        if pace.status == PaceStatus.MONITORING:
            summary = (
                "No high-priority constraint is active, but the pace analyst is still building a "
                "recent-lap baseline. Maintain the current strategy and continue collecting telemetry."
            )
        else:
            summary = (
                "Specialist assessments are stable and no high-priority rule is active. "
                "Maintain the current strategy and continue monitoring telemetry."
            )

    strategy = OrchestratedStrategy(
        telemetry=telemetry,
        rules=rules,
        tire=tire,
        pace=pace,
        track=track,
        final_action=final_action,
        priority=priority,
        confidence=min(tire.confidence, pace.confidence, track.confidence),
        summary=summary,
    )

    return strategy.model_dump(mode="json")
