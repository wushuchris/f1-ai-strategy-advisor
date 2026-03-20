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


def initialize_race_state():
    return {
        "lap": 1,
        "lap_time": round(random.uniform(84.0, 87.0), 2),
        "tire_temp": random.randint(92, 98),
        "fuel_level": 100,
        "track_condition": random.choice(["Dry", "Wet"])
    }


def simulate_next_lap(previous: dict) -> dict:
    lap = previous["lap"] + 1

    fuel_drop = random.randint(2, 4)
    new_fuel = max(0, previous["fuel_level"] - fuel_drop)

    tire_temp_change = random.randint(-1, 3)
    new_tire_temp = min(110, max(85, previous["tire_temp"] + tire_temp_change))

    if previous["track_condition"] == "Dry":
        base_lap_time = 84.5
        lap_time_penalty = (100 - new_fuel) * 0.015 + max(0, new_tire_temp - 100) * 0.08
    else:
        base_lap_time = 88.5
        lap_time_penalty = (100 - new_fuel) * 0.02 + max(0, new_tire_temp - 100) * 0.10

    new_lap_time = round(base_lap_time + lap_time_penalty + random.uniform(-0.8, 0.8), 2)

    return {
        "lap": lap,
        "lap_time": new_lap_time,
        "tire_temp": new_tire_temp,
        "fuel_level": new_fuel,
        "track_condition": previous["track_condition"]
    }


def generate_strategy(data: dict) -> dict:
    actions = []
    priority = "Normal"

    if data["tire_temp"] >= 105:
        actions.append("High tire temperatures detected. Advise tire management.")
        priority = "High"

    if data["fuel_level"] <= 20:
        actions.append("Fuel is low. Evaluate pit window and fuel-saving modes.")
        priority = "High"

    if data["track_condition"] == "Wet":
        actions.append("Wet conditions detected. Review compound choice and reduce push laps.")
        priority = "High"

    if data["lap"] >= 20 and data["tire_temp"] >= 100:
        actions.append("Long stint degradation risk is rising. Consider a stop soon.")
        priority = "High"

    if not actions:
        actions.append("Conditions are stable. Maintain pace and monitor trends.")

    return {
        "priority": priority,
        "recommendation": " ".join(actions)
    }


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
strategy = generate_strategy(data)
df = pd.DataFrame(st.session_state.history)

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

st.subheader("Strategy Recommendation")
if strategy["priority"] == "High":
    st.warning(f"Priority: {strategy['priority']}")
else:
    st.info(f"Priority: {strategy['priority']}")

st.write(strategy["recommendation"])

st.success("Telemetry system active")
