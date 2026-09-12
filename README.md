# 🏎️ F1 AI Strategy Advisor

[![Tests](https://github.com/wushuchris/f1-ai-strategy-advisor/actions/workflows/tests.yml/badge.svg)](https://github.com/wushuchris/f1-ai-strategy-advisor/actions/workflows/tests.yml)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://f1-ai-strategy-advisor-ekkzao7ckhtbv3sfh5v4nd.streamlit.app/)

A cloud-deployed Formula 1 strategy system that uses simulated IoT telemetry, deterministic specialist analysis, centralized orchestration, verification, and bounded LLM interpretation.

The project began as an IoT/AI coursework concept and has been extended into a portfolio project focused on trustworthy agent engineering: typed contracts, application-owned control, failure containment, evaluation, CI, and observable decision boundaries.

---

## 📌 Portfolio Snapshot

- **System:** Governed multi-agent race-strategy advisor
- **Specialists:** Tire, Pace, and Track Conditions analysts
- **Control:** Centralized orchestrator + deterministic publication verifier
- **Reliability:** Conservative specialist fallbacks, degraded-mode observability, regression scenarios, CI
- **LLM role:** Structured interpretation of an already-verified strategy; never the publication authority
- **Deployment:** Streamlit Community Cloud with Hugging Face Inference Providers
- **Live demo:** https://f1-ai-strategy-advisor-ekkzao7ckhtbv3sfh5v4nd.streamlit.app/
- **Concise project brief:** [`PORTFOLIO.md`](PORTFOLIO.md)

---

## 🚀 Overview

The application simulates lap-by-lap race telemetry including lap time, tire temperature, fuel level, and observed track condition. That telemetry is validated before entering a governed strategy pipeline.

Three deterministic specialists independently assess tire state, pace behavior, and track conditions. A centralized orchestrator combines those outputs with a deterministic rules engine, and a verifier checks the resulting strategy before it is allowed to become the authoritative pit-wall recommendation.

An LLM accessed through Hugging Face Inference Providers is intentionally downstream of that publication boundary. It explains the verified strategy in structured JSON, but it does not own routing, validation, escalation, or the final decision. Application-owned policy determines whether LLM interpretation is eligible to run, including verification status, specialist fallback state, minimum lap requirements, session limits, cooldowns, and same-state cache reuse.

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
- Typed `fallback_components` metadata for explicit degraded-mode observability
- Application-owned, testable LLM eligibility policy
- Structured LLM interpretation validated before display and suppressed during fallback mode
- Same-state LLM response reuse with stale-response suppression after telemetry or strategy changes
- Deterministic evaluation suite for known race-state scenarios
- Automated pytest coverage through GitHub Actions
- Streamlit Community Cloud deployment
- Hugging Face token isolation through Streamlit secrets and fine-grained permissions
- Session-level LLM rate limiting and cooldowns

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
Application LLM Eligibility Policy
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
- degraded-mode metadata
- publication priority
- confidence propagation
- final pit-wall recommendation
- verification and publication gating
- LLM eligibility policy
- cache-state matching before previously generated interpretation is shown

**The LLM contributes:**
- concise explanation of the already-verified strategy
- structured pit, pace, tire, risk, and overall guidance

The LLM cannot directly change the application-owned final strategy action and is not invoked while a specialist fallback is active.

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
- Fallback use is recorded explicitly in typed `fallback_components` metadata rather than inferred from prose.
- A failed specialist drives publication confidence to `0.0` and requires a conservative high-priority action rather than allowing `Maintain` or `Review Strategy` to publish.
- `Prepare to Pit` can only be published when the Tire Analyst explicitly emits that bounded action.
- The verifier checks priority consistency, pit-action preservation, maintain-state safety, published confidence, and fallback publication policy.
- The Streamlit dashboard visibly reports whether degraded mode is active and which specialist components are affected.
- LLM interpretation is disabled during fallback mode so probabilistic explanation cannot obscure a degraded analytical state.
- LLM eligibility is centralized in deterministic application policy rather than duplicated as UI-only control logic.
- A previously generated interpretation is only shown when its state hash matches the current telemetry and verified strategy, preventing stale AI guidance from appearing under a newer pit-wall state.
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

Malformed JSON, missing fields, and unexpected fields are rejected. LLM failure never replaces or invalidates the deterministic pit-wall strategy. The interpreter is also disabled whenever deterministic specialist fallback mode is active.

A separate deterministic policy function controls whether an LLM request is allowed based on publication status, fallback state, lap threshold, per-session request budget, cooldown timing, and whether an identical verified state can reuse a cached response.

---

## 🧪 Evaluation and Testing

A deterministic evaluation suite exercises 11 known operating conditions without using paid LLM inference. Current scenarios include:

- stable dry state
- overheated tires
- low fuel
- wet track
- pace degradation
- critical pace loss
- insufficient pace history
- tire-management threshold
- exact pace-degradation threshold
- exact critical-pace threshold
- late-race lap state without tire-age evidence

The suite tracks scenario pass rate, publication rate, expected-action match rate, and expected-priority match rate.

Regression tests also cover:

- telemetry validation
- specialist threshold behavior
- race-lap vs. tire-age evidence boundaries
- same-condition pace baselines
- orchestration precedence
- publication verification
- structured fallback-component metadata
- conservative fallback publication policy
- multi-specialist failure containment
- structured LLM response validation
- deterministic LLM eligibility policy
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
5. Contain specialist failures with conservative application-owned fallbacks and record affected components explicitly.
6. Aggregate validated evidence in the centralized orchestrator.
7. Verify the proposed strategy against deterministic publication rules, including fallback-policy invariants.
8. Publish the authoritative pit-wall strategy only if verification passes.
9. Evaluate application-owned LLM eligibility policy.
10. Optionally request a structured LLM explanation only when policy permits.
11. Validate the LLM response before rendering it in the dashboard.
12. Reuse a cached interpretation only when it still corresponds to the current verified strategy state.

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
│   ├── policy.py
│   ├── rules.py
│   ├── schemas.py
│   ├── simulation.py
│   └── verifier.py
├── tests/
├── PORTFOLIO.md
└── requirements-dev.txt
```

---

## 🎯 Engineering Focus

This project is primarily an exercise in governed AI systems rather than in maximizing the number of agents. The engineering emphasis is on clear authority boundaries, deterministic control, evidence-bounded reasoning, observable specialist outputs, safe fallbacks, testable LLM eligibility policy, structured model responses, regression evaluation, and cloud deployment.
