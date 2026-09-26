"""Multi-provider LLM routing for Ember.

This module deliberately keeps provider metadata separate from credentials:
  config/providers.json          provider URLs, priorities, routing preferences
  config/provider_secrets.json   one or more API keys per provider

No API key is ever returned by status()/diagnostics() or included in normal
error messages. Keys may be rotated within a provider and providers can fall
back to one another without changing Ember's higher-level chat code.
"""
from __future__ import annotations

import json
import os
import threading
import time
from pathlib import Path
from typing import Iterable

import requests

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"
PROVIDERS_PATH = CONFIG_DIR / "providers.json"
SECRETS_PATH = CONFIG_DIR / "provider_secrets.json"
LEGACY_KEYS_PATH = CONFIG_DIR / "api_keys.json"

_lock = threading.RLock()
_model_cache: dict[str, tuple[float, list[str]]] = {}
_key_cursor: dict[str, int] = {}
_key_cooldown: dict[tuple[str, int], float] = {}
_provider_cooldown: dict[str, float] = {}
_MODEL_CACHE_SECONDS = 600
_KEY_COOLDOWN_SECONDS = 180
_PROVIDER_COOLDOWN_SECONDS = 45

_BAD_MODEL_MARKERS = (
    "embedding", "moderation", "whisper", "tts", "audio", "transcribe",
    "image", "dall-e", "realtime", "search-preview",
)


def _json(path: Path, default):
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
        return obj
    except Exception:
        return default


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def load_config() -> dict:
    obj = _json(PROVIDERS_PATH, {})
    return obj if isinstance(obj, dict) else {}


def load_secrets() -> dict[str, list[str]]:
    raw = _json(SECRETS_PATH, {})
    raw = raw if isinstance(raw, dict) else {}
    out: dict[str, list[str]] = {}
    for provider_id, values in raw.items():
        if isinstance(values, str):
            values = [values]
        if not isinstance(values, list):
            continue
        clean: list[str] = []
        for value in values:
            value = str(value or "").strip()
            if value and value not in clean:
                clean.append(value)
        out[str(provider_id).lower()] = clean

    # Preserve Ember's pre-existing Gemini key without duplicating it into the
    # imported Infinity secret file.
    legacy = _json(LEGACY_KEYS_PATH, {})
    gemini = str(legacy.get("gemini_api_key") or "").strip() if isinstance(legacy, dict) else ""
    if gemini:
        out.setdefault("gemini", [])
        if gemini not in out["gemini"]:
            out["gemini"].insert(0, gemini)
    return out


def save_keys(provider_id: str, keys: Iterable[str]) -> int:
    """Replace one provider's key list. Returns the number of stored keys."""
    pid = str(provider_id or "").strip().lower()
    if not pid:
        raise ValueError("provider_id is required")
    raw = _json(SECRETS_PATH, {})
    raw = raw if isinstance(raw, dict) else {}
    clean: list[str] = []
    for key in keys:
        key = str(key or "").strip()
        if key and key not in clean:
            clean.append(key)
    raw[pid] = clean
    _write_json(SECRETS_PATH, raw)
    with _lock:
        _key_cursor.pop(pid, None)
        for marker in list(_key_cooldown):
            if marker[0] == pid:
                _key_cooldown.pop(marker, None)
    return len(clean)


def add_key(provider_id: str, key: str) -> int:
    pid = str(provider_id or "").strip().lower()
    current = load_secrets().get(pid, [])
    value = str(key or "").strip()
    if value and value not in current:
        current.append(value)
    return save_keys(pid, current)


def _providers() -> list[dict]:
    cfg = load_config()
    rows = cfg.get("providers", [])
    if not isinstance(rows, list):
        return []
    out = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        p = dict(row)
        p["id"] = str(p.get("id") or p.get("provider_kind") or p.get("name") or "").strip().lower()
        if p["id"]:
            out.append(p)
    return out


def enabled() -> bool:
    cfg = _json(LEGACY_KEYS_PATH, {})
    return bool(isinstance(cfg, dict) and cfg.get("multi_provider_enabled", False) and _providers())


