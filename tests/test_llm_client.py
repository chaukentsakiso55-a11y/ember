import json
import unittest
from unittest.mock import patch

from core import llm_client
from core.local_mode import _compact_history


class FakeResponse:
    def __init__(self, payload=None, status_code=200, text=""):
        self._payload = payload or {}
        self.status_code = status_code
        self.text = text

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            import requests
            response = self
            raise requests.exceptions.HTTPError(response=response)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


class LLMClientTests(unittest.TestCase):
    def test_openai_root_does_not_duplicate_v1(self):
        self.assertEqual(llm_client._openai_root("http://localhost:1234"), "http://localhost:1234/v1")
        self.assertEqual(llm_client._openai_root("http://localhost:1234/v1/"), "http://localhost:1234/v1")

    def test_provider_aware_text_call_uses_openai_endpoint_and_auth(self):
        cfg = {
            "llm_provider": "openai",
            "llm_url": "http://localhost:1234/v1",
            "llm_model": "test-model",
            "llm_api_key": "secret",
            "llm_retries": 0,
        }
        response = FakeResponse({"choices": [{"message": {"content": "hello"}}]})
        with patch.object(llm_client, "_load_config", return_value=cfg), \
             patch.object(llm_client.requests, "post", return_value=response) as post:
            text = llm_client.call_llm_text("hi")
        self.assertEqual(text, "hello")
        args, kwargs = post.call_args
        self.assertEqual(args[0], "http://localhost:1234/v1/chat/completions")
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer secret")

    def test_recovers_json_tool_call_only_for_known_tool(self):
        tools = [{"type": "function", "function": {"name": "open_app", "parameters": {"type": "object"}}}]
        content = json.dumps({"name": "open_app", "arguments": {"app": "calculator"}})
        calls = llm_client._content_tool_call(content, tools)
        self.assertEqual(calls[0]["function"]["name"], "open_app")
        self.assertEqual(calls[0]["function"]["arguments"]["app"], "calculator")
        self.assertEqual(llm_client._content_tool_call('{"name":"delete_everything"}', tools), [])


    def test_gemini_style_tools_are_converted_for_local_providers(self):
        tools = [{
            "name": "set_volume",
            "description": "Set volume",
            "parameters": {
                "type": "OBJECT",
                "properties": {"level": {"type": "INTEGER"}},
                "required": ["level"],
            },
        }]
        normalized = llm_client._provider_tools(tools)
        self.assertEqual(normalized[0]["type"], "function")
        self.assertEqual(normalized[0]["function"]["name"], "set_volume")
        self.assertEqual(normalized[0]["function"]["parameters"]["type"], "object")
        self.assertEqual(normalized[0]["function"]["parameters"]["properties"]["level"]["type"], "integer")

    def test_history_compaction_keeps_recent_context(self):
        history = [{"role": "user" if i % 2 == 0 else "assistant", "content": f"turn {i}"} for i in range(30)]
        with patch("core.local_mode.get", side_effect=lambda key, default=None: {"llm_history_turns": 8, "llm_history_chars": 24000}.get(key, default)):
            compact = _compact_history(history)
        self.assertEqual(len(compact), 8)
        self.assertEqual(compact[0]["content"], "turn 22")
        self.assertEqual(compact[-1]["content"], "turn 29")


if __name__ == "__main__":
    unittest.main()
