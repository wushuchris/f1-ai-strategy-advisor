from src.policy import get_llm_disabled_reason


def base_kwargs():
    return {
        "publishable": True,
        "fallback_components": [],
        "lap": 5,
        "min_lap": 5,
        "calls_used": 0,
        "max_calls": 5,
        "cooldown_remaining": 0,
        "same_state": False,
    }


def test_llm_policy_allows_healthy_verified_state():
    assert get_llm_disabled_reason(**base_kwargs()) is None


def test_llm_policy_blocks_unverified_strategy():
    kwargs = base_kwargs()
    kwargs["publishable"] = False

    reason = get_llm_disabled_reason(**kwargs)

    assert "failed verification" in reason


def test_llm_policy_blocks_specialist_fallback():
    kwargs = base_kwargs()
    kwargs["fallback_components"] = ["Pace"]

    reason = get_llm_disabled_reason(**kwargs)

    assert "fallback is active" in reason


def test_llm_policy_blocks_before_minimum_lap():
    kwargs = base_kwargs()
    kwargs["lap"] = 4

    reason = get_llm_disabled_reason(**kwargs)

    assert "at least lap 5" in reason


def test_llm_policy_blocks_session_limit():
    kwargs = base_kwargs()
    kwargs["calls_used"] = 5

    reason = get_llm_disabled_reason(**kwargs)

    assert "Session limit reached" in reason


def test_llm_policy_blocks_new_state_during_cooldown():
    kwargs = base_kwargs()
    kwargs["cooldown_remaining"] = 12

    reason = get_llm_disabled_reason(**kwargs)

    assert "wait 12 seconds" in reason


def test_llm_policy_allows_same_state_cache_during_cooldown():
    kwargs = base_kwargs()
    kwargs["cooldown_remaining"] = 12
    kwargs["same_state"] = True

    assert get_llm_disabled_reason(**kwargs) is None