def _env_keys(provider: dict) -> list[str]:
    names = provider.get("api_key_env", [])
    if isinstance(names, str):
        names = [names]
    out: list[str] = []
    for name in names if isinstance(names, list) else []:
        value = str(os.environ.get(str(name), "") or "").strip()
        if value and value not in out:
            out.append(value)
    return out


def keys_for(provider: dict) -> list[str]:
    pid = str(provider.get("id") or "").lower()
    out = list(load_secrets().get(pid, []))
    for key in _env_keys(provider):
        if key not in out:
            out.append(key)
    if provider.get("local") and not out:
        return [""]
    return out


def _cooling_provider(pid: str) -> bool:
    with _lock:
        until = _provider_cooldown.get(pid, 0.0)
        if until > time.monotonic():
            return True
        _provider_cooldown.pop(pid, None)
        return False


def _mark_provider_cool(pid: str, seconds: int = _PROVIDER_COOLDOWN_SECONDS) -> None:
    with _lock:
        _provider_cooldown[pid] = time.monotonic() + max(1, seconds)


def _ordered_keys(provider: dict) -> list[tuple[int, str]]:
    pid = str(provider.get("id") or "").lower()
    keys = keys_for(provider)
    if not keys:
        return []
    with _lock:
        start = _key_cursor.get(pid, 0) % len(keys)
    now = time.monotonic()
    ordered: list[tuple[int, str]] = []
    for offset in range(len(keys)):
        idx = (start + offset) % len(keys)
        until = _key_cooldown.get((pid, idx), 0.0)
        if until <= now:
            ordered.append((idx, keys[idx]))
    # If every key is cooling down, permit the oldest one rather than making a
    # provider permanently unreachable after a temporary burst limit.
    if not ordered:
        idx = min(range(len(keys)), key=lambda i: _key_cooldown.get((pid, i), 0.0))
        ordered = [(idx, keys[idx])]
    return ordered


def _mark_key_result(provider: dict, index: int, *, failed: bool, status: int | None = None) -> None:
    pid = str(provider.get("id") or "").lower()
    with _lock:
        if failed and status in {401, 402, 403, 429}:
            _key_cooldown[(pid, index)] = time.monotonic() + _KEY_COOLDOWN_SECONDS
        else:
            _key_cooldown.pop((pid, index), None)
            count = max(1, len(keys_for(provider)))
            _key_cursor[pid] = (index + 1) % count


def _routing_order(provider_id: str | None = None, *, local_only: bool = False) -> list[dict]:
    rows = [p for p in _providers() if bool(p.get("enabled", True))]
    if local_only:
        rows = [p for p in rows if bool(p.get("local", False))]
    if provider_id:
        pid = str(provider_id).strip().lower()
        rows = [p for p in rows if p.get("id") == pid]
    cfg = load_config().get("routing", {})
    order = cfg.get("fallback_order", []) if isinstance(cfg, dict) else []
    order_index = {str(pid).lower(): i for i, pid in enumerate(order if isinstance(order, list) else [])}
    rows.sort(key=lambda p: (order_index.get(p["id"], 10_000), -int(p.get("priority", 0) or 0)))
    return rows


def _headers(provider: dict, key: str, *, json_body: bool = True) -> dict[str, str]:
    headers = {"Accept": "application/json"}
    if json_body:
        headers["Content-Type"] = "application/json"
    kind = str(provider.get("type") or "openai-compatible").lower()
    if kind == "anthropic":
        if key:
            headers["x-api-key"] = key
        headers["anthropic-version"] = "2023-06-01"
    elif key:
        headers["Authorization"] = f"Bearer {key}"
    extras = provider.get("headers")
    if isinstance(extras, dict):
        for k, v in extras.items():
            if isinstance(k, str) and isinstance(v, (str, int, float)):
                headers[k] = str(v)
    return headers


def _root(provider: dict) -> str:
    return str(provider.get("base_url") or "").strip().rstrip("/")


def _clean_model_ids(rows) -> list[str]:
    out: list[str] = []
    if isinstance(rows, dict):
        rows = rows.get("data", rows.get("models", []))
    if not isinstance(rows, list):
        return out
    for item in rows:
        if isinstance(item, str):
            mid = item
        elif isinstance(item, dict):
            mid = item.get("id") or item.get("name") or item.get("model")
        else:
            continue
        mid = str(mid or "").strip()
        if mid.startswith("models/"):
            mid = mid.split("/", 1)[1]
        if mid and mid not in out:
            out.append(mid)
    return out


