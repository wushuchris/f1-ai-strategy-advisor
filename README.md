# 🏎️ F1 AI Strategy Advisor

A cloud-deployed Formula 1 strategy system that uses simulated IoT telemetry, deterministic specialist analysis, centralized orchestration, verification, and bounded LLM interpretation.

The project began as an IoT/AI coursework concept and has been extended into a portfolio project focused on trustworthy agent engineering: typed contracts, application-owned control, failure containment, evaluation, CI, and observable decision boundaries.

---

## 🚀 Overview

The application simulates lap-by-lap race telemetry including lap time, tire temperature, fuel level, and observed track condition. That telemetry is validated before entering a governed strategy pipeline.

Three deterministic specialists independently assess tire state, pace behavior, and track conditions. A centralized orchestrator combines those outputs with a deterministic rules engine, and a verifier checks the resulting strategy before it is allowed to become the authoritative pit-wall recommendation.

A Hugging Face-hosted LLM is intentionally downstream of that publication boundary. It explains the verified strategy in structured JSON, but it does not own routing, validation, escalation, or the final decision.

> **Models interpret. Application code validates, orchestrates, verifies, and publishes.**

---

## ⚙️ Key Features

- Interactive lap-by-lap IoT-style telemetry simulation
- Pydantic validation for telemetry, specialist outputs, orchestration, verification, and LLM responses
- Deterministic rules engine with evidence-bounded recommendations
- Tire Analyst with bounded temperature- and condition-based reasoning
- Trend-aware Pace Analyst using recent same-condition telemetry rather than fixed lap-time targets
- Track Conditions Analyst limited to observed surface state rather than unsupported forecasting
- Centralized strategy orchestrator that owns the final recommendation boundary
- Deterministic publication verifier with fail-closed consistency checks
- Conservative specialist fallbacks when an analysis component fails
- Structured LLM interpretation validated before display
- Deterministic evaluation suite for known race-state scenarios
- Automated pytest coverage through GitHub Actions
- Streamlit Community Cloud deployment
- Hugging Face token isolation through Streamlit secrets and fine-grained permissions
- Session-level LLM rate limiting, cooldowns, and same-state response reuse

---

## 🏗️ Architecture

```text
Synthetic IoT Telemetry
        ↓
Pydantic Telemetry Validation
        ↓
┌──────────────────────────────┐
│ Tire Analyst                 │
│ Pace Analyst                 │
│ Track Conditions Analyst     │
│ Deterministic Rules Engine   │
└──────────────────────────────┘
        ↓
Centralized Strategy Orchestrator
        ↓
Deterministic Strategy Verifier
        ↓
Verified Pit-Wall Strategy
        ↓
┌──────────────────────┐
│ Streamlit Dashboard  │
│ LLM Interpretation   │
└──────────────────────┘
```

### Control boundaries

**Application code owns:**
- telemetry validation
- specialist contracts
- valid strategy actions
- routing and aggregation
- failure fallbacks
- publication priority
- confidence propagation
- final pit-wall recommendation
- verification and publication gating

**The LLM contributes:**
- concise explanation of the already-verified strategy
- structured pit, pace, tire, risk, and overall guidance

The LLM cannot directly change the application-owned final strategy action.

---

## 🧠 Specialist Logic

### Tire Analyst

Uses observed tire temperature and track condition. It does **not** estimate remaining tire life because the current telemetry does not include tire age, compound, or measured wear.

### Pace Analyst

Builds a pace reference from the median of the three most recent prior laps under the same reported track condition. If insufficient comparable history exists, it emits a bounded `Monitoring` state rather than inventing a baseline.

### Track Conditions Analyst

Responds only to the reported `Dry` or `Wet` track state. It does not infer future weather.

### Rules Engine

Provides deterministic guardrail signals for high tire temperature, low fuel, and wet conditions without treating race lap number as tire age.

---

## 🛡️ Governance and Reliability

The system is designed so one model or specialist cannot silently become the decision authority.

