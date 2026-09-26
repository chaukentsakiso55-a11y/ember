# Ember Multi-Provider AI

Ember can keep several AI providers configured simultaneously and route text/model work through them as one pool.

## Current provider pool

- xKiro
- OpenAI
- Anthropic Claude
- Groq
- OpenRouter
- Google Gemini (ready for a Gemini/Google key)
- Ollama Local (local fallback)

Provider metadata is stored in `config/providers.json`. Credentials are stored separately in `config/provider_secrets.json` and are represented as arrays, so a provider can have more than one key.

Example shape only (do not replace your real file with these placeholders):

```json
{
  "openai": ["KEY_1", "KEY_2"],
  "openrouter": ["KEY_1"]
}
```

When a provider has multiple keys, Ember rotates them and temporarily cools a key after authentication, credit, quota, or rate-limit errors. If that provider cannot answer, Ember moves to the next enabled provider. Model lists are discovered from providers when no model is pinned.

`AUTO` and `ONLINE` typed chat may use the provider pool. `LOCAL` pins requests to Ollama and does not send those prompts to a cloud provider. Gemini Live voice remains a separate realtime connection and still requires a Gemini key.

The Provider Manager plugin can report provider state, key counts, priorities, and enable/disable/default-provider changes. It never returns secret values.

## Security

This build contains API credentials imported from the supplied Infinity project. Do not publish or share this ZIP publicly. Anyone who obtains an embedded API key may be able to use the associated provider account until the key is revoked.
