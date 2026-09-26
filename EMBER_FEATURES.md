# EMBER — Added Feature Pack

This build extends the renamed MARK LIV base while keeping the original CC BY-NC 4.0 license and attribution in `LICENSE` and `ATTRIBUTION.md`.

## Implemented and wired

- **Local / Auto / Online model routing** for typed chat, with Ollama and OpenAI-compatible local servers (LM Studio, Jan, LocalAI, llama.cpp server).
- **On-demand offline voice turn**: cached Whisper → local LLM → cached Kokoro (`/localvoice`, optional heavy dependencies).
- **Local model manager + benchmark** and configurable provider/URL/model.
- **Plugin/skills manager** with local install, enable/disable and permission metadata controls.
- **Screen understanding + visual computer agent** retained from the original Live vision/computer-control stack.
- **Workspace / Project Mode** with active project path, workspace memory, notes, tasks and study progress.
- **Searchable workspace memory UI output** and **Temporary Memory Mode** (also skips end-of-session summaries).
- **Coding workspace + Git**: tree, search, status, diff, branches, logs, standard project tests and explicit commits.
- **Offline knowledge library**: text/code, PDF, DOCX, PPTX and XLSX indexing/search.
- **Study + Teacher tools** plus persistent workspace weak-topic/progress tracking.
- **Voice profiles**, Gemini voice selection and real **Whisper Mode** playback attenuation.
- **Hey Ember wake-model support**: drop `config/hey_amber.onnx` or `config/hey_amber.tflite` into the project. If no custom model is present, the bundled OpenWakeWord path uses its legacy Hey Jarvis fallback.
- **Optional local speaker identification** using user-supplied WAV enrolment (`resemblyzer` optional).
- **Natural voice interruption / barge-in** using EMBER's echo guard.
- **Floating Mini HUD** when the main window is minimized.
- **Notification Center + Daily Brief dashboard**.
- **Automation Builder + Workflow Recorder + Replay** of recorded registered action/plugin calls.
- **Multi-agent consultation** (research/coding/study/files/vision/planning) using the configured local model, plus transparent supervisor plans.
- **Task planning view**, **Undo History**, and nested **Crash Recovery Journal**.
- **Privacy audit dashboard** and **Emergency Kill Switch** that gates tools, PC/phone mic streaming, camera preview and outgoing speech.
- **Device manager** for active companion pairings, including individual revoke/rename.
- **Phone ↔ PC clipboard sync** and remote project-status API.
- **Authenticated EMBER local API** endpoints for status, features, workspaces, devices, privacy, notifications, automations, clipboard and project status.
- **Optional Home Assistant connector** for the user's own configured smart-home server.
- **Vision Memory**: explicit save/list/delete for selected screenshots and image files; no background capture.
- **Personal dashboard widgets** for model, workspace/project, tasks, notifications, workflows and safety status.
- **HUD themes**: amber, cyber, violet, emerald, rose and mono; custom accent still supported.
- **Avatar/HUD center customization** between animated face and reactor/core modes.
- **Boot sequence**: Core → Memory → Vision → Plugins → Privacy Guard → EMBER Active.

## Optional components

Some features need software/models that are intentionally not bundled in this small ZIP:

- Offline voice: `faster-whisper`, `kokoro`, its model files, and the normal audio stack.
- Speaker ID: `resemblyzer`.
- Custom **Hey Ember**: a compatible OpenWakeWord `.onnx` or `.tflite` model named `hey_amber` in `config/`.
- Local AI: Ollama, LM Studio, Jan, LocalAI, llama.cpp server, or another compatible local model server.
- Smart home: a Home Assistant URL and user-created long-lived access token.

EMBER does not pretend these external components exist: when missing, the relevant feature reports what is required instead of showing a fake success state.

## Multi-provider intelligence
- Simultaneous provider configuration for xKiro, OpenAI, Anthropic, Groq, OpenRouter, Gemini and Ollama.
- Multiple keys per provider with automatic key rotation and cooldown after quota/rate/auth failures.
- Automatic provider fallback without exposing credentials in status output or logs.
- Typed AUTO/ONLINE chat uses the provider pool; LOCAL is hard-pinned to Ollama.
- Model auto-discovery for providers where no model is pinned.
