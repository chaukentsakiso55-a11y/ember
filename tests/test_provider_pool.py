import json
import unittest
from unittest.mock import patch

import requests

from core import provider_pool
from core import llm_client


class FakeResponse:
    def __init__(self, payload=None, status_code=200, text=""):
        self._payload = payload or {}
        self.status_code = status_code
        self.text = text

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.exceptions.HTTPError(response=self)


class ProviderPoolTests(unittest.TestCase):
    def setUp(self):
        provider_pool._key_cursor.clear()
        provider_pool._key_cooldown.clear()
        provider_pool._provider_cooldown.clear()
        provider_pool._model_cache.clear()

    def test_rotates_to_second_key_after_rate_limit(self):
        provider = {
            "id": "openai",
            "name": "OpenAI",
            "type": "openai-compatible",
            "base_url": "https://example.invalid/v1",
            "model": "test-model",
            "enabled": True,
            "priority": 100,
        }
        limited = FakeResponse(status_code=429, text="rate limited")
        ok = FakeResponse({"choices": [{"message": {"content": "second key worked"}}]})
        with patch.object(provider_pool, "_providers", return_value=[provider]), \
             patch.object(provider_pool, "load_config", return_value={"routing": {"fallback_order": ["openai"]}}), \
             patch.object(provider_pool, "load_secrets", return_value={"openai": ["key-A", "key-B"]}), \
             patch.object(provider_pool.requests, "post", side_effect=[limited, ok]) as post:
            result = provider_pool.chat([{"role": "user", "content": "hi"}])
        self.assertEqual(result["content"], "second key worked")
        self.assertEqual(result["provider"], "openai")
        self.assertEqual(post.call_args_list[0].kwargs["headers"]["Authorization"], "Bearer key-A")
        self.assertEqual(post.call_args_list[1].kwargs["headers"]["Authorization"], "Bearer key-B")

    def test_status_never_contains_secret_values(self):
        provider = {
            "id": "openrouter",
            "name": "OpenRouter",
            "type": "openai-compatible",
            "base_url": "https://example.invalid/v1",
            "enabled": True,
            "priority": 80,
        }
        with patch.object(provider_pool, "_providers", return_value=[provider]), \
             patch.object(provider_pool, "load_config", return_value={"routing": {"fallback_order": ["openrouter"]}}), \
             patch.object(provider_pool, "load_secrets", return_value={"openrouter": ["SUPER-SECRET-1", "SUPER-SECRET-2"]}), \
             patch.object(provider_pool, "enabled", return_value=True):
            text = json.dumps(provider_pool.status())
        self.assertNotIn("SUPER-SECRET-1", text)
        self.assertNotIn("SUPER-SECRET-2", text)
        self.assertIn('"key_count": 2', text)

    def test_llm_client_delegates_to_pool_when_enabled(self):
        result = {"content": "pooled", "tool_calls": [], "model": "m", "provider": "groq"}
        cfg = {"multi_provider_enabled": True, "llm_max_tokens": 768, "llm_temperature": 0.35}
        with patch.object(llm_client, "_load_config", return_value=cfg), \
             patch.object(provider_pool, "enabled", return_value=True), \
             patch.object(provider_pool, "chat", return_value=result) as chat:
            out = llm_client.call_llm([{"role": "user", "content": "hello"}])
        self.assertEqual(out["content"], "pooled")
        self.assertEqual(out["provider"], "groq")
        chat.assert_called_once()

    def test_local_pin_is_forwarded_to_pool(self):
        result = {"content": "local", "tool_calls": [], "model": "qwen", "provider": "ollama"}
        cfg = {"multi_provider_enabled": True}
        with patch.object(llm_client, "_load_config", return_value=cfg), \
             patch.object(provider_pool, "enabled", return_value=True), \
             patch.object(provider_pool, "chat", return_value=result) as chat:
            out = llm_client.call_llm(
                [{"role": "user", "content": "hello"}], provider_id="ollama", local_only=True
            )
        self.assertEqual(out["provider"], "ollama")
        self.assertEqual(chat.call_args.kwargs["provider_id"], "ollama")
        self.assertTrue(chat.call_args.kwargs["local_only"])


if __name__ == "__main__":
    unittest.main()
