import sys
import time
import hashlib
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.simulation import initialize_race_state, simulate_next_lap
from src.llm import generate_llm_strategy
from src.orchestrator import run_strategy_orchestrator
from src.policy import get_llm_disabled_reason
from src.verifier import verify_strategy
from src.evaluation import run_evaluation_suite

st.set_page_config(
    page_title="F1 AI Strategy Advisor",
    page_icon="🏎️",
    layout="wide"
)

st.title("🏎️ F1 AI Strategy Advisor")
st.write("🚀 Real-time IoT telemetry + AI race strategy system")
st.caption("AI interpretations are rate-limited in this public demo to manage inference usage.")

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


def build_state_hash(
    current_data: dict,
    history_df: pd.DataFrame,
    orchestrated_strategy: dict,
    verification: dict,
) -> str:
    payload = {
        "current_data": current_data,
        "recent_history": history_df.tail(5).to_dict(orient="records"),
        "orchestrated_strategy": orchestrated_strategy,
        "verification": verification,
    }
    return hashlib.sha256(str(payload).encode("utf-8")).hexdigest()


def render_llm_interpretation(result: dict) -> None:
    """Render only validated structured LLM output; deterministic strategy remains authoritative."""

    if not result["ok"]:
        st.warning(result["error"])
        st.caption(
            "The AI interpretation is unavailable, but the verified deterministic pit-wall strategy remains authoritative."
        )
        return

    interpretation = result["interpretation"]

    st.markdown("#### AI Interpretation")
    st.caption(
        "This section explains the verified pit-wall strategy. It does not replace or override the application-owned decision."
    )

    st.markdown("**Pit Recommendation**")
    st.write(interpretation["pit_recommendation"])

    st.markdown("**Pace Guidance**")
    st.write(interpretation["pace_guidance"])

    st.markdown("**Tire Guidance**")
    st.write(interpretation["tire_guidance"])

    st.markdown("**Risk Summary**")
    st.write(interpretation["risk_summary"])

    st.markdown("**Overall Strategy**")
    st.write(interpretation["overall_strategy"])


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
orchestrated_strategy = run_strategy_orchestrator(
    data,
    history=st.session_state.history,
)
verification = verify_strategy(orchestrated_strategy)
rules_strategy = orchestrated_strategy["rules"]
tire_assessment = orchestrated_strategy["tire"]
pace_assessment = orchestrated_strategy["pace"]
track_assessment = orchestrated_strategy["track"]
fallback_components = orchestrated_strategy["fallback_components"]

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

# --- Verified publication boundary ---
st.subheader("Pit Wall Strategy")

verification_col1, verification_col2 = st.columns(2)
verification_col1.metric("Verification", verification["status"])
verification_col2.metric("Checks Run", verification["checks_run"])

if fallback_components:
    st.warning(
        "Degraded mode active. Deterministic fallback is currently handling: "
        f"{', '.join(fallback_components)}. The verifier requires a conservative publication state while fallback is active."
    )
else:
    st.caption("All specialist components are operating normally; no deterministic fallbacks are active.")

if verification["publishable"]:
    strategy_col1, strategy_col2, strategy_col3 = st.columns(3)
    strategy_col1.metric("Final Action", orchestrated_strategy["final_action"])
    strategy_col2.metric("Priority", orchestrated_strategy["priority"])
    strategy_col3.metric("Confidence", f"{orchestrated_strategy['confidence']:.0%}")

    if orchestrated_strategy["priority"] == "High":
        st.warning(orchestrated_strategy["summary"])
    else:
        st.success(orchestrated_strategy["summary"])

    st.caption(verification["rationale"])
else:
    st.error(
        "Strategy publication blocked. The verifier rejected the orchestrated strategy, "
        "so no authoritative pit-wall action will be published."
    )
    st.write(verification["rationale"])
    for violation in verification["violations"]:
        st.write(f"- {violation}")

st.caption(
    "The pit-wall strategy is published only after deterministic verification. "
    "Specialist outputs below are supporting evidence, not independent final decisions."
)

