from src.evaluation import build_evaluation_scenarios, run_evaluation_suite


def test_evaluation_suite_covers_key_strategy_states():
    names = {scenario.name for scenario in build_evaluation_scenarios()}

    assert names == {
        "stable_dry_state",
        "overheated_tires",
        "low_fuel",
        "wet_track",
        "pace_degradation",
        "critical_pace_loss",
        "insufficient_pace_history",
    }


def test_all_evaluation_scenarios_match_expected_behavior():
    report = run_evaluation_suite()

    assert report["metrics"]["total_scenarios"] == 7
    assert report["metrics"]["passed_scenarios"] == 7
    assert report["metrics"]["scenario_pass_rate"] == 1.0
    assert report["metrics"]["publishable_rate"] == 1.0
    assert report["metrics"]["expected_action_match_rate"] == 1.0
    assert report["metrics"]["expected_priority_match_rate"] == 1.0


def test_evaluation_report_exposes_expected_and_actual_outputs():
    report = run_evaluation_suite()
    first = report["results"][0]

    assert first["name"] == "stable_dry_state"
    assert first["expected_action"] == "Maintain"
    assert first["actual_action"] == "Maintain"
    assert first["expected_priority"] == "Normal"
    assert first["actual_priority"] == "Normal"
    assert first["publishable"] is True
    assert first["passed"] is True
