# Ember Advanced Upgrade

This build keeps the original project's capabilities and licensing while making **Ember** the canonical assistant identity and hardening the LLM stack.

## LLM reliability upgrades

- Unified Ollama and OpenAI-compatible generation paths.
- Fixed `call_llm_text()` so helper agents no longer bypass the selected provider and accidentally call Ollama when LM Studio/Jan/LocalAI/etc. is selected.
- OpenAI-compatible URLs now accept either `http://host:port` or `http://host:port/v1` without creating `/v1/v1/...` requests.
- Optional `llm_api_key` and custom `llm_headers` support for authenticated compatible endpoints.
- Response limit increased from the old 150-token default to a configurable 768-token default.
- Configurable temperature, retry count, response length, and fallback model list.
- Retries transient timeouts, rate limits and common 5xx server failures.
- Tool-call arguments are normalised across providers.
- Gemini-style tool declarations are converted to standard Ollama/OpenAI function schemas, including JSON-Schema type normalization.
- Local models that print a JSON tool request instead of native tool-call metadata can now be recovered safely, but only when the requested tool exactly matches a tool Ember was actually given.
- OpenAI-compatible and Ollama streaming use the same normalized output shape.
- Clearer provider-specific failure messages.

## Conversation intelligence

- Local chat retains a larger configurable recent context instead of a hard-coded 12-message slice.
- History is bounded by both turns and characters to reduce context-overflow failures on small local models.
- Improved local system behavior: direct answers, uncertainty handling, no fake action-success claims.
- Local typed chat can now call Ember actions/plugins and synthesize the final answer from the real tool results; the previous build passed no tools at all in this path.
- Model Lab now exposes health diagnostics, response-limit tuning, temperature tuning and fallback-model configuration.

## Identity and compatibility

- Canonical assistant name is **Ember**.
- Replaced visible AMBER/Amber branding throughout the source and dashboard.
- Canonical feature-state file is now `config/ember_features.json`; the old `amber_features.json` is still read automatically so existing preferences survive an upgrade.
- Canonical dashboard routes are `/api/ember/status` and `/api/ember/features`; old AMBER routes remain as compatibility aliases.
- Canonical control plugin is `ember_control_center`.
- Canonical shutdown tool is `shutdown_ember`; the executor still accepts the old internal name for session compatibility.
- Canonical icon alias is `config/ember.ico`.

## Startup robustness

- Desktop automation modules no longer get rejected during discovery merely because PyAutoGUI cannot connect to a graphical display at import time. The capability now loads and reports that desktop automation is unavailable only if an actual desktop action is attempted in such a session.

## Example local LLM configuration

Add these fields to `config/api_keys.json` (the setup UI may create this file first):

```json
{
  "assistant_name": "Ember",
  "llm_provider": "ollama",
  "llm_url": "http://localhost:11434",
  "llm_model": "llama3.2",
  "llm_fallback_models": ["qwen2.5:7b", "mistral:7b"],
  "llm_max_tokens": 768,
  "llm_temperature": 0.35,
  "llm_retries": 2
}
```

For LM Studio/Jan/another OpenAI-compatible server, set `llm_provider` to `openai` and use that server's base URL. If the server requires authentication, add `llm_api_key`.

## Validation performed

- Full Python bytecode compilation succeeded.
- LLM unit tests passed for provider routing, authenticated OpenAI-compatible calls, `/v1` URL normalization, Gemini-to-local tool schema conversion, JSON tool recovery, and history compaction.
- Action/plugin discovery test: **16 actions valid, 27 plugins valid, 0 rejected actions, 0 invalid plugins** in the test environment.

## Multi-provider API pool

Ember can now keep multiple cloud providers and multiple keys per provider active at the same time. Provider metadata lives in `config/providers.json`; secret values live separately in `config/provider_secrets.json` as arrays so additional keys can be added without replacing an existing key.

The router tries the configured provider order, rotates between keys when a provider has several, cools keys after authentication/quota/rate-limit failures, and falls through to the next provider. Ollama remains the local fallback. LOCAL mode pins the request to Ollama and never routes it to cloud providers.

Imported from the supplied Infinity project: OpenAI, OpenRouter, Anthropic, Groq, and xKiro credentials only. Infinity contained Gemini integration code but no embedded Gemini/Google API key in its private `.env.local`; Ember therefore keeps its existing Gemini key path and an empty Gemini provider slot rather than fabricating a credential.

Provider status is deliberately redacted: Ember reports provider names, enabled state and key counts, never key values.


## Offline model BAT installers

`offline_model_installers/` contains one Windows `.bat` installer per supported Ollama model, a menu, a recommended small pack, and an all-model pack. Each installer can optionally set the downloaded model as Ember's default local model.

## Unified in-app settings update — 22 September 2026

- Added a unified **APP SETTINGS** panel inside the main Ember desktop interface.
- General settings now expose assistant identity, voice, theme and HUD style.
- AI settings now expose Auto/Online/Local routing, multi-provider routing, local runtime/endpoint, installed model selection and generation tuning.
- Provider settings now expose provider enable/disable, preferred provider and secure key replacement without displaying saved key values.
- Privacy/features settings now expose temporary memory, privacy logging, mini HUD, agent/screen features, performance profile and kill switch.
- Voice/input settings now expose wake word, push-to-talk, morning brief, thinking, proactive audio and media resolution.
- Offline model BAT installers are directly launchable from the AI settings page.
- Memory, Audio Devices, Plugin Manager and Plugin Settings are linked from the same settings surface.
- Existing configuration files remain compatible and remain the source of truth.
- Packaged provider API keys were removed from this distributable build; enter credentials locally through APP SETTINGS > PROVIDERS.


## Windows one-click Ember installer and Ollama installer repair

- Double-click `INSTALL_EMBER.bat` in the extracted Ember folder to install Python dependencies into `.venv`, with an optional desktop shortcut.
- Launch later with `RUN_EMBER.bat`.
- The corrected `offline_model_installers/00_INSTALL_OLLAMA.bat` uses winget first, then an optional official PowerShell fallback without the old `^` escaping bug.
- `offline_model_installers/_helpers/find_ollama.bat` detects Ollama even when PATH has not refreshed; individual model and model-checker BAT files use it.
- Read `INSTALLATION_GUIDE_WINDOWS.txt` for setup details.
