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
