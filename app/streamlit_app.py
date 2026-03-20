import streamlit as st
import random
import time
import pandas as pd

st.set_page_config(
    page_title="F1 AI Strategy Advisor",
    page_icon="🏎️",
    layout="wide"
)

st.title("🏎️ F1 AI Strategy Advisor")
st.write("🚀 Real-time IoT telemetry + AI race strategy system")

# --- Simulated Telemetry Function ---
def generate_telemetry():
    return {
        "lap": random.randint(1, 70),
        "lap_time": round(random.uniform(80, 95), 2),
        "tire_temp": random.randint(90, 110),
        "fuel_level": random.randint(10, 100),
        "track_condition": random.choice(["Dry", "Wet"])
    }

# --- Generate Data ---
data = generate_telemetry()

# --- Layout ---
col1, col2, col3, col4 = st.columns(4)

col1.metric("Lap", data["lap"])
col2.metric("Lap Time (s)", data["lap_time"])
col3.metric("Tire Temp (°C)", data["tire_temp"])
col4.metric("Fuel Level (%)", data["fuel_level"])

st.subheader("Track Condition")
st.write(data["track_condition"])

# --- Data Table ---
st.subheader("Telemetry Snapshot")
df = pd.DataFrame([data])
st.dataframe(df)

st.success("Live telemetry stream active")
