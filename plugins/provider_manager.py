from __future__ import annotations

from core import provider_pool

PLUGIN = {
    "permissions": ["models.local", "network.localhost"],
    "name": "provider_manager",
    "description": (
        "Inspect Ember's multi-provider AI routing without revealing API keys, "
        "enable/disable providers, or choose which provider should be tried first."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {"type": "STRING", "description": "status, enable, disable, default"},
            "provider": {"type": "STRING", "description": "Provider id such as openai, openrouter, anthropic, groq, xkiro, gemini, ollama."},
        },
        "required": ["action"],
    },
    "behavior": "NON_BLOCKING",
    "scheduling": "WHEN_IDLE",
}


def run(p, player=None, session_memory=None):
    action = str(p.get("action") or "status").strip().lower()
    provider = str(p.get("provider") or "").strip().lower()
    if action in {"status", "list"}:
        return provider_pool.status()
    if action == "enable":
        return {"provider": provider, "enabled": provider_pool.set_provider_enabled(provider, True)}
    if action == "disable":
        return {"provider": provider, "enabled": provider_pool.set_provider_enabled(provider, False)}
    if action in {"default", "select", "prefer"}:
        return {"default_provider": provider_pool.set_default_provider(provider)}
    return "Use status, enable, disable, or default. API key values are intentionally never returned."
