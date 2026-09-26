"""Cloud/local provider-pool text chat for Ember."""
from __future__ import annotations

from core.feature_hub import audit, kill_switch_enabled
from core.llm_client import call_llm
from core.local_mode import SYSTEM, _compact_history


def ask_routed(text: str, history: list[dict] | None = None, tools: list | None = None) -> dict:
    if kill_switch_enabled():
        return {"content": "Ember's kill switch is active. Agent execution is paused.", "tool_calls": []}
    messages = [{"role": "system", "content": SYSTEM}]
    messages.extend(_compact_history(history))
    messages.append({"role": "user", "content": text})
    audit("model", "provider_pool", text[:120])
    return call_llm(messages, tools=tools)
