import streamlit as st
import pandas as pd
from huggingface_hub import InferenceClient


@st.cache_resource
def get_hf_client():
    token = st.secrets.get("HF_TOKEN", None)
    if not token:
        return None
    return InferenceClient(token=token)


def build_llm_prompt(current_data: dict, history_df: pd.DataFrame, rules_strategy: dict) -> str:
    recent = history_df.tail(5).to_dict(orient="records")

    return f"""
You are an F1 race strategist.

Analyze the telemetry and provide a concise strategy recommendation.

Current telemetry:
- Lap: {current_data['lap']}
- Lap time: {current_data['lap_time']} seconds
- Tire temperature: {current_data['tire_temp']} C
- Fuel level: {current_data['fuel_level']}%
- Track condition: {current_data['track_condition']}

Recent telemetry history:
{recent}

Rules-based strategy baseline:
- Priority: {rules_strategy['priority']}
- Recommendation: {rules_strategy['recommendation']}

Return your answer in exactly this format:

Pit Recommendation: <one sentence>
Pace Guidance: <one sentence>
Tire Guidance: <one sentence>
Risk Summary: <one sentence>
Overall Strategy: <2-3 sentences>
""".strip()


def generate_llm_strategy(current_data: dict, history_df: pd.DataFrame, rules_strategy: dict) -> str:
    client = get_hf_client()

    if client is None:
        return "Hugging Face token not configured. Add HF_TOKEN in Streamlit secrets."

    prompt = build_llm_prompt(current_data, history_df, rules_strategy)

    try:
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.1-8B-Instruct",
            messages=[
                {"role": "system", "content": "You are a precise Formula 1 race strategist."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=300,
            temperature=0.3,
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"LLM strategy unavailable: {e}"
