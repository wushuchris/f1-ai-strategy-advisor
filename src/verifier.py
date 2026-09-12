from src.schemas import (
    OrchestratedStrategy,
    PaceStatus,
    StrategyAction,
    StrategyPriority,
    StrategyVerification,
    TireAction,
    TireRisk,
    TrackRisk,
    VerificationStatus,
)


def verify_strategy(strategy_data: dict) -> dict:
    """Verify that an orchestrated strategy is internally consistent before publication."""

    strategy = OrchestratedStrategy.model_validate(strategy_data)
    violations: list[str] = []
    checks_run = 0

    checks_run += 1
    if strategy.final_action == StrategyAction.PREPARE_TO_PIT and strategy.tire.action != TireAction.PREPARE_TO_PIT:
        violations.append(
            "Prepare to Pit may only be published when the tire analyst explicitly emits Prepare to Pit."
        )

    checks_run += 1
    if strategy.tire.action == TireAction.PREPARE_TO_PIT and strategy.final_action != StrategyAction.PREPARE_TO_PIT:
        violations.append(
            "A tire Prepare to Pit signal must be preserved by the orchestrator publication action."
        )

    checks_run += 1
    high_priority_signal = (
        strategy.tire.risk == TireRisk.HIGH
        or strategy.pace.status == PaceStatus.CRITICAL
        or strategy.track.risk == TrackRisk.ELEVATED
        or strategy.rules.priority == StrategyPriority.HIGH
    )
    if high_priority_signal and strategy.priority != StrategyPriority.HIGH:
        violations.append("High-priority specialist or rule signals require High publication priority.")

    checks_run += 1
    if not high_priority_signal and strategy.priority == StrategyPriority.HIGH:
        violations.append("High publication priority requires at least one high-priority supporting signal.")

    checks_run += 1
    if strategy.final_action == StrategyAction.MAINTAIN and (
        strategy.tire.risk != TireRisk.LOW
        or strategy.pace.status != PaceStatus.ON_TARGET
        or strategy.track.risk != TrackRisk.LOW
        or strategy.rules.priority != StrategyPriority.NORMAL
    ):
        violations.append("Maintain may only be published when all bounded inputs are stable.")

    checks_run += 1
    expected_confidence = min(
        strategy.tire.confidence,
        strategy.pace.confidence,
        strategy.track.confidence,
    )
    if abs(strategy.confidence - expected_confidence) > 1e-9:
        violations.append(
            "Published confidence must equal the lowest confidence across all specialist assessments."
        )

    if violations:
        verification = StrategyVerification(
            status=VerificationStatus.REJECTED,
            publishable=False,
            checks_run=checks_run,
            violations=violations,
            rationale=(
                "The orchestrated strategy failed one or more deterministic publication checks "
                "and must not be presented as the authoritative pit-wall decision."
            ),
        )
    else:
        verification = StrategyVerification(
            status=VerificationStatus.APPROVED,
            publishable=True,
            checks_run=checks_run,
            violations=[],
            rationale=(
                "The orchestrated strategy is consistent with its validated specialist evidence "
                "and application-owned publication policy."
            ),
        )

    return verification.model_dump(mode="json")
