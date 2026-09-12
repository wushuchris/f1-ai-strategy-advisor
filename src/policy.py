def get_llm_disabled_reason(
    *,
    publishable: bool,
    fallback_components: list[str],
    lap: int,
    min_lap: int,
    calls_used: int,
    max_calls: int,
    cooldown_remaining: int,
    same_state: bool,
) -> str | None:
    """Return the application-owned reason LLM interpretation is unavailable, if any."""

    if not publishable:
        return "AI interpretation is disabled because the deterministic pit-wall strategy failed verification."

    if fallback_components:
        return (
            "AI interpretation is disabled while deterministic specialist fallback is active. "
            "The conservative verified pit-wall strategy remains authoritative until all specialists recover."
        )

    if lap < min_lap:
        return f"Simulate to at least lap {min_lap} before generating an AI interpretation."

    if calls_used >= max_calls:
        return "Session limit reached for AI interpretations. Reset the simulation to start over."

    if cooldown_remaining > 0 and not same_state:
        return f"Please wait {cooldown_remaining} seconds before generating another new AI interpretation."

    return None
