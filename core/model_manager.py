"""Local model discovery, configuration, diagnostics and benchmarking for Ember."""
from __future__ import annotations

import json
import time
from pathlib import Path

import requests

from core.llm_client import (
    CONFIG_PATH,
    call_llm,
    ensure_ollama_running,
    get_llm_provider,
    get_llm_settings,
)


def _load_cfg() -> dict:
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save_cfg(data: dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(data, indent=4), encoding="utf-8")


def configure(
    provider: str | None = None,
    url: str | None = None,
    model: str | None = None,
    *,
    api_key: str | None = None,
    max_tokens: int | None = None,
    temperature: float | None = None,
    fallback_models: list[str] | str | None = None,
) -> dict:
    data = _load_cfg()
    p = str(provider or data.get("llm_provider") or "ollama").strip().lower()
    if p in {"lmstudio", "lm-studio", "localai", "jan", "llamacpp", "llama.cpp", "vllm", "openrouter", "compatible"}:
        p = "openai"
    if p not in {"ollama", "openai"}:
        raise ValueError("provider must be ollama or openai-compatible")

    data["llm_provider"] = p
    if url is not None and str(url).strip():
        data["llm_url"] = str(url).strip().rstrip("/")
    elif "llm_url" not in data:
        data["llm_url"] = "http://localhost:11434" if p == "ollama" else "http://localhost:1234"
    if model is not None and str(model).strip():
        data["llm_model"] = str(model).strip()
    if api_key is not None:
        data["llm_api_key"] = str(api_key).strip()
    if max_tokens is not None:
        data["llm_max_tokens"] = max(32, min(8192, int(max_tokens)))
    if temperature is not None:
        data["llm_temperature"] = max(0.0, min(2.0, float(temperature)))
    if fallback_models is not None:
        if isinstance(fallback_models, str):
            fallback_models = [x.strip() for x in fallback_models.split(",") if x.strip()]
        data["llm_fallback_models"] = [str(x).strip() for x in fallback_models if str(x).strip()]

    _save_cfg(data)
    return status()


def list_models() -> list[str]:
    url, _ = get_llm_settings()
    provider = get_llm_provider()
    try:
        if provider == "ollama":
            resp = requests.get(url + "/api/tags", timeout=4)
            resp.raise_for_status()
            return [
                m.get("name", "") for m in resp.json().get("models", []) if m.get("name")
            ]
        base = url.rstrip("/") if url.rstrip("/").endswith("/v1") else url.rstrip("/") + "/v1"
        headers = {}
        key = str(_load_cfg().get("llm_api_key") or "").strip()
        if key:
            headers["Authorization"] = f"Bearer {key}"
        resp = requests.get(base + "/models", headers=headers, timeout=4)
        resp.raise_for_status()
        return [m.get("id", "") for m in resp.json().get("data", []) if m.get("id")]
    except Exception:
        return []


def reachable() -> bool:
    try:
        return bool(ensure_ollama_running(timeout=3))
    except Exception:
        return False


def diagnostics() -> dict:
    """Return actionable model health information for UI/plugin surfaces."""
    cfg = _load_cfg()
    try:
        from core import provider_pool
        if provider_pool.enabled():
            pool = provider_pool.status()
            usable = [
                p for p in pool.get("providers", [])
                if p.get("enabled") and (p.get("local") or int(p.get("key_count", 0) or 0) > 0)
            ]
            issues = [] if usable else ["No enabled multi-provider route has a key or local runtime configured"]
            return {
                "ok": bool(usable),
                "provider": "multi",
                "url": "provider-pool",
                "model": "automatic per provider",
                "reachable": bool(usable),
                "models": [],
                "provider_pool": pool,
                "generation": {
                    "max_tokens": cfg.get("llm_max_tokens", 768),
                    "temperature": cfg.get("llm_temperature", 0.35),
                    "fallback_models": cfg.get("llm_fallback_models", []),
                },
                "issues": issues,
                "recommendations": [] if usable else ["Configure at least one provider key or start Ollama"],
            }
    except Exception:
        pass
    url, model = get_llm_settings()
    provider = get_llm_provider()
    is_reachable = reachable()
    models = list_models() if is_reachable else []
    exact = model in models
    base_match = any(m.split(":")[0] == model.split(":")[0] for m in models)
    issues: list[str] = []
    recommendations: list[str] = []

    if not is_reachable:
        issues.append("LLM server is not reachable")
        if provider == "ollama":
            recommendations.append("Start Ollama or install it, then run: ollama serve")
        else:
            recommendations.append("Start the configured OpenAI-compatible server and verify its base URL")
    elif models and not (exact or base_match):
        issues.append(f"Configured model '{model}' is not available from the server")
        if provider == "ollama":
            recommendations.append(f"Pull it with: ollama pull {model}")
        recommendations.append("Or select one of the detected models in Ember Model Lab")

    try:
        max_tokens = int(cfg.get("llm_max_tokens", 768) or 768)
    except (TypeError, ValueError):
        max_tokens = 768
    if max_tokens < 256:
        issues.append("Response token limit is very low and may truncate answers")
        recommendations.append("Set llm_max_tokens to at least 512 for normal typed chat")

    return {
        "ok": not issues,
        "provider": provider,
        "url": url,
        "model": model,
        "reachable": is_reachable,
        "models": models,
        "generation": {
            "max_tokens": max_tokens,
            "temperature": cfg.get("llm_temperature", 0.35),
            "fallback_models": cfg.get("llm_fallback_models", []),
        },
        "issues": issues,
        "recommendations": recommendations,
    }


def status() -> dict:
    return diagnostics()


def benchmark(prompt: str = "Reply with exactly: EMBER READY") -> dict:
    start = time.perf_counter()
    try:
        result = call_llm(
            [
                {"role": "system", "content": "You are a benchmark responder. Follow the exact instruction."},
                {"role": "user", "content": prompt},
            ],
            timeout=90,
            max_tokens=64,
        )
        text = str(result.get("content") or "")
        return {
            "ok": True,
            "seconds": round(time.perf_counter() - start, 3),
            "response": text[:300],
            "provider": get_llm_provider(),
            "model": result.get("model") or get_llm_settings()[1],
        }
    except Exception as e:
        return {
            "ok": False,
            "seconds": round(time.perf_counter() - start, 3),
            "error": str(e),
            "provider": get_llm_provider(),
            "model": get_llm_settings()[1],
        }
