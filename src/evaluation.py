from dataclasses import dataclass

from src.orchestrator import run_strategy_orchestrator
from src.verifier import verify_strategy


@dataclass(frozen=True)
class EvaluationScenario:
    name: str
    history: list[dict]
    current: dict
    expected_action: str
    expected_priority: str


def _telemetry(
    lap: int,
    lap_time: float,
    tire_temp: float = 96.0,
    fuel_level: float = 80.0,
    track_condition: str = "Dry",
) -> dict:
    return {
        "lap": lap,
        "lap_time": lap_time,
        "tire_temp": tire_temp,
        "fuel_level": fuel_level,
        "track_condition": track_condition,
    }


def build_evaluation_scenarios() -> list[EvaluationScenario]:
    """Return deterministic race-state scenarios used for regression evaluation."""

    dry_history = [
        _telemetry(1, 85.0),
        _telemetry(2, 85.1),
        _telemetry(3, 84.9),
    ]
    wet_history = [
        _telemetry(1, 89.2, track_condition="Wet"),
        _telemetry(2, 89.4, track_condition="Wet"),
        _telemetry(3, 89.3, track_condition="Wet"),
    ]

    return [
        EvaluationScenario(
            name="stable_dry_state",
            history=dry_history,
            current=_telemetry(4, 85.2),
            expected_action="Maintain",
            expected_priority="Normal",
        ),
        EvaluationScenario(
            name="overheated_tires",
            history=dry_history,
            current=_telemetry(4, 85.2, tire_temp=105.0),
            expected_action="Prepare to Pit",
            expected_priority="High",
        ),
        EvaluationScenario(
            name="low_fuel",
            history=dry_history,
            current=_telemetry(4, 85.2, fuel_level=15.0),
            expected_action="Manage and Reassess",
            expected_priority="High",
        ),
        EvaluationScenario(
            name="wet_track",
            history=wet_history,
            current=_telemetry(4, 89.4, track_condition="Wet"),
            expected_action="Manage and Reassess",
            expected_priority="High",
        ),
        EvaluationScenario(
            name="pace_degradation",
            history=dry_history,
            current=_telemetry(4, 86.0),
            expected_action="Review Strategy",
            expected_priority="Normal",
        ),
        EvaluationScenario(
            name="critical_pace_loss",
            history=dry_history,
            current=_telemetry(4, 86.6),
            expected_action="Manage and Reassess",
            expected_priority="High",
        ),
        EvaluationScenario(
            name="insufficient_pace_history",
            history=[_telemetry(1, 85.0)],
            current=_telemetry(2, 85.1),
            expected_action="Maintain",
            expected_priority="Normal",
        ),
    ]


def run_evaluation_suite() -> dict:
    """Evaluate deterministic strategy behavior without making any LLM calls."""

    results = []

    for scenario in build_evaluation_scenarios():
        strategy = run_strategy_orchestrator(
            scenario.current,
            history=scenario.history,
        )
        verification = verify_strategy(strategy)

        action_match = strategy["final_action"] == scenario.expected_action
        priority_match = strategy["priority"] == scenario.expected_priority
        publishable = verification["publishable"] is True
        passed = action_match and priority_match and publishable

        results.append(
            {
                "name": scenario.name,
                "expected_action": scenario.expected_action,
                "actual_action": strategy["final_action"],
                "expected_priority": scenario.expected_priority,
                "actual_priority": strategy["priority"],
                "publishable": publishable,
                "action_match": action_match,
                "priority_match": priority_match,
                "passed": passed,
            }
        )

    total = len(results)
    passed_count = sum(item["passed"] for item in results)
    publishable_count = sum(item["publishable"] for item in results)
    action_match_count = sum(item["action_match"] for item in results)
    priority_match_count = sum(item["priority_match"] for item in results)

    return {
        "results": results,
        "metrics": {
            "total_scenarios": total,
            "passed_scenarios": passed_count,
            "scenario_pass_rate": passed_count / total,
            "publishable_rate": publishable_count / total,
            "expected_action_match_rate": action_match_count / total,
            "expected_priority_match_rate": priority_match_count / total,
        },
    }
