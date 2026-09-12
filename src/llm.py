import json

import pandas as pd
import streamlit as st
from huggingface_hub import InferenceClient

from src.schemas import LLMStrategyInterpretation, OrchestratedStrategy


@st.cache_resource
def get_hf_client():
    token = st.secrets.get("HF_TOKEN", None)
    if not token:
        return None
    return InferenceClient(token=token)


def build_llm_prompt(
    current_data: dict,
    history_df: pd.DataFrame,
    orchestrated_strategy: dict,
) -> str:
    recent = history_df.tail(5).to_dict(orient="records")
    strategy = OrchestratedStrategy.model_validate(orchestrated_strategy)

    return f"""
You are an F1 race-strategy interpretation assistant.

The application has already produced and verified the authoritative pit-wall strategy below.
Your job is to explain that validated decision clearly. Do not replace, contradict, or escalate it.
Do not invent telemetry, tire life, tire compound, weather forecasts, or pit execution details that are not provided.

Current telemetry:
- Lap: {current_data['lap']}
- Lap time: {current_data['lap_time']} seconds
- Tire temperature: {current_data['tire_temp']} C
- Fuel level: {current_data['fuel_level']}%
- Track condition: {current_data['track_condition']}

Recent telemetry history:
{recent}

Verified application strategy:
- Final action: {strategy.final_action.value}
- Priority: {strategy.priority.value}
- Confidence: {strategy.confidence}
- Summary: {strategy.summary}
- Tire assessment: {strategy.tire.model_dump(mode='json')}
- Pace assessment: {strategy.pace.model_dump(mode='json')}
- Track assessment: {strategy.track.model_dump(mode='json')}
- Rules baseline: {strategy.rules.model_dump(mode='json')}

Return JSON only with exactly these keys:
{{
  "pit_recommendation": "one concise sentence",
  "pace_guidance": "one concise sentence",
  "tire_guidance": "one concise sentence",
  "risk_summary": "one concise sentence",
  "overall_strategy": "two or three concise sentences"
}}
""".strip()


def parse_llm_strategy_response(response_text: str) -> dict:
    """Parse and validate model output before it is exposed to the application."""

    parsed = json.loads(response_text)
    interpretation = LLMStrategyInterpretation.model_validate(parsed)
    return interpretation.model_dump(mode="json")


def generate_llm_strategy(
    current_data: dict,
    history_df: pd.DataFrame,
    orchestrated_strategy: dict,
) -> dict:
    client = get_hf_client()

    if client is None:
        return {
            "ok": False,
            "error": "Hugging Face token not configured. Add HF_TOKEN in Streamlit secrets.",
            "interpretation": None,
        }

    prompt = build_llm_prompt(current_data, history_df, orchestrated_strategy)

    try:
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.1-8B-Instruct",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You explain a verified Formula 1 strategy. Return valid JSON only and "
                        "never override the application's authoritative decision."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=350,
            temperature=0.2,
        )

        interpretation = parse_llm_strategy_response(response.choices[0].message.content)
        return {"ok": True, "error": None, "interpretation": interpretation}

    except Exception as exc:
        return {
            "ok": False,
            "error": f"LLM interpretation unavailable: {exc}",
            "interpretation": None,
        }
