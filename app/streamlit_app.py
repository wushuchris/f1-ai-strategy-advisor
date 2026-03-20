import sys
import time
import hashlib
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.simulation import initialize_race_state, simulate_next_lap
from src.rules import generate_strategy
from src.llm import generate_llm_strategy

st.set_page_config(
    page_title="F1 AI Strategy Advisor",
    page_icon="🏎️",
    layout="wide"
)

st.title("🏎️ F1 AI Strategy Advisor")
st.write("🚀 Real-time IoT telemetry + AI race strategy system")
st.caption("AI recommendations are rate-limited in this public demo to manage inference usage.")

# --- Session state initialization ---
if "history" not in st.session_state:
    initial = initialize_race_state()
    st.session_state.history = [initial]

if "llm_calls_used" not in st.session_state:
    st.session_state.llm_calls_used = 0

if "last_llm_call_time" not in st.session_state:
    st.session_state.last_llm_call_time = 0.0

if "last_llm_state_hash" not in st.session_state:
    st.session_state.last_llm_state_hash = None

if "last_llm_response" not in st.session_state:
    st.session_state.last_llm_response = None

# --- Constants ---
MIN_LAPS_FOR_LLM = 5
LLM_COOLDOWN_SECONDS = 30
MAX_LLM_CALLS_PER_SESSION = 5


def build_state_hash(current_data: dict, history_df: pd.DataFrame, rules_strategy: dict) -> str:
    payload = {
        "current_data": current_data,
        "recent_history": history_df.tail(5).to_dict(orient="records"),
        "rules_strategy": rules_strategy,
    }
    return hashlib.sha256(str(payload).encode("utf-8")).hexdigest()


# --- Controls ---
col_a, col_b = st.columns([1, 1])

with col_a:
    if st.button("Simulate Next Lap"):
        next_data = simulate_next_lap(st.session_state.history[-1])
        st.session_state.history.append(next_data)

with col_b:
    if st.button("Reset Simulation"):
        initial = initialize_race_state()
        st.session_state.history = [initial]
        st.session_state.llm_calls_used = 0
        st.session_state.last_llm_call_time = 0.0
        st.session_state.last_llm_state_hash = None
        st.session_state.last_llm_response = None

if len(st.session_state.history) > 50:
    st.session_state.history = st.session_state.history[-50:]

# --- Current state ---
data = st.session_state.history[-1]
df = pd.DataFrame(st.session_state.history)
rules_strategy = generate_strategy(data)

# --- Metrics ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Lap", data["lap"])
col2.metric("Lap Time (s)", data["lap_time"])
col3.metric("Tire Temp (°C)", data["tire_temp"])
col4.metric("Fuel Level (%)", data["fuel_level"])

st.subheader("Track Condition")
st.write(data["track_condition"])

st.subheader("Telemetry History")
st.dataframe(df, use_container_width=True)

st.subheader("Lap Time Trend")
st.line_chart(df.set_index("lap")["lap_time"])

st.subheader("Fuel Level Trend")
st.line_chart(df.set_index("lap")["fuel_level"])

# --- Rules strategy ---
st.subheader("Rules-Based Strategy Recommendation")
if rules_strategy["priority"] == "High":
    st.warning(f"Priority: {rules_strategy['priority']}")
else:
    st.info(f"Priority: {rules_strategy['priority']}")
st.write(rules_strategy["recommendation"])

# --- LLM safeguards status ---
st.subheader("LLM Strategy Advisor")

calls_remaining = MAX_LLM_CALLS_PER_SESSION - st.session_state.llm_calls_used
elapsed = time.time() - st.session_state.last_llm_call_time
cooldown_remaining = max(0, int(LLM_COOLDOWN_SECONDS - elapsed))

status_col1, status_col2, status_col3 = st.columns(3)
status_col1.metric("LLM Calls Used", st.session_state.llm_calls_used)
status_col2.metric("Calls Remaining", max(0, calls_remaining))
status_col3.metric("Cooldown (s)", cooldown_remaining)

current_state_hash = build_state_hash(data, df, rules_strategy)

llm_disabled_reason = None

if data["lap"] < MIN_LAPS_FOR_LLM:
    llm_disabled_reason = f"Simulate to at least lap {MIN_LAPS_FOR_LLM} before generating an AI recommendation."
elif st.session_state.llm_calls_used >= MAX_LLM_CALLS_PER_SESSION:
    llm_disabled_reason = "Session limit reached for AI recommendations. Reset the simulation to start over."
elif cooldown_remaining > 0 and st.session_state.last_llm_state_hash != current_state_hash:
    llm_disabled_reason = f"Please wait {cooldown_remaining} seconds before generating another new AI recommendation."

if llm_disabled_reason:
    st.caption(llm_disabled_reason)

generate_clicked = st.button(
    "Generate AI Strategy Recommendation",
    disabled=llm_disabled_reason is not None
)

if generate_clicked:
    # Reuse cached output if telemetry state is unchanged
    if st.session_state.last_llm_state_hash == current_state_hash and st.session_state.last_llm_response:
        llm_text = st.session_state.last_llm_response
        st.info("Using cached AI recommendation for the current telemetry state.")
    else:
        with st.spinner("Generating AI strategy..."):
            llm_text = generate_llm_strategy(data, df, rules_strategy)

        st.session_state.last_llm_call_time = time.time()
        st.session_state.llm_calls_used += 1
        st.session_state.last_llm_state_hash = current_state_hash
        st.session_state.last_llm_response = llm_text

    st.text_area("AI Strategy Output", llm_text, height=220)

# Keep showing last response after reruns
if st.session_state.last_llm_response:
    with st.expander("Most Recent AI Strategy Output", expanded=False):
        st.text_area(
            "Last AI Recommendation",
            st.session_state.last_llm_response,
            height=220,
            key="last_ai_output_display"
        )

st.success("Telemetry system active")
