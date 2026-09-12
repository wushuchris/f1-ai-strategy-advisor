# F1 AI Strategy Advisor — Portfolio Summary

## What this project demonstrates

F1 AI Strategy Advisor is a cloud-deployed governed multi-agent system built around simulated Formula 1 telemetry. The project demonstrates how deterministic application logic, typed specialist contracts, verification, bounded LLM use, failure containment, and automated evaluation can be combined into a trustworthy AI workflow.

## Engineering story

The system is intentionally designed so the LLM does not own the final decision. Telemetry is validated first, deterministic specialists assess tire state, pace, and track conditions, a centralized orchestrator combines the evidence, and a verifier decides whether the resulting pit-wall strategy may be published. Only after that boundary passes can the LLM produce a structured explanation of the already-verified strategy.

This architecture reflects a core design principle:

> **Models interpret. Application code validates, orchestrates, verifies, and publishes.**

## Reusable engineering primitives

- Typed Pydantic contracts for telemetry and specialist outputs
- Deterministic specialist agents with bounded action spaces
- Centralized orchestration and publication authority
- Fail-closed verification before strategy publication
- Conservative deterministic fallbacks for specialist failure
- Structured fallback-component observability
- Application-owned LLM eligibility policy
- Same-state response caching with stale-output suppression
- Deterministic evaluation scenarios that avoid paid inference
- GitHub Actions regression testing
- Streamlit Community Cloud deployment with secret isolation

## AI and agent-engineering concepts

This project demonstrates a governed alternative to loosely coordinated agent systems. Rather than allowing specialists or an LLM to vote on or directly publish a race strategy, the application owns the protocol and authority boundaries. Specialists contribute structured interpretation; deterministic code decides what can be trusted and published.

The result is a multi-agent pattern that emphasizes:

- bounded autonomy
- evidence discipline
- deterministic control
- explicit failure states
- observable handoffs
- application-owned authority
- safe probabilistic interpretation

## Technical stack

Python, Streamlit, pandas, Pydantic, Hugging Face Inference Providers, Llama 3.1 8B Instruct, pytest, GitHub Actions, Streamlit Community Cloud.

## Deployment

Live demo: https://f1-ai-strategy-advisor-ekkzao7ckhtbv3sfh5v4nd.streamlit.app/

The public demo uses per-session rate limiting and cooldown controls for LLM inference. The deterministic strategy pipeline remains operational even when the LLM layer is unavailable.
