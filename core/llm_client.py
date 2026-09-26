"""Unified local / OpenAI-compatible LLM client for Ember.

Ember can use:
  * Ollama (default)
  * Any OpenAI-compatible server or API (LM Studio, Jan, llama.cpp, LocalAI,
    vLLM, OpenRouter-style gateways, etc.)

The implementation intentionally keeps the public functions used by the rest of
Ember stable while making the backend more resilient: provider-aware text calls,
optional auth, configurable generation limits, transient retries, model
fallbacks, robust tool-call normalisation, and streaming support.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Callable, Generator, Iterable

import requests

_SENT_END = re.compile(r"(?<=[.!?])\s+|(?<=\n)\s*\n")
_JSON_FENCE = re.compile(r"^\s*```(?:json)?\s*(.*?)\s*```\s*$", re.I | re.S)


def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


BASE_DIR = get_base_dir()
CONFIG_PATH = BASE_DIR / "config" / "api_keys.json"

_DEFAULTS = {
    "llm_url": "http://localhost:11434",
    "llm_model": "llama3.2",
    "llm_provider": "ollama",
    # 150 tokens was too small for useful typed answers and often caused
    # seemingly random truncation. 768 is still modest for local hardware.
    "llm_max_tokens": 768,
    "llm_temperature": 0.35,
    "llm_retries": 2,
}

_TRANSIENT_STATUS = {408, 409, 425, 429, 500, 502, 503, 504}


def _load_config() -> dict:
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _cfg_int(name: str, default: int, lo: int, hi: int) -> int:
    try:
        return max(lo, min(hi, int(_load_config().get(name, default))))
    except (TypeError, ValueError):
        return default


def _cfg_float(name: str, default: float, lo: float, hi: float) -> float:
    try:
        return max(lo, min(hi, float(_load_config().get(name, default))))
    except (TypeError, ValueError):
        return default


def _openai_root(url: str) -> str:
    """Return a base that contains exactly one /v1 for OpenAI-style routes."""
    clean = (url or "").strip().rstrip("/")
    return clean if clean.endswith("/v1") else clean + "/v1"


def _headers() -> dict[str, str]:
    cfg = _load_config()
    headers = {"Content-Type": "application/json"}
    # Local compatible servers usually need no key; hosted compatible APIs can
    # use llm_api_key without forcing Ember to depend on a specific vendor SDK.
    key = str(cfg.get("llm_api_key") or "").strip()
    if key:
        headers["Authorization"] = f"Bearer {key}"
    extra = cfg.get("llm_headers")
    if isinstance(extra, dict):
        for k, v in extra.items():
            if isinstance(k, str) and isinstance(v, (str, int, float)):
                headers[k] = str(v)
    return headers


def get_llm_provider() -> str:
    """Return ``ollama`` or ``openai`` for the configured backend."""
    raw = str(_load_config().get("llm_provider", "ollama")).strip().lower()
    aliases = {
        "openai", "lmstudio", "lm-studio", "localai", "jan", "llamacpp",
        "llama.cpp", "vllm", "openrouter", "compatible",
    }
    return "openai" if raw in aliases else "ollama"


def get_llm_settings() -> tuple[str, str]:
    """Return ``(base_url, model_name)``."""
    cfg = _load_config()
    url = str(cfg.get("llm_url", _DEFAULTS["llm_url"])).strip().rstrip("/")
    model = str(cfg.get("llm_model", _DEFAULTS["llm_model"])).strip()
    return url, model


def _model_candidates(explicit: str | None = None) -> list[str]:
    cfg = _load_config()
    primary = explicit or str(cfg.get("llm_model") or _DEFAULTS["llm_model"])
    raw = cfg.get("llm_fallback_models", [])
    if isinstance(raw, str):
        raw = [x.strip() for x in raw.split(",") if x.strip()]
    if not isinstance(raw, list):
        raw = []
    out: list[str] = []
    for m in [primary, *raw]:
        m = str(m or "").strip()
        if m and m not in out:
            out.append(m)
    return out or [_DEFAULTS["llm_model"]]


def _generation(max_tokens: int | None = None) -> tuple[int, float]:
    tokens = max_tokens if max_tokens is not None else _cfg_int(
        "llm_max_tokens", _DEFAULTS["llm_max_tokens"], 32, 8192
    )
    temperature = _cfg_float(
        "llm_temperature", _DEFAULTS["llm_temperature"], 0.0, 2.0
    )
    return int(tokens), temperature


def _normalise_schema(value):
    """Convert Gemini-style uppercase schema types to standard JSON Schema."""
    if isinstance(value, list):
        return [_normalise_schema(x) for x in value]
    if not isinstance(value, dict):
        return value
    out = {}
    type_map = {
        "OBJECT": "object", "STRING": "string", "BOOLEAN": "boolean",
        "INTEGER": "integer", "NUMBER": "number", "ARRAY": "array",
    }
    for key, item in value.items():
        if key == "type" and isinstance(item, str):
            out[key] = type_map.get(item.upper(), item.lower())
        else:
            out[key] = _normalise_schema(item)
    return out


def _provider_tools(tools: list | None) -> list[dict]:
    """Return OpenAI/Ollama function-tool objects from Ember/Gemini declarations."""
    out: list[dict] = []
    for tool in tools or []:
        if not isinstance(tool, dict):
            continue
        if tool.get("type") == "function" and isinstance(tool.get("function"), dict):
            fn = dict(tool["function"])
        elif tool.get("name"):
            fn = {
                "name": str(tool.get("name")),
                "description": str(tool.get("description") or ""),
                "parameters": tool.get("parameters") or {"type": "object", "properties": {}},
            }
        else:
            continue
        fn["parameters"] = _normalise_schema(fn.get("parameters") or {"type": "object", "properties": {}})
        out.append({"type": "function", "function": fn})
    return out


def _known_tool_names(tools: list | None) -> set[str]:
    names: set[str] = set()
    for tool in tools or []:
        if not isinstance(tool, dict):
            continue
        fn = tool.get("function")
        if isinstance(fn, dict) and fn.get("name"):
            names.add(str(fn["name"]))
        elif tool.get("name"):
            names.add(str(tool["name"]))
    return names


def _parse_arguments(value):
    if isinstance(value, dict):
        return value
    if value is None or value == "":
        return {}
    if isinstance(value, str):
        text = value.strip()
        try:
            parsed = json.loads(text)
            return parsed if isinstance(parsed, dict) else {"value": parsed}
        except Exception:
            # Preserve malformed arguments rather than crashing the entire turn;
            # the executor can surface a precise parameter error to the user.
            return value
    return value


def _normalise_tool_calls(raw_calls) -> list[dict]:
    out: list[dict] = []
    if not isinstance(raw_calls, list):
        return out
    for i, call in enumerate(raw_calls):
        if not isinstance(call, dict):
            continue
        fn = call.get("function") if isinstance(call.get("function"), dict) else call
        name = str(fn.get("name") or call.get("name") or "").strip()
        if not name:
            continue
        args = fn.get("arguments", fn.get("parameters", call.get("arguments", {})))
        out.append({
            "id": str(call.get("id") or f"tool_{i}"),
            "function": {"name": name, "arguments": _parse_arguments(args)},
        })
    return out


def _content_tool_call(content: str, tools: list | None) -> list[dict]:
    """Recover tool calls from models that print JSON instead of tool metadata.

    We only accept a JSON object whose tool name exactly matches a supplied tool,
    so ordinary JSON answers are never mistaken for computer actions.
    """
    allowed = _known_tool_names(tools)
    if not content or not allowed:
        return []
    raw = content.strip()
    m = _JSON_FENCE.match(raw)
    if m:
        raw = m.group(1).strip()
    if not (raw.startswith("{") and raw.endswith("}")):
        return []
    try:
        obj = json.loads(raw)
    except Exception:
        return []
    if not isinstance(obj, dict):
        return []
    fn = obj.get("function") if isinstance(obj.get("function"), dict) else obj
    name = str(fn.get("name") or obj.get("tool") or "").strip()
    if name not in allowed:
        return []
    args = fn.get("arguments", obj.get("arguments", obj.get("parameters", {})))
    return [{
        "id": str(obj.get("id") or "content_tool_0"),
        "function": {"name": name, "arguments": _parse_arguments(args)},
    }]


def _post_json(
    endpoint: str,
    payload: dict,
    timeout: int,
    *,
    headers: dict | None = None,
    stream: bool = False,
):
    """POST with short retries for transient transport/server failures."""
    attempts = _cfg_int("llm_retries", _DEFAULTS["llm_retries"], 0, 4) + 1
    last_exc: Exception | None = None
    for attempt in range(attempts):
        try:
            resp = requests.post(
                endpoint, json=payload, timeout=timeout, headers=headers, stream=stream
            )
            if resp.status_code in _TRANSIENT_STATUS and attempt + 1 < attempts:
                try:
                    resp.close()
                except Exception:
                    pass
                time.sleep(min(1.5, 0.25 * (2 ** attempt)))
                continue
            resp.raise_for_status()
            return resp
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            last_exc = e
            if attempt + 1 >= attempts:
                raise
            time.sleep(min(1.5, 0.25 * (2 ** attempt)))
        except requests.exceptions.HTTPError as e:
            last_exc = e
            status = getattr(e.response, "status_code", 0)
            if status not in _TRANSIENT_STATUS or attempt + 1 >= attempts:
                raise
            time.sleep(min(1.5, 0.25 * (2 ** attempt)))
    if last_exc:
        raise last_exc
    raise RuntimeError("LLM request failed before a response was received")


def ensure_ollama_running(timeout: int = 15) -> bool:
    """Check configured LLM server availability.

    The historic function name is kept for compatibility. For an OpenAI-
    compatible backend it only checks ``/v1/models`` and never tries to launch
    anything. For Ollama it can auto-start ``ollama serve``.
    """
    url, _ = get_llm_settings()
    provider = get_llm_provider()

    if provider == "openai":
        try:
            return requests.get(
                f"{_openai_root(url)}/models", headers=_headers(), timeout=5
            ).status_code == 200
        except Exception:
            return False

    health = f"{url}/api/tags"

    def _is_up() -> bool:
        try:
            return requests.get(health, timeout=3).status_code == 200
        except Exception:
            return False

    if _is_up():
        return True

    try:
        kwargs: dict = {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
        if sys.platform == "win32":
            kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
        subprocess.Popen(["ollama", "serve"], **kwargs)
    except (FileNotFoundError, OSError):
        return False

    deadline = time.time() + max(1, timeout)
    while time.time() < deadline:
        time.sleep(0.5)
        if _is_up():
            return True
    return False


def warmup_model(system_prompt: str | None = None) -> bool:
    """Preload the configured model and, for Ollama, keep it resident."""
    url, model = get_llm_settings()
    provider = get_llm_provider()
    messages: list[dict] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": "Reply with: ready"})

    try:
        if provider == "openai":
            payload = {
                "model": model, "messages": messages, "stream": False,
                "max_tokens": 2, "temperature": 0,
            }
            _post_json(
                f"{_openai_root(url)}/chat/completions", payload, 180,
                headers=_headers(),
            )
        else:
            payload = {
                "model": model, "messages": messages, "stream": False,
                "keep_alive": -1,
                "options": {"num_predict": 2, "num_gpu": 99, "temperature": 0},
            }
            _post_json(f"{url}/api/chat", payload, 180)
        return True
    except Exception as e:
        print(f"[LLM] Warmup failed (non-fatal): {e}")
        return False


def check_model_available(log: Callable | None = None) -> bool:
    if get_llm_provider() != "ollama":
        return True
    url, model = get_llm_settings()
    try:
        resp = requests.get(f"{url}/api/tags", timeout=5)
        resp.raise_for_status()
        pulled = [m.get("name", "") for m in resp.json().get("models", [])]
        model_base = model.split(":")[0]
        found = any(
            m == model or m == model_base or m.startswith(model_base + ":")
            for m in pulled
        )
        if not found and log:
            log(f"WRN: '{model}' not found — run: ollama pull {model}")
        return found
    except Exception:
        return True


def _request_once(
    messages: list,
    tools: list | None,
    timeout: int,
    model: str,
    max_tokens: int | None = None,
) -> dict:
    url, _ = get_llm_settings()
    provider = get_llm_provider()
    tokens, temperature = _generation(max_tokens)

    if provider == "openai":
        payload: dict = {
            "model": model,
            "messages": messages,
            "stream": False,
            "max_tokens": tokens,
            "temperature": temperature,
        }
        if tools:
            payload["tools"] = _provider_tools(tools)
            payload["tool_choice"] = "auto"
        resp = _post_json(
            f"{_openai_root(url)}/chat/completions", payload, timeout,
            headers=_headers(),
        )
        choice = (resp.json().get("choices") or [{}])[0]
        msg = choice.get("message") or {}
        content = str(msg.get("content") or "").strip()
        calls = _normalise_tool_calls(msg.get("tool_calls") or [])
    else:
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "keep_alive": -1,
            "options": {
                "num_predict": tokens,
                "num_gpu": 99,
                "temperature": temperature,
            },
        }
        if tools:
            payload["tools"] = _provider_tools(tools)
        resp = _post_json(f"{url}/api/chat", payload, timeout)
        msg = resp.json().get("message") or {}
        content = str(msg.get("content") or "").strip()
        calls = _normalise_tool_calls(msg.get("tool_calls") or [])

    if tools and not calls:
        recovered = _content_tool_call(content, tools)
        if recovered:
            calls = recovered
            content = ""
    return {"content": content, "tool_calls": calls, "model": model}


def call_llm(
    messages: list,
    tools: list | None = None,
    timeout: int = 120,
    model: str | None = None,
    max_tokens: int | None = None,
    provider_id: str | None = None,
    local_only: bool = False,
) -> dict:
    """Non-streaming chat generation with optional tool calling.

    Configured fallback models are tried only after the primary model fails.
    This is especially useful when a local model was renamed, unloaded, or is
    temporarily unavailable while another pulled model is still ready.
    """
    if not isinstance(messages, list) or not messages:
        raise ValueError("messages must be a non-empty list")

    # The provider pool is opt-in through api_keys.json so old Ember installs,
    # tests, and manually configured LM Studio/Ollama setups remain compatible.
    # A provider_id can pin a request (used by LOCAL mode); otherwise Ember
    # rotates keys and falls through the configured cloud/local provider order.
    try:
        from core import provider_pool
        pool_enabled = bool(_load_config().get("multi_provider_enabled", False)) and provider_pool.enabled()
    except Exception:
        provider_pool = None
        pool_enabled = False
    if pool_enabled and provider_pool is not None:
        tokens, temperature = _generation(max_tokens)
        result = provider_pool.chat(
            messages,
            tools=_provider_tools(tools),
            timeout=timeout,
            model=model,
            max_tokens=tokens,
            temperature=temperature,
            provider_id=provider_id,
            local_only=local_only,
        )
        content = str(result.get("content") or "").strip()
        calls = _normalise_tool_calls(result.get("tool_calls") or [])
        if tools and not calls:
            recovered = _content_tool_call(content, tools)
            if recovered:
                calls = recovered
                content = ""
        return {
            "content": content,
            "tool_calls": calls,
            "model": result.get("model") or model or "",
            "provider": result.get("provider") or provider_id or "auto",
        }

    errors: list[str] = []
    for candidate in _model_candidates(model):
        try:
            return _request_once(messages, tools, timeout, candidate, max_tokens)
        except requests.exceptions.ConnectionError as e:
            # Ollama is the only backend Ember can safely launch itself.
            if get_llm_provider() == "ollama" and ensure_ollama_running(timeout=8):
                try:
                    return _request_once(messages, tools, timeout, candidate, max_tokens)
                except Exception as retry_e:
                    errors.append(f"{candidate}: {retry_e}")
            else:
                errors.append(f"{candidate}: connection failed ({e})")
        except requests.exceptions.Timeout:
            errors.append(f"{candidate}: request timed out after {timeout}s")
        except requests.exceptions.HTTPError as e:
            body = ""
            try:
                body = (e.response.text or "")[:240]
            except Exception:
                pass
            errors.append(f"{candidate}: HTTP {getattr(e.response, 'status_code', '?')} {body}".strip())
        except Exception as e:
            errors.append(f"{candidate}: {type(e).__name__}: {e}")

    provider = get_llm_provider()
    url, _ = get_llm_settings()
    detail = " | ".join(errors[-3:]) or "unknown error"
    if provider == "openai":
        raise RuntimeError(
            f"Cannot get a response from the OpenAI-compatible LLM at {url}. {detail}"
        )
    raise RuntimeError(f"Cannot get a response from Ollama at {url}. {detail}")


def call_llm_text(
    prompt: str,
    system: str | None = None,
    model: str | None = None,
    timeout: int = 120,
    max_tokens: int = 1200,
    provider_id: str | None = None,
) -> str:
    """Provider-aware text generation used by Ember's helper agents."""
    messages: list[dict] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    return call_llm(
        messages, timeout=timeout, model=model, max_tokens=max_tokens, provider_id=provider_id
    ).get("content", "").strip()


