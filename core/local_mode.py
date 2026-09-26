"""Local/auto model routing for Ember typed conversations."""
from __future__ import annotations

from core.feature_hub import get, audit, kill_switch_enabled
from core.llm_client import call_llm, ensure_ollama_running

SYSTEM = """You are Ember, an advanced local desktop AI assistant.
Be accurate, practical, and concise unless the user asks for depth. Maintain
context across the conversation. Never claim a computer action succeeded unless
a tool actually returned success. If information is uncertain, say what is
uncertain instead of inventing details. Prefer a clear direct answer over filler.
"""


def local_available() -> bool:
    try:
        return bool(ensure_ollama_running(timeout=2))
    except Exception:
        return False


def should_use_local(online_connected: bool) -> bool:
    mode = str(get("model_mode", "auto")).lower()
    if mode == "local":
        return True
    if mode == "online":
        return False
    return not online_connected and local_available()


def _compact_history(history: list[dict] | None) -> list[dict]:
    """Keep recent context without blindly overflowing small local models."""
    if not history:
        return []
    try:
        max_turns = max(4, min(40, int(get("llm_history_turns", 20))))
    except Exception:
        max_turns = 20
    try:
        max_chars = max(4000, min(80000, int(get("llm_history_chars", 24000))))
    except Exception:
        max_chars = 24000

    selected: list[dict] = []
    used = 0
    for item in reversed(history[-max_turns:]):
        if not isinstance(item, dict):
            continue
        text = str(item.get("content") or "")
        if selected and used + len(text) > max_chars:
            break
        selected.append({"role": item.get("role", "user"), "content": text})
        used += len(text)
    selected.reverse()
    return selected


def ask_local(text: str, history: list[dict] | None = None, tools: list | None = None) -> dict:
    if kill_switch_enabled():
        return {"content": "Ember's kill switch is active. Local agent execution is paused.", "tool_calls": []}
    messages = [{"role": "system", "content": SYSTEM}]
    messages.extend(_compact_history(history))
    messages.append({"role": "user", "content": text})
    audit("model", "local_llm", text[:120])
    return call_llm(messages, tools=tools, provider_id="ollama", local_only=True)
