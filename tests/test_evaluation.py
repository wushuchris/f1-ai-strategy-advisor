from src.evaluation import build_evaluation_scenarios, run_evaluation_suite


def test_evaluation_suite_covers_key_strategy_states_and_boundaries():
    names = {scenario.name for scenario in build_evaluation_scenarios()}

    assert names == {
        "stable_dry_state",
        "tire_management_threshold",
        "overheated_tires",
        "low_fuel",
        "wet_track",
        "pace_degradation",
        "exact_pace_degradation_threshold",
        "critical_pace_loss",
        "exact_critical_pace_threshold",
        "insufficient_pace_history",
        "late_race_lap_without_tire_age_evidence",
    }


def test_all_evaluation_scenarios_match_expected_behavior():
    report = run_evaluation_suite()

    assert report["metrics"]["total_scenarios"] == 11
    assert report["metrics"]["passed_scenarios"] == 11
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


def test_boundary_scenarios_are_published_with_expected_actions():
    results = {item["name"]: item for item in run_evaluation_suite()["results"]}

    assert results["tire_management_threshold"]["actual_action"] == "Review Strategy"
    assert results["exact_pace_degradation_threshold"]["actual_action"] == "Review Strategy"
    assert results["exact_critical_pace_threshold"]["actual_action"] == "Manage and Reassess"
    assert results["late_race_lap_without_tire_age_evidence"]["actual_action"] == "Maintain"
