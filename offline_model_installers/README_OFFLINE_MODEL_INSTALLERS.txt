EMBER OFFLINE AI MODEL INSTALLERS
==================================

Start with:
  START_HERE_MODEL_INSTALLER_MENU.bat

Each AI model also has its own BAT installer so you can install only the models you want.
The model files are downloaded by Ollama the first time. Once installed, Ember can use them offline.

MODEL PACK
----------
1. llama3.2:3b          ~2.0 GB   General assistant / current Ember default family
2. qwen2.5:3b           ~1.9 GB   Lightweight general AI
3. qwen2.5:7b           ~4.7 GB   Stronger general AI; Ember fallback
4. qwen2.5-coder:3b     ~1.9 GB   Lightweight coding AI
5. qwen2.5-coder:7b     ~4.7 GB   Stronger coding AI
6. phi4-mini            ~2.5 GB   Reasoning, mathematics, multilingual, tools
7. gemma3:4b            ~3.3 GB   Text + image capable local model
8. mistral:7b           ~4.4 GB   General fallback; Ember fallback

Approximate total for all eight: 25.4 GB. Actual disk use can differ after updates, manifests, and cache.
The recommended small pack is about 11.6 GB.

HOW IT WORKS
------------
- The BAT checks whether Ollama exists.
- If Ollama is unavailable, run 00_INSTALL_OLLAMA.bat.
- The BAT runs `ollama pull MODEL`, which shows Ollama's normal progress indicator.
- After a successful download, it asks whether to set that model as Ember's default local model.
- Ember LOCAL mode stays on the local Ollama server at http://localhost:11434.

NOTES
-----
- Internet is required to download a model the first time. Afterward, local inference can work offline.
- Larger models require more RAM and can be slower on older CPUs.
- Do not install every model unless you actually want the extra disk usage.
- Ollama stores models in the configured OLLAMA_MODELS folder, or its normal user model directory if not changed.
