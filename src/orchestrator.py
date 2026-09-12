from src.agents.pace_agent import analyze_pace
from src.agents.tire_agent import analyze_tires
from src.agents.track_agent import analyze_track
from src.rules import generate_strategy
from src.schemas import (
    OrchestratedStrategy,
    PaceAssessment,
    PaceStatus,
    RulesStrategy,
    StrategyAction,
    StrategyPriority,
    TelemetrySnapshot,
    TireAction,
    TireAssessment,
    TireRisk,
    TrackAssessment,
    TrackRisk,
)


def run_strategy_orchestrator(data: dict) -> dict:
    """Run specialist analysis and publish one application-governed strategy state."""

    telemetry = TelemetrySnapshot.model_validate(data)
    telemetry_data = telemetry.model_dump(mode="json")

    rules = RulesStrategy.model_validate(generate_strategy(telemetry_data))
    tire = TireAssessment.model_validate(analyze_tires(telemetry_data))
    pace = PaceAssessment.model_validate(analyze_pace(telemetry_data))
    track = TrackAssessment.model_validate(analyze_track(telemetry_data))

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