def _stream_openai(
    messages: list,
    tools: list | None,
    timeout: int,
) -> Generator[dict, None, None]:
    url, model = get_llm_settings()
    endpoint = f"{_openai_root(url)}/chat/completions"
    tokens, temperature = _generation()
    payload: dict = {
        "model": model,
        "messages": messages,
        "stream": True,
        "max_tokens": tokens,
        "temperature": temperature,
    }
    if tools:
        payload["tools"] = _provider_tools(tools)
        payload["tool_choice"] = "auto"

    try:
        with _post_json(
            endpoint, payload, timeout, headers=_headers(), stream=True
        ) as resp:
            full_content = ""
            buf = ""
            tc_fragments: dict[int, dict] = {}

            for raw in resp.iter_lines():
                if not raw:
                    continue
                line = raw.decode("utf-8", errors="replace") if isinstance(raw, bytes) else raw
                if not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if data == "[DONE]":
                    break
                try:
                    chunk = json.loads(data)
                except json.JSONDecodeError:
                    continue

                choice = (chunk.get("choices") or [{}])[0]
                delta = choice.get("delta") or {}
                text = delta.get("content") or ""
                full_content += text
                buf += text

                while True:
                    m = _SENT_END.search(buf)
                    if not m:
                        break
                    sentence = buf[:m.start()].strip()
                    buf = buf[m.end():]
                    if sentence:
                        yield {"type": "sentence", "text": sentence}

                for tc in delta.get("tool_calls") or []:
                    idx = int(tc.get("index", 0))
                    frag = tc_fragments.setdefault(
                        idx, {"id": "", "function": {"name": "", "arguments": ""}}
                    )
                    frag["id"] = frag["id"] or tc.get("id", "")
                    fn = tc.get("function") or {}
                    frag["function"]["name"] += fn.get("name") or ""
                    frag["function"]["arguments"] += fn.get("arguments") or ""

                if choice.get("finish_reason") in ("stop", "tool_calls", "length"):
                    break

            if buf.strip():
                yield {"type": "sentence", "text": buf.strip()}

            calls = _normalise_tool_calls([tc_fragments[i] for i in sorted(tc_fragments)])
            if tools and not calls:
                recovered = _content_tool_call(full_content, tools)
                if recovered:
                    calls = recovered
                    full_content = ""
            yield {"type": "done", "content": full_content.strip(), "tool_calls": calls}

    except requests.exceptions.ConnectionError:
        raise RuntimeError(f"Cannot reach OpenAI-compatible LLM at {url}.")
    except requests.exceptions.Timeout:
        raise RuntimeError(f"OpenAI-compatible stream timed out after {timeout}s.")
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"OpenAI-compatible HTTP error: {getattr(e.response, 'status_code', '?')}")


