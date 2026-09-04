import os
from unittest.mock import patch

from src.extract import _fallback_models


def test_retired_lite_model_is_never_called_from_legacy_configuration():
    env = {
        "GEMINI_MODEL_FALLBACKS": "gemini-2.5-flash-lite,models/gemini-2.5-flash-lite,gemini-3.5-flash",
    }
    with patch.dict(os.environ, env, clear=True):
        models = _fallback_models("gemini-2.5-flash-lite")

    assert models == ["gemini-3.5-flash-lite", "gemini-3.5-flash"]
    assert all("2.5-flash-lite" not in model for model in models)
