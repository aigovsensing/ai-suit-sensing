import os
from unittest.mock import patch

from src.extract import (
    _fallback_models,
    _is_permanent_billing_error,
    _is_rate_limit_error,
    extract_with_llm,
)


def test_retired_lite_model_is_never_called_from_legacy_configuration():
    env = {
        "GEMINI_MODEL_FALLBACKS": "gemini-2.5-flash-lite,models/gemini-2.5-flash-lite,gemini-3.5-flash",
    }
    with patch.dict(os.environ, env, clear=True):
        models = _fallback_models("gemini-2.5-flash-lite")

    assert models == ["gemini-3.5-flash-lite", "gemini-3.5-flash"]
    assert all("2.5-flash-lite" not in model for model in models)


def test_depleted_prepaid_credit_is_not_retried_as_a_transient_limit():
    error = Exception("429: Your prepayment credits are depleted. Please manage billing.")
    assert _is_permanent_billing_error(error)
    assert not _is_rate_limit_error(error)


def test_temporary_rate_limit_remains_retryable():
    assert _is_rate_limit_error(Exception("429 RESOURCE_EXHAUSTED: rate limit exceeded"))


def test_depleted_credit_does_not_try_the_remaining_model_chain(monkeypatch):
    calls = []

    class BrokenModel:
        def __init__(self, name):
            calls.append(name)

        def generate_content(self, _prompt):
            raise Exception("429: Your prepayment credits are depleted.")

    fake_genai = type("FakeGenAI", (), {
        "configure": staticmethod(lambda **_kwargs: None),
        "GenerativeModel": BrokenModel,
    })
    monkeypatch.setitem(__import__("sys").modules, "google.generativeai", fake_genai)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    monkeypatch.setattr("src.extract._MIN_CALL_INTERVAL_SEC", 0)

    assert extract_with_llm("issue text") == []
    assert calls == ["gemini-3.5-flash-lite"]
