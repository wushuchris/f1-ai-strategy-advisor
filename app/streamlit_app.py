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
        actions.append("High tire temperatures detected. Advise tire management and reduced corner aggression.")
        priority = "High"

    if data["fuel_level"] <= 20:
        actions.append("Fuel level is low. Consider fuel-saving modes and evaluate pit window.")
        priority = "High"

    if data["lap"] >= 45 and data["tire_temp"] >= 100:
        actions.append("Late-race tire wear risk is increasing. Strongly consider a pit stop soon.")
        priority = "High"

    if data["track_condition"] == "Wet":
        actions.append("Wet conditions detected. Review tire compound choice and reduce push laps.")
        priority = "High"

    if not actions:
        actions.append("Telemetry looks stable. Maintain current pace and monitor tire and fuel trends.")

    if data["lap_time"] < 83:
        actions.append("Current lap pace is strong. Continue pushing if tire and fuel conditions remain acceptable.")

    return {
        "priority": priority,
        "recommendation": " ".join(actions)
    }


data = generate_telemetry()
strategy = generate_strategy(data)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Lap", data["lap"])
col2.metric("Lap Time (s)", data["lap_time"])
col3.metric("Tire Temp (°C)", data["tire_temp"])
col4.metric("Fuel Level (%)", data["fuel_level"])

st.subheader("Track Condition")
st.write(data["track_condition"])

st.subheader("Telemetry Snapshot")
df = pd.DataFrame([data])
st.dataframe(df, use_container_width=True)

st.subheader("Strategy Recommendation")

if strategy["priority"] == "High":
    st.warning(f"Priority: {strategy['priority']}")
else:
    st.info(f"Priority: {strategy['priority']}")

st.write(strategy["recommendation"])

st.success("Live telemetry stream active")
