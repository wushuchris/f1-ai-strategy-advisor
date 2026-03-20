import streamlit as st
import random
import pandas as pd

st.set_page_config(
    page_title="F1 AI Strategy Advisor",
    page_icon="🏎️",
    layout="wide"
)

st.title("🏎️ F1 AI Strategy Advisor")
st.write("🚀 Real-time IoT telemetry + AI race strategy system")


def generate_telemetry():
    return {
        "lap": random.randint(1, 70),
        "lap_time": round(random.uniform(80, 95), 2),
        "tire_temp": random.randint(90, 110),
        "fuel_level": random.randint(10, 100),
        "track_condition": random.choice(["Dry", "Wet"])
    }


def generate_strategy(data: dict) -> dict:
    actions = []
    priority = "Normal"

    if data["tire_temp"] >= 105:
        actions.append("High tire temperatures detected. Advise tire management.")
        priority = "High"

    if data["fuel_level"] <= 20:
        actions.append("Fuel low. Consider pit window.")
        priority = "High"

    if data["track_condition"] == "Wet":
        actions.append("Wet conditions. Adjust tire strategy.")
        priority = "High"

    if not actions:
        actions.append("Conditions stable. Maintain pace.")

    return {
        "priority": priority,
        "recommendation": " ".join(actions)
    }


# --- SESSION STATE (Telemetry History) ---
if "history" not in st.session_state:
    st.session_state.history = []

# --- Generate New Data ---
data = generate_telemetry()
st.session_state.history.append(data)

# Limit history size
if len(st.session_state.history) > 50:
    st.session_state.history.pop(0)

strategy = generate_strategy(data)

# --- METRICS ---
col1, col2, col3, col4 = st.columns(4)

col1.metric("Lap", data["lap"])
col2.metric("Lap Time (s)", data["lap_time"])
col3.metric("Tire Temp (°C)", data["tire_temp"])
col4.metric("Fuel Level (%)", data["fuel_level"])

st.subheader("Track Condition")
st.write(data["track_condition"])

# --- HISTORY DATAFRAME ---
df = pd.DataFrame(st.session_state.history)

st.subheader("Telemetry History")
st.dataframe(df, use_container_width=True)

# --- CHART ---
st.subheader("Lap Time Trend")
st.line_chart(df["lap_time"])

# --- STRATEGY ---
st.subheader("Strategy Recommendation")

if strategy["priority"] == "High":
    st.warning(f"Priority: {strategy['priority']}")
else:
    st.info(f"Priority: {strategy['priority']}")

st.write(strategy["recommendation"])

st.success("Live telemetry stream active")
