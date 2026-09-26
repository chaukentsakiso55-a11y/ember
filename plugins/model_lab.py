from __future__ import annotations

from core.model_manager import list_models, benchmark, configure, diagnostics
from core.feature_hub import set_model_mode, get

PLUGIN = {
    "permissions": ["models.local", "network.localhost"],
    "name": "model_lab",
    "description": (
        "Inspect and configure Ember's local/OpenAI-compatible LLMs, run health "
        "diagnostics and benchmarks, tune generation, set fallback models, and "
        "switch Ember between auto, online and local routing."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {"type": "STRING", "description": "list, benchmark, mode, status, diagnose, configure"},
            "value": {"type": "STRING", "description": "Mode for action=mode."},
            "prompt": {"type": "STRING"},
            "provider": {"type": "STRING", "description": "ollama or openai-compatible."},
            "url": {"type": "STRING"},
            "model": {"type": "STRING"},
            "max_tokens": {"type": "INTEGER", "description": "Maximum generated tokens, 32-8192."},
            "temperature": {"type": "NUMBER", "description": "Generation temperature, 0.0-2.0."},
            "fallback_models": {"type": "STRING", "description": "Comma-separated fallback model names."},
        },
        "required": ["action"],
    },
    "behavior": "NON_BLOCKING",
    "scheduling": "WHEN_IDLE",
}


def run(p, player=None, session_memory=None):
    action = str(p.get("action", "")).lower().strip()
    if action == "list":
        return "Local models: " + (", ".join(list_models()) or "none detected")
    if action == "benchmark":
        return str(benchmark(p.get("prompt") or "Reply with exactly: EMBER READY"))
    if action == "mode":
        return f"Model mode set to {set_model_mode(p.get('value') or 'auto')}"
    if action in {"status", "diagnose"}:
        return str({"route_mode": get("model_mode", "auto"), **diagnostics()})
    if action == "configure":
        return str(configure(
            p.get("provider"),
            p.get("url"),
            p.get("model"),
            max_tokens=p.get("max_tokens"),
            temperature=p.get("temperature"),
            fallback_models=p.get("fallback_models"),
        ))
    return "Use list, benchmark, mode, status, diagnose, or configure."