- Specialist outputs are schema-validated.
- Specialist exceptions are contained with conservative deterministic fallbacks.
- A failed specialist drives confidence to `0.0` and causes a conservative `Manage and Reassess` state rather than an unsupported pit recommendation.
- `Prepare to Pit` can only be published when the Tire Analyst explicitly emits that bounded action.
- The verifier checks priority consistency, pit-action preservation, maintain-state safety, and published confidence.
- The deterministic strategy remains available when Hugging Face inference is unavailable or malformed.

---

## 🤖 LLM Interpretation Layer

The application uses:

- **Hugging Face Inference Providers**
- **`meta-llama/Llama-3.1-8B-Instruct`**

The model receives the verified orchestrated strategy and recent telemetry, then returns JSON matching a strict Pydantic contract:

```json
{
  "pit_recommendation": "...",
  "pace_guidance": "...",
  "tire_guidance": "...",
  "risk_summary": "...",
  "overall_strategy": "..."
}
```

Malformed JSON, missing fields, and unexpected fields are rejected. LLM failure never replaces or invalidates the deterministic pit-wall strategy.

---

## 🧪 Evaluation and Testing

A deterministic evaluation suite exercises known operating conditions without using paid LLM inference. Current scenarios include:

- stable dry state
- overheated tires
- low fuel
- wet track
- pace degradation
- critical pace loss
- insufficient pace history

The suite tracks scenario pass rate, publication rate, expected-action match rate, and expected-priority match rate.

Regression tests also cover:

- telemetry validation
- specialist threshold behavior
- race-lap vs. tire-age evidence boundaries
- same-condition pace baselines
- orchestration precedence
- publication verification
- specialist failure containment
- structured LLM response validation
- simulated fuel-load and tire-temperature effects

GitHub Actions runs the deterministic pytest suite on pushes and pull requests without requiring an `HF_TOKEN`.

---

## 🧰 Tech Stack

- **Application:** Python, Streamlit, pandas
- **Validation:** Pydantic
- **AI:** Hugging Face Inference Providers, Llama 3.1 8B Instruct
- **Testing:** pytest, GitHub Actions
- **Deployment:** Streamlit Community Cloud
- **Security:** Streamlit Secrets, fine-grained Hugging Face token

---

## 🔄 Decision Flow

1. Initialize a validated synthetic race state.
2. Simulate the next lap with fuel burn, tire-temperature movement, track state, and lap-time variation.
3. Validate telemetry through the application schema.
4. Run deterministic Tire, Pace, and Track specialists plus the rules engine.
5. Contain specialist failures with conservative application-owned fallbacks.
6. Aggregate validated evidence in the centralized orchestrator.
7. Verify the proposed strategy against deterministic publication rules.
8. Publish the authoritative pit-wall strategy only if verification passes.
9. Optionally request a structured LLM explanation of that verified strategy.
10. Validate the LLM response before rendering it in the dashboard.

---

## 🌐 Deployment

Live Streamlit application:

https://f1-ai-strategy-advisor-ekkzao7ckhtbv3sfh5v4nd.streamlit.app/

The public demo rate-limits LLM requests per session to control inference usage. The deterministic strategy pipeline does not depend on the LLM being available.

---

## 📁 Project Structure

```text
f1-ai-strategy-advisor/
├── .github/
│   └── workflows/
│       └── tests.yml
├── app/
│   ├── streamlit_app.py
│   └── requirements.txt
├── src/
│   ├── agents/
│   │   ├── pace_agent.py
│   │   ├── tire_agent.py
│   │   └── track_agent.py
│   ├── evaluation.py
│   ├── llm.py
│   ├── orchestrator.py
│   ├── rules.py
│   ├── schemas.py
│   ├── simulation.py
│   └── verifier.py
├── tests/
└── requirements-dev.txt
```

---

## 🎯 Engineering Focus

This project is primarily an exercise in governed AI systems rather than in maximizing the number of agents. The engineering emphasis is on clear authority boundaries, deterministic control, evidence-bounded reasoning, observable specialist outputs, safe fallbacks, structured model responses, regression evaluation, and cloud deployment.