# --- Specialist evidence ---
with st.expander("Specialist Analysis", expanded=True):
    st.markdown("#### Tire Analyst")
    tire_col1, tire_col2 = st.columns(2)
    tire_col1.metric("Tire Risk", tire_assessment["risk"])
    tire_col2.metric("Recommended Action", tire_assessment["action"])
    st.write(tire_assessment["rationale"])
    st.caption(
        f"Assessment confidence: {tire_assessment['confidence']:.0%}. "
        "The current telemetry does not model tire age, compound, or measured wear, so the system does not estimate remaining tire life."
    )

    st.markdown("#### Pace Analyst")
    pace_col1, pace_col2, pace_col3, pace_col4, pace_col5 = st.columns(5)
    pace_col1.metric("Pace Status", pace_assessment["status"])
    pace_col2.metric("Recommended Action", pace_assessment["action"])
    pace_col3.metric("Reference Lap (s)", pace_assessment["reference_lap_time"])
    pace_col4.metric("Delta to Reference (s)", pace_assessment["delta_to_reference"])
    pace_col5.metric("Comparable Laps", pace_assessment["history_laps"])
    st.write(pace_assessment["rationale"])
    st.caption(
        f"Assessment confidence: {pace_assessment['confidence']:.0%}. "
        "Pace is compared with the median of up to the three most recent laps under the same reported track condition."
    )

    st.markdown("#### Track Conditions Analyst")
    track_col1, track_col2, track_col3 = st.columns(3)
    track_col1.metric("Observed Condition", track_assessment["condition"])
    track_col2.metric("Operational Risk", track_assessment["risk"])
    track_col3.metric("Recommended Action", track_assessment["action"])
    st.write(track_assessment["rationale"])
    st.caption(f"Assessment confidence: {track_assessment['confidence']:.0%}")

    st.markdown("#### Rules Engine")
    if rules_strategy["priority"] == "High":
        st.warning(f"Priority: {rules_strategy['priority']}")
    else:
        st.info(f"Priority: {rules_strategy['priority']}")
    st.write(rules_strategy["recommendation"])

# --- Deterministic evaluation visibility ---
with st.expander("Deterministic Evaluation", expanded=False):
    evaluation = run_evaluation_suite()
    evaluation_metrics = evaluation["metrics"]

    eval_col1, eval_col2, eval_col3, eval_col4 = st.columns(4)
    eval_col1.metric(
        "Scenario Pass Rate",
        f"{evaluation_metrics['scenario_pass_rate']:.0%}",
    )
    eval_col2.metric(
        "Publishable Rate",
        f"{evaluation_metrics['publishable_rate']:.0%}",
    )
    eval_col3.metric(
        "Action Match Rate",
        f"{evaluation_metrics['expected_action_match_rate']:.0%}",
    )
    eval_col4.metric(
        "Priority Match Rate",
        f"{evaluation_metrics['expected_priority_match_rate']:.0%}",
    )

    st.dataframe(pd.DataFrame(evaluation["results"]), use_container_width=True)
    st.caption(
        "These are deterministic regression scenarios executed without any LLM calls. "
        "They are engineering checks for expected bounded behavior, not claims of real-world race accuracy."
    )

# --- LLM safeguards status ---
st.subheader("LLM Strategy Interpreter")

calls_remaining = MAX_LLM_CALLS_PER_SESSION - st.session_state.llm_calls_used
elapsed = time.time() - st.session_state.last_llm_call_time
cooldown_remaining = max(0, int(LLM_COOLDOWN_SECONDS - elapsed))

status_col1, status_col2, status_col3 = st.columns(3)
status_col1.metric("LLM Calls Used", st.session_state.llm_calls_used)
status_col2.metric("Calls Remaining", max(0, calls_remaining))
status_col3.metric("Cooldown (s)", cooldown_remaining)

current_state_hash = build_state_hash(data, df, orchestrated_strategy, verification)
same_state = st.session_state.last_llm_state_hash == current_state_hash

llm_disabled_reason = get_llm_disabled_reason(
    publishable=verification["publishable"],
    fallback_components=fallback_components,
    lap=data["lap"],
    min_lap=MIN_LAPS_FOR_LLM,
    calls_used=st.session_state.llm_calls_used,
    max_calls=MAX_LLM_CALLS_PER_SESSION,
    cooldown_remaining=cooldown_remaining,
    same_state=same_state,
)

if llm_disabled_reason:
    st.caption(llm_disabled_reason)

generate_clicked = st.button(
    "Generate AI Strategy Interpretation",
    disabled=llm_disabled_reason is not None
)

if generate_clicked:
    # Reuse cached output if telemetry and verified strategy state are unchanged.
    if same_state and st.session_state.last_llm_response:
        llm_result = st.session_state.last_llm_response
        st.info("Using cached AI interpretation for the current verified strategy state.")
    else:
        with st.spinner("Generating AI interpretation..."):
            llm_result = generate_llm_strategy(data, df, orchestrated_strategy)

        st.session_state.last_llm_call_time = time.time()
        st.session_state.llm_calls_used += 1
        st.session_state.last_llm_state_hash = current_state_hash
        st.session_state.last_llm_response = llm_result

    render_llm_interpretation(llm_result)

# Keep showing the last validated interpretation after reruns.
if st.session_state.last_llm_response:
    with st.expander("Most Recent AI Interpretation", expanded=False):
        render_llm_interpretation(st.session_state.last_llm_response)

st.success("Telemetry system active")