def discover_models(provider: dict, key: str = "", timeout: int = 8, *, refresh: bool = False) -> list[str]:
    pid = str(provider.get("id") or "").lower()
    now = time.monotonic()
    with _lock:
        cached = _model_cache.get(pid)
        if cached and not refresh and now - cached[0] < _MODEL_CACHE_SECONDS:
            return list(cached[1])
    base = _root(provider)
    if not base:
        return []
    try:
        resp = requests.get(base + "/models", headers=_headers(provider, key, json_body=False), timeout=timeout)
        resp.raise_for_status()
        models = _clean_model_ids(resp.json())
    except Exception:
        # Ollama's native catalog is a useful fallback when its /v1 shim is old.
        if pid == "ollama":
            try:
                native = base[:-3] if base.endswith("/v1") else base
                resp = requests.get(native + "/api/tags", timeout=timeout)
                resp.raise_for_status()
                models = _clean_model_ids(resp.json())
            except Exception:
                models = []
        else:
            models = []
    with _lock:
        _model_cache[pid] = (now, models)
    return models


def _model_score(provider: dict, model: str) -> tuple[int, int]:
    low = model.lower()
    if any(marker in low for marker in _BAD_MODEL_MARKERS):
        return (-1000, 0)
    score = 0
    hints = provider.get("model_hints", [])
    if isinstance(hints, str):
        hints = [hints]
    for rank, hint in enumerate(hints if isinstance(hints, list) else []):
        if str(hint).lower() in low:
            score += max(1, 100 - rank * 5)
            break
    # Prefer general chat/instruct/reasoning names when there is no explicit hint.
    if any(x in low for x in ("chat", "instruct", "gpt", "claude", "gemini", "llama", "qwen", "deepseek", "mistral", "gemma")):
        score += 20
    return (score, -len(model))


def choose_model(provider: dict, key: str = "", explicit: str | None = None, timeout: int = 8) -> str:
    if explicit:
        return str(explicit).strip()
    configured = str(provider.get("model") or "").strip()
    if configured:
        return configured
    configured_models = provider.get("models", [])
    if isinstance(configured_models, list):
        for model in configured_models:
            model = str(model or "").strip()
            if model:
                return model
    models = discover_models(provider, key, timeout=timeout)
    ranked = sorted(models, key=lambda m: _model_score(provider, m), reverse=True)
    ranked = [m for m in ranked if _model_score(provider, m)[0] >= 0]
    return ranked[0] if ranked else ""


def _anthropic_messages(messages: list[dict]) -> tuple[str, list[dict]]:
    systems: list[str] = []
    chat: list[dict] = []
    for item in messages:
        if not isinstance(item, dict):
            continue
        role = str(item.get("role") or "user")
        content = item.get("content", "")
        if role == "system":
            systems.append(str(content))
        elif role in {"user", "assistant"}:
            chat.append({"role": role, "content": content})
        elif role == "tool":
            # Ember's current tool loop synthesises tool results in a fresh user
            # message, but support role=tool defensively for future callers.
            chat.append({"role": "user", "content": f"Tool result: {content}"})
    return "\n\n".join(systems), chat or [{"role": "user", "content": "Hello"}]


def _anthropic_tools(tools: list[dict] | None) -> list[dict]:
    out: list[dict] = []
    for item in tools or []:
        if not isinstance(item, dict):
            continue
        fn = item.get("function") if isinstance(item.get("function"), dict) else item
        name = str(fn.get("name") or "").strip()
        if not name:
            continue
        out.append({
            "name": name,
            "description": str(fn.get("description") or ""),
            "input_schema": fn.get("parameters") or {"type": "object", "properties": {}},
        })
    return out