def call_llm_stream(
    messages: list,
    tools: list | None = None,
    timeout: int = 120,
) -> Generator[dict, None, None]:
    """Streaming generation. Sentence events allow Ember's TTS to start early."""
    try:
        from core import provider_pool as _pool
        _pool_enabled = bool(_load_config().get("multi_provider_enabled", False)) and _pool.enabled()
    except Exception:
        _pool_enabled = False
    if _pool_enabled:
        result = call_llm(messages, tools=tools, timeout=timeout)
        content = str(result.get("content") or "")
        buf = content
        while True:
            m = _SENT_END.search(buf)
            if not m:
                break
            sentence = buf[:m.start()].strip()
            buf = buf[m.end():]
            if sentence:
                yield {"type": "sentence", "text": sentence}
        if buf.strip():
            yield {"type": "sentence", "text": buf.strip()}
        yield {
            "type": "done",
            "content": content.strip(),
            "tool_calls": result.get("tool_calls") or [],
            "provider": result.get("provider"),
            "model": result.get("model"),
        }
        return
    if get_llm_provider() == "openai":
        yield from _stream_openai(messages, tools, timeout)
        return

    url, model = get_llm_settings()
    endpoint = f"{url}/api/chat"
    tokens, temperature = _generation()
    payload: dict = {
        "model": model,
        "messages": messages,
        "stream": True,
        "keep_alive": -1,
        "options": {
            "num_predict": tokens,
            "num_gpu": 99,
            "temperature": temperature,
        },
    }
    if tools:
        payload["tools"] = _provider_tools(tools)

    def _do_stream() -> Generator[dict, None, None]:
        with _post_json(endpoint, payload, timeout, stream=True) as resp:
            full_content = ""
            calls: list[dict] = []
            buf = ""
            for raw in resp.iter_lines():
                if not raw:
                    continue
                try:
                    chunk = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                msg = chunk.get("message") or {}
                delta = msg.get("content") or ""
                full_content += delta
                buf += delta

                while True:
                    m = _SENT_END.search(buf)
                    if not m:
                        break
                    sentence = buf[:m.start()].strip()
                    buf = buf[m.end():]
                    if sentence:
                        yield {"type": "sentence", "text": sentence}

                if msg.get("tool_calls"):
                    calls.extend(_normalise_tool_calls(msg.get("tool_calls")))

                if chunk.get("done"):
                    if buf.strip():
                        yield {"type": "sentence", "text": buf.strip()}
                    if tools and not calls:
                        recovered = _content_tool_call(full_content, tools)
                        if recovered:
                            calls = recovered
                            full_content = ""
                    yield {
                        "type": "done",
                        "content": full_content.strip(),
                        "tool_calls": calls,
                    }
                    return

    try:
        yield from _do_stream()
    except requests.exceptions.ConnectionError as e:
        if ensure_ollama_running(timeout=8):
            yield from _do_stream()
            return
        raise RuntimeError(f"Cannot connect to Ollama at {url}: {e}")
    except requests.exceptions.Timeout:
        raise RuntimeError(f"Ollama stream timed out after {timeout}s.")
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"Ollama HTTP error: {getattr(e.response, 'status_code', '?')}")
