import sys
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

if "history" not in st.session_state:
    initial = initialize_race_state()
    st.session_state.history = [initial]

col_a, col_b = st.columns([1, 1])

with col_a:
    if st.button("Simulate Next Lap"):
        next_data = simulate_next_lap(st.session_state.history[-1])
        st.session_state.history.append(next_data)

with col_b:
    if st.button("Reset Simulation"):
        initial = initialize_race_state()
        st.session_state.history = [initial]

if len(st.session_state.history) > 50:
    st.session_state.history = st.session_state.history[-50:]

data = st.session_state.history[-1]
df = pd.DataFrame(st.session_state.history)
rules_strategy = generate_strategy(data)

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

st.subheader("Rules-Based Strategy Recommendation")
if rules_strategy["priority"] == "High":
    st.warning(f"Priority: {rules_strategy['priority']}")
else:
    st.info(f"Priority: {rules_strategy['priority']}")
st.write(rules_strategy["recommendation"])

st.subheader("LLM Strategy Advisor")
if st.button("Generate AI Strategy Recommendation"):
    with st.spinner("Generating AI strategy..."):
        llm_text = generate_llm_strategy(data, df, rules_strategy)
    st.text_area("AI Strategy Output", llm_text, height=220)

st.success("Telemetry system active")