def _anthropic_request(provider: dict, key: str, model: str, messages: list[dict], tools: list[dict] | None,
                       timeout: int, max_tokens: int, temperature: float) -> dict:
    system, chat = _anthropic_messages(messages)
    body: dict = {"model": model, "messages": chat, "max_tokens": max_tokens}
    if system:
        body["system"] = system
    if 0 <= temperature <= 1:
        body["temperature"] = temperature
    a_tools = _anthropic_tools(tools)
    if a_tools:
        body["tools"] = a_tools
    resp = requests.post(_root(provider) + "/messages", headers=_headers(provider, key), json=body, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    text_parts: list[str] = []
    calls: list[dict] = []
    for block in data.get("content", []) if isinstance(data, dict) else []:
        if not isinstance(block, dict):
            continue
        if block.get("type") == "text":
            text_parts.append(str(block.get("text") or ""))
        elif block.get("type") == "tool_use" and block.get("name"):
            calls.append({
                "id": str(block.get("id") or f"tool_{len(calls)}"),
                "function": {"name": str(block.get("name")), "arguments": block.get("input") or {}},
            })
    return {"content": "".join(text_parts).strip(), "tool_calls": calls, "model": model}


def _openai_request(provider: dict, key: str, model: str, messages: list[dict], tools: list[dict] | None,
                    timeout: int, max_tokens: int, temperature: float) -> dict:
    pid = str(provider.get("id") or "").lower()
    body: dict = {"model": model, "messages": messages, "stream": False}
    if pid in {"openai", "groq"}:
        body["max_completion_tokens"] = max_tokens
    else:
        body["max_tokens"] = max_tokens
    # Some reasoning models only support their default temperature. OpenAI is
    # left at its model default to avoid a needless 400 on those models.
    if pid != "openai":
        body["temperature"] = temperature
    if tools:
        body["tools"] = tools
        body["tool_choice"] = "auto"

    endpoint = _root(provider) + "/chat/completions"
    resp = requests.post(endpoint, headers=_headers(provider, key), json=body, timeout=timeout)
    if resp.status_code == 400:
        low = (resp.text or "").lower()
        # Compatibility servers disagree on which token-limit field they accept.
        retry = dict(body)
        changed = False
        if "max_completion_tokens" in retry and ("max_completion_tokens" in low or "max_tokens" in low):
            retry["max_tokens"] = retry.pop("max_completion_tokens")
            changed = True
        elif "max_tokens" in retry and "max_tokens" in low:
            retry["max_completion_tokens"] = retry.pop("max_tokens")
            changed = True
        if "temperature" in retry and "temperature" in low:
            retry.pop("temperature", None)
            changed = True
        if changed:
            resp = requests.post(endpoint, headers=_headers(provider, key), json=retry, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    choice = (data.get("choices") or [{}])[0] if isinstance(data, dict) else {}
    msg = choice.get("message") or {}
    content = msg.get("content")
    if isinstance(content, list):
        content = "".join(str(x.get("text") or "") for x in content if isinstance(x, dict))
    return {
        "content": str(content or "").strip(),
        "tool_calls": msg.get("tool_calls") or [],
        "model": model,
    }


def _request(provider: dict, key: str, model: str, messages: list[dict], tools: list[dict] | None,
             timeout: int, max_tokens: int, temperature: float) -> dict:
    kind = str(provider.get("type") or "openai-compatible").lower()
    if kind == "anthropic":
        return _anthropic_request(provider, key, model, messages, tools, timeout, max_tokens, temperature)
    return _openai_request(provider, key, model, messages, tools, timeout, max_tokens, temperature)


def chat(messages: list[dict], tools: list[dict] | None = None, *, timeout: int = 120,
         model: str | None = None, max_tokens: int = 768, temperature: float = 0.35,
         provider_id: str | None = None, local_only: bool = False) -> dict:
    """Route one non-streaming chat request through Ember's provider pool."""
    providers = _routing_order(provider_id, local_only=local_only)
    if not providers:
        raise RuntimeError("No enabled Ember LLM providers are configured.")

    errors: list[str] = []
    for provider in providers:
        pid = str(provider.get("id") or "").lower()
        if _cooling_provider(pid) and not provider_id:
            continue
        key_options = _ordered_keys(provider)
        if not key_options:
            errors.append(f"{pid}: no API key configured")
            continue

        provider_had_transport_failure = False
        for key_index, key in key_options:
            chosen = choose_model(provider, key, explicit=model, timeout=min(10, timeout))
            if not chosen:
                errors.append(f"{pid}: no chat model available")
                continue
            try:
                result = _request(provider, key, chosen, messages, tools, timeout, max_tokens, temperature)
                _mark_key_result(provider, key_index, failed=False)
                result["provider"] = pid
                return result
            except requests.exceptions.HTTPError as exc:
                status = getattr(exc.response, "status_code", None)
                _mark_key_result(provider, key_index, failed=True, status=status)
                if status in {401, 402, 403, 429}:
                    errors.append(f"{pid}: HTTP {status}")
                else:
                    body = ""
                    try:
                        body = (exc.response.text or "")[:220].replace("\n", " ")
                    except Exception:
                        pass
                    errors.append(f"{pid}: HTTP {status or '?'} {body}".strip())
                    if status and status >= 500:
                        provider_had_transport_failure = True
                continue
            except requests.exceptions.Timeout:
                errors.append(f"{pid}: timed out")
                provider_had_transport_failure = True
                continue
            except requests.exceptions.ConnectionError:
                errors.append(f"{pid}: connection failed")
                provider_had_transport_failure = True
                continue
            except Exception as exc:
                errors.append(f"{pid}: {type(exc).__name__}: {str(exc)[:180]}")
                provider_had_transport_failure = True
                continue
        if provider_had_transport_failure:
            _mark_provider_cool(pid)

    detail = " | ".join(errors[-6:]) or "no provider accepted the request"
    raise RuntimeError("Ember could not get an LLM response from the configured provider pool. " + detail)


def status() -> dict:
    """Safe status summary. Never exposes credential values."""
    cfg = load_config()
    secrets = load_secrets()
    rows = []
    for p in _providers():
        pid = p["id"]
        rows.append({
            "id": pid,
            "name": p.get("name", pid),
            "type": p.get("type", "openai-compatible"),
            "enabled": bool(p.get("enabled", True)),
            "local": bool(p.get("local", False)),
            "priority": int(p.get("priority", 0) or 0),
            "model": p.get("model") or "auto-discover",
            "key_count": len(secrets.get(pid, [])) + len(_env_keys(p)),
            "cooling_down": _cooling_provider(pid),
        })
    routing = cfg.get("routing", {}) if isinstance(cfg, dict) else {}
    return {
        "enabled": enabled(),
        "default_provider": routing.get("default_provider", "auto"),
        "fallback_order": routing.get("fallback_order", []),
        "providers": rows,
    }


def set_provider_enabled(provider_id: str, value: bool) -> bool:
    cfg = load_config()
    rows = cfg.get("providers", [])
    pid = str(provider_id or "").strip().lower()
    changed = False
    for p in rows if isinstance(rows, list) else []:
        if isinstance(p, dict) and str(p.get("id") or "").lower() == pid:
            p["enabled"] = bool(value)
            changed = True
    if not changed:
        raise ValueError(f"Unknown provider: {provider_id}")
    _write_json(PROVIDERS_PATH, cfg)
    return bool(value)


def set_default_provider(provider_id: str) -> str:
    cfg = load_config()
    pid = str(provider_id or "").strip().lower()
    valid = {p["id"] for p in _providers()}
    if pid not in valid:
        raise ValueError(f"Unknown provider: {provider_id}")
    routing = cfg.setdefault("routing", {})
    routing["default_provider"] = pid
    order = routing.get("fallback_order", [])
    order = [str(x).lower() for x in order] if isinstance(order, list) else []
    routing["fallback_order"] = [pid] + [x for x in order if x != pid]
    _write_json(PROVIDERS_PATH, cfg)
    return pid


def set_provider_model(provider_id: str, model: str) -> str:
    """Persist a preferred model for one provider without exposing credentials."""
    cfg = load_config()
    rows = cfg.get("providers", [])
    pid = str(provider_id or "").strip().lower()
    value = str(model or "").strip()
    changed = False
    for p in rows if isinstance(rows, list) else []:
        if isinstance(p, dict) and str(p.get("id") or "").lower() == pid:
            p["model"] = value
            changed = True
    if not changed:
        raise ValueError(f"Unknown provider: {provider_id}")
    _write_json(PROVIDERS_PATH, cfg)
    with _lock:
        _model_cache.pop(pid, None)
    return value
