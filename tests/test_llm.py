import json

import pandas as pd
import pytest
from pydantic import ValidationError

from src.llm import build_llm_prompt, parse_llm_strategy_response
from src.orchestrator import run_strategy_orchestrator


def make_telemetry(**overrides):
    telemetry = {
        "lap": 5,
        "lap_time": 85.0,
        "tire_temp": 96.0,
        "fuel_level": 80.0,
        "track_condition": "Dry",
    }
    telemetry.update(overrides)
    return telemetry


def test_valid_json_response_is_structured_and_validated():
    payload = {
        "pit_recommendation": "Stay out and continue monitoring the verified strategy state.",
        "pace_guidance": "Maintain the current pace while monitoring recent-lap behavior.",
        "tire_guidance": "Continue tire management based only on the observed temperature signal.",
        "risk_summary": "No unsupported escalation is warranted from the validated evidence.",
        "overall_strategy": "Follow the verified pit-wall action. Reassess when new telemetry arrives.",
    }

    result = parse_llm_strategy_response(json.dumps(payload))

    assert result == payload


def test_extra_llm_fields_are_rejected():
    payload = {
        "pit_recommendation": "Stay out.",
        "pace_guidance": "Maintain pace.",
        "tire_guidance": "Monitor temperature.",
        "risk_summary": "Risk is bounded.",
        "overall_strategy": "Follow the verified strategy.",
        "override_action": "Pit now",
    }

    with pytest.raises(ValidationError):
        parse_llm_strategy_response(json.dumps(payload))


def test_missing_required_llm_fields_are_rejected():
    payload = {
        "pit_recommendation": "Stay out.",
        "pace_guidance": "Maintain pace.",
    }

    with pytest.raises(ValidationError):
        parse_llm_strategy_response(json.dumps(payload))


def test_non_json_llm_output_is_rejected():
    with pytest.raises(json.JSONDecodeError):
        parse_llm_strategy_response("Pit Recommendation: stay out")


def test_prompt_frames_llm_as_interpreter_not_authority():
    telemetry = make_telemetry()
    history = pd.DataFrame([telemetry])
    strategy = run_strategy_orchestrator(telemetry, history.to_dict(orient="records"))

    prompt = build_llm_prompt(telemetry, history, strategy)

    assert "authoritative pit-wall strategy" in prompt
    assert "Do not replace, contradict, or escalate it" in prompt
    assert f"Final action: {strategy['final_action']}" in prompt
