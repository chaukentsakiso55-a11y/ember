# INFINITY OS V7 REBORN
## Owner Manual — Ops 20 Features / Real-Time Owner Control Private Build

**Manual target:** `Infinity-OS-V7-REBORN-OPS-20-FEATURES-PRIVATE`

Infinity OS Desktop is a native Windows AI operating layer built around AEGIS, AI routing, real-time desktop control, project intelligence, voice, automation, recovery, device/phone connectivity, and owner-only remote control.

> **Identity rule:** This Windows/Desktop Infinity build is independent and is **not** a Cyber Pulse product. **Infinity OS Android** is the Infinity edition that belongs to Cyber Pulse.

---

# 1. Quick Start

## First launch

1. Extract the Infinity ZIP into a **fresh folder**.
2. Make sure a supported 64-bit Python version is installed. Infinity requires **Python 3.11 or newer**.
3. Double-click:

   `RUN-INFINITY.bat`

4. Leave the launcher window open while setup runs.
5. Infinity will:
   - choose a compatible Python installation,
   - create or repair `.venv`,
   - prepare pip,
   - install all packages in `requirements.txt`,
   - verify the required Python modules,
   - install Playwright Chromium if missing,
   - create/refresh the desktop shortcut,
   - launch Infinity.

The first run can take longer because PySide6, Windows automation libraries, voice packages, browser automation, Vosk, and other dependencies may need to download.

## Important private-build warning

The PRIVATE build can contain locally wired AI credentials. On Windows, Infinity Vault is designed to migrate bootstrap credentials into DPAPI-protected local storage and remove the plaintext bootstrap file after a successful migration.

**Do not send the private ZIP to testers, friends, GitHub, or public storage.**

---

# 2. Main Interface

Infinity’s left sidebar contains these main areas:

| Page | Purpose |
|---|---|
| **Dashboard** | Quick system overview and shortcuts |
| **Mission** | Mission Control: providers, performance, capsules, mesh, task queue, operator, WhatsApp, recovery |
| **AEGIS** | Main AI conversation and owner-command interface |
| **AI Nexus** | Providers, models, routing, health and offline AI |
| **Browser** | Playwright-powered browser automation |
| **Memory** | Project/assistant memory |
| **System** | System information and telemetry |
| **Forge** | Developer workspace, files, terminal, Git and builds |
| **Study** | Focus/study tools |
| **Workflows** | Repeatable automations and schedules |
| **Control** | Windows control and phone companion |
| **Mesh** | Trusted devices and safe local discovery |
| **Plugins** | Plugin/MCP management |
| **Security** | Permission policies and audit history |
| **Notifications** | Infinity event/results feed |
| **Ops** | Owner oversight, autonomy, rollback, checkpoints, Bug Hunter, releases |
| **NextGen** | Capsules, Vision, Agent Team, Sandbox, Memory 3.0, Vault, Ultimate and WhatsApp |
| **Settings** | Appearance, AI/API settings, Voice Studio, updates and recovery |

The top bar contains a global AEGIS command field and the live microphone button.

---

# 3. AEGIS — Main AI Assistant

Open **AEGIS** for normal chat, coding help, reasoning, research, project work and owner commands.

## Basic chat

Type a question and press **Send**.

Recommended settings:

- **Provider:** Auto / Smart Route
- **Model:** Auto model unless you need a specific one
- **Mode:** `Answer` for normal answers, `Agent` when you want tool-based actions

Smart Route can fail over between configured providers. In this private build, xKiro is configured as a preferred provider for general/coding work, while other configured providers remain fallbacks.

## Example normal questions

- `Explain this Kotlin error.`
- `What does this Python function do?`
- `Summarize my active project.`
- `What Cyber Pulse products do you know about?`
- `Is Desktop Infinity part of Cyber Pulse?`

## Attachments

Use **+ File** in AEGIS to attach supported documents/files for analysis.

---

# 4. Real-Time Owner Control

Infinity includes an owner-only AEGIS Real-Time Operator.

It accepts trusted owner commands from:

- local Infinity desktop,
- live voice,
- Global Command Mode,
- configured owner WhatsApp channel.

## Example owner commands

- `Open VS Code.`
- `Open Chrome and search for Android Studio documentation.`
- `Open my active project and run its tests.`
- `Open VS Code, inspect StudyLock, fix the build errors and keep testing until it passes.`
- `Check what is on my screen and help me continue.`
- `Open the active project and find where authentication is handled.`

For normal Windows tasks, AEGIS can use Windows UI Automation, mouse/keyboard control, browser automation, clipboard, screenshots and terminal/file tools.

It can run bounded **plan → act → inspect → continue** cycles.

## Important limit

Owner control does **not** bypass:

- Windows UAC,
- passwords,
- lock screens,
- administrator policy,
- Windows security,
- app-specific security,
- Infinity Security Center.

---

# 5. Code Autopilot

For a coding/development request, Infinity can run a coding mission.

Typical flow:

1. Resolve the active Project Capsule.
2. Open the project in VS Code using the `code` launcher when available.
3. Create a Time Machine/checkpoint snapshot.
4. Index the project.
5. Find relevant source/config files.
6. Edit files directly on disk while VS Code is open.
7. Run recognized diagnostics/tests/build commands.
8. Read failures.
9. Attempt bounded repairs.
10. Re-run tests/builds.

The default operator configuration limits automatic repair loops and operator steps so a mission cannot run forever.

## Best first coding test

`Open VS Code and open my active project. Inspect it, run its tests, fix any errors you find, and tell me what you changed.`

## If VS Code does not open

Make sure Visual Studio Code is installed and its `code` command is available in Windows PATH.

---

# 6. Project Capsules and Project Brain

Open:

**NextGen → Capsules**

A Project Capsule gives a project its own workspace identity.

## Create a capsule

1. Click **+ New Capsule**.
2. Enter a name.
3. Choose the project folder.
4. Select the new capsule.
5. Click **Set Active**.

The active capsule becomes AEGIS’s default project workspace.

## Project Brain

Project Brain indexes relevant code/text files in the active project and can inject matching source context into AEGIS.

Use this when you want Infinity to understand a large project without manually pasting every file.

---

# 7. Mission Control

Open **Mission**.

Mission Control shows the current state of:

- Infinity Core,
- performance mode,
- active Project Capsule,
- Memory 3.0 graph,
- device mesh,
- AI providers,
- Task Queue,
- Real-Time Operator,
- WhatsApp bridge,
- Emergency Stop,
- Watchdog,
- Action Timeline.

Quick controls include:

- **AEGIS Vision**
- **Time Machine Snapshot**
- **Live Voice**
- **Auto Performance**
- **Agent Team**
- **Ops Center**

Mission Control is the best page for checking whether the major Infinity systems are alive.

---

# 8. Ops — Owner Operations Center

Open **Ops**.

This is the primary control room for autonomous AEGIS missions.

## Autonomy levels

Infinity provides five levels:

### Observe
AEGIS observes and reports.

### Suggest
AEGIS proposes actions but does not freely execute them.

### Ask
AEGIS requests approval more often.

### Routine
Routine actions can proceed while sensitive actions remain gated.

### Owner
Highest owner-autonomy setting available inside Infinity’s security model.

Even **Owner** mode does not override Security Center or Windows security boundaries.

## Mission controls

Ops provides:

- **Pause**
- **Resume**
- **Skip Next**
- **Emergency Stop**
- **Clear Stop**
- **Roll Back Last Mission**

## Goal Lock

When a mission is active, Goal Lock keeps the operator focused on the current owner goal.

---

# 9. Emergency Stop

The global Windows emergency hotkey is:

**Ctrl + Alt + Esc**

This stops operator/task/voice automation.

After an emergency stop, owner automation must be cleared locally before it resumes.

Use Emergency Stop when:

- the mouse is moving somewhere you did not expect,
- AEGIS is working on the wrong goal,
- an automation loop is behaving incorrectly,
- you want all autonomous activity stopped immediately.

You can also trigger Emergency Stop from **Ops**.

---

# 10. Live Action Timeline and Visual Cursor

## Action Timeline

Ops records mission events such as:

- mission started,
- app opened,
- file edited,
- build launched,
- error detected,
- repair attempted,
- permission used,
- mission completed/failed.

Use the timeline to see what AEGIS is doing instead of treating automation like a black box.

## Visual Cursor Overlay

Before coordinate-based mouse actions, Infinity can show a visible AEGIS cursor marker so you can see where automation is acting.

---

# 11. Rollback, Time Machine and Checkpoints

Infinity contains several recovery layers.

## Time Machine

Creates snapshots before important changes.

## Coding Checkpoints

Code Autopilot creates project checkpoints before repair iterations.

## Roll Back Last Mission

In **Ops**, click **Roll Back Last Mission** to restore the pre-mission snapshot where available.

Rollback can restore local project/system files captured by the snapshot.

It cannot automatically undo every external action. Examples that may not be reversible include:

- a message that was already sent,
- a website/account change already submitted,
- an external service action completed outside the local snapshot.

---

# 12. Bug Hunter

Open:

**Ops → Project Intelligence**

Choose or activate a project and click **Bug Hunter**.

Bug Hunter can:

- recognize the project type,
- run the available test/build path,
- collect failures,
- rank likely problems,
- inspect selected source warning markers.

Use it before asking Code Autopilot to make large changes.

---

# 13. Local Code Search

Open:

**Ops → Project Intelligence**

1. Select the project.
2. Click **Index Code**.
3. Enter a query.
4. Click **Search**.

Examples:

- `authentication`
- `Firebase`
- `PIN validation`
- `MainActivity`
- `API routing`

The local source index excludes common generated dependency/build folders and secret-like filenames.

---

# 14. Architecture Map

Open:

**Ops → Project Intelligence → Architecture Map**

Infinity extracts:

- source files,
- definitions,
- import relationships,

and produces architecture information including Mermaid-compatible graph text.

Use this for understanding a large codebase before editing it.

---

# 15. Build Artifact Manager

Open:

**Ops → Project Intelligence → Scan Artifacts**

Infinity can recognize outputs such as:

- APK
- AAB
- EXE
- MSI
- MSIX
- ZIP
- JAR
- WAR
- WHL
- DEB
- RPM

It records metadata including file size, modification time and SHA-256.

---

# 16. Release Assistant

Open:

**Ops → Project Intelligence → Prepare Release**

Release Assistant can:

1. create a checkpoint,
2. optionally update common version metadata,
3. run tests/build,
4. scan produced artifacts,
5. calculate hashes,
6. prepare local release metadata.

**It does not publish/upload the release automatically.**

---

# 17. AEGIS Watchdog and Self-Healing

## Watchdog

Infinity includes an external Windows watchdog that can watch the main Infinity process and use Safe Mode recovery after unexpected crashes/hangs, with restart-loop protection.

## Self-Healing

Infinity can track repeated startup crash signatures and quarantine repeatedly failing optional components.

## Safe Mode

If normal startup fails, run:

`START-SAFE-MODE.bat`

Crash information may be written to:

`data/last_crash.txt`

Launcher logs are stored in:

`data/logs/launcher.log`

---

# 18. AEGIS Vision / Screen Awareness

## One-time vision

Open:

**NextGen → Vision**

or use the **AEGIS Vision** button in Mission Control.

Infinity can capture the current screen through its permission-gated screenshot path and ask a vision-capable AI provider to describe:

- visible errors,
- controls,
- windows,
- useful next actions.

Vision itself does not automatically click anything.

## Screen Awareness 2.0

The Ultimate feature layer includes optional continuous screen analysis.

Use this only when you actually want Infinity repeatedly observing the visible screen.

---

# 19. Voice and Always-On Live Chat

Infinity can operate as a live voice assistant.

Open:

**Settings → Voice**

Important options include:

- speak every AEGIS answer,
- auto-speak,
- continuous live chat,
- auto-start live chat,
- voice engine,
- voice preset,
- neural/system voice,
- rate,
- pitch/depth,
- volume,
- wake words.

The global top-bar mic button shows whether the continuous microphone is active.

## Voice engines

### Auto
Tries Microsoft neural TTS first, then Windows/system fallback.

### Microsoft Edge Neural
Online higher-quality speech through `edge-tts`.

### Windows/System
Local SAPI/pyttsx3 fallback.

## Included style presets

Examples include:

- JARVIS
- EDITH
- FRIDAY
- ULTRON
- OPTIMUS PRIME
- REFERENCE DARK
- DARK TITAN
- SHADOW LORD
- MECH COMMANDER
- CYBER VILLAIN
- ANIME MENTOR
- ANIME RIVAL
- SHONEN HERO
- ANIME STRATEGIST
- ANIME HEROINE
- CYBER SAMURAI

These are style/tone presets, not packaged exact clones of performers.

## Barge-in

While AEGIS is speaking, use wake-prefixed interruption phrases such as:

- `AEGIS stop`
- `AEGIS, actually...`

This helps avoid the microphone treating the PC speakers as the owner.

---

# 20. Offline Voice

Infinity supports Vosk for local speech recognition.

Open:

**NextGen → Ultimate + WhatsApp**

Under **Offline Voice**:

1. Click **Choose Vosk Model Folder**.
2. Select a downloaded Vosk model directory.
3. Choose STT mode:
   - `auto`
   - `offline`
   - `online`

Without an offline Vosk model, the online speech-recognition fallback may use Google’s recognizer, meaning spoken phrases can be sent to that service for transcription.

---

# 21. AI Nexus

Open **AI Nexus** to manage AI routing.

Use it to:

- inspect providers,
- select/discover models,
- run health checks,
- detect offline AI,
- control routing/failover,
- use provider diagnostics.

## Smart Route

For ordinary use, keep AEGIS on **Auto / Smart Route**.

Infinity can use observed provider/model performance and provider reputation when routing.

## If AI does not answer

1. Open **AI Nexus**.
2. Run **Health Check**.
3. Look for:
   - authentication problems,
   - model access errors,
   - quota/rate limits,
   - timeouts,
   - DNS/internet errors,
   - unavailable local runtimes.

A bad/expired provider credential cannot be fixed by routing logic; Infinity can only fail over to another working provider.

---

# 22. Offline AI

Infinity can discover compatible local AI servers running on standard localhost endpoints.

Supported runtime foundations include:

- Ollama
- LM Studio
- llama.cpp / llama-server
- custom local OpenAI-compatible server

Use:

**AI Nexus → Detect Offline AI**

Enable **Offline only** when you want prompts kept away from configured cloud AI providers.

---

# 23. Infinity Vault

Infinity Vault stores secret configuration without displaying secret values in normal UI.

Open:

**NextGen → AI Lab + Vault**

The private build’s AI bootstrap credentials are intended to migrate to Windows DPAPI-backed storage.

Never paste secret values into normal project code, screenshots, public issue reports or shareable builds.

---

# 24. Memory Systems

Infinity has several kinds of memory.

## Memory 2.0
Searchable assistant/project memory.

## Memory 3.0 Knowledge Graph
Stores nodes and relationships so AEGIS can reason across connected facts.

## Owner Knowledge
The `knowledge/` folder contains owner-maintained profile/product information and identity rules.

Important built-in identity rule:

**Desktop Infinity is independent from Cyber Pulse. Infinity OS Android is the Infinity version that belongs to Cyber Pulse.**

## Encrypted Private Knowledge
The Ultimate layer provides an AES-GCM encrypted local knowledge library.

Add private documents from:

**NextGen → Ultimate + WhatsApp**

Matching decrypted snippets are passed into AEGIS only when relevant to the query.

---

# 25. Agent Team

Open:

**NextGen → Agent Team**

Specialist roles include:

- Planner
- Researcher
- Coder
- Debugger
- Security Reviewer
- Verifier

Use Agent Team when a task benefits from specialized roles rather than one single-pass answer.

---

# 26. Infinity Sandbox

Open:

**NextGen → Sandbox + Time**

Sandbox creates an isolated project copy where commands/tests can run away from the live project.

When sandbox changes are promoted back to the source project, Infinity creates a Time Machine snapshot first.

Use Sandbox for risky experiments before applying them to the real project.

---

# 27. Study Mode

The latest Infinity build contains both the Study page and an Ultimate Study Mode.

## Study page

Use it for:

- focus sessions,
- session intent,
- focus totals,
- memory reflections.

## Ultimate Study Mode

Open:

**NextGen → Ultimate + WhatsApp**

Use:

- **Toggle Study Mode**
- **Quick Quiz**

This changes AEGIS’s teaching/explanation behavior without changing Desktop Infinity’s product identity.

---

# 28. Workflows and Background Intelligence

Open **Workflows** to create reusable automations.

You can:

- create a workflow from a prompt,
- run selected workflows,
- enable/disable them,
- use schedules,
- build step dependencies.

Scheduled workflows only run permissions already allowed by Security Center.

Background Intelligence can react to Infinity Event Bus events and trigger notifications or existing workflows.

---

# 29. Browser Agent

Open **Browser** for Playwright-powered browser automation.

`RUN-INFINITY.bat` verifies Playwright Chromium and downloads it if necessary.

Browser permissions are still governed by Security Center.

A page navigation may be allowed while actions such as form submission can still require approval.

---

# 30. Control Center

Open **Control**.

This area provides:

- natural-language laptop control,
- Windows UI Automation,
- active-window inspection,
- phone companion controls.

Example:

`Open Chrome, search for Android Studio documentation, then open VS Code.`

Infinity can show the planned actions and permissions before execution.

---

# 31. Phone Companion

In **Control**:

1. Click **Start Remote**.
2. Use the displayed LAN URL.
3. Click **Show QR** if needed.
4. Use the pairing PIN.
5. Keep Infinity Desktop running.

The phone companion is intended for trusted devices on the same network.

Closing Infinity Desktop stops the companion server.

---

# 32. WhatsApp Control Bridge

Open:

**NextGen → Ultimate + WhatsApp**

The bridge is designed for the official WhatsApp Business / Cloud API.

## Owner vs public behavior

### Owner number
Your configured owner number gets private Owner Mode.

It can:

- chat with AEGIS,
- issue natural owner commands,
- start Real-Time Operator tasks,
- receive mission progress,
- use task confirmation when needed.

Examples:

- `Open VS Code and check StudyLock.`
- `Run the active project tests.`
- `Open Chrome.`
- `!open VS Code`
- `cmd: run the tests`

### Other numbers
Other chats are public assistant-only.

They cannot:

- execute desktop commands,
- control the PC,
- access private knowledge,
- access local files,
- access API credentials,
- inherit owner context.

## Configure WhatsApp

Click **Configure** and supply:

- WhatsApp Cloud API access token,
- Phone Number ID,
- webhook verification token,
- owner WhatsApp number including country code,
- Meta App Secret (optional but recommended).

The secret values are stored through Infinity Vault.

## Webhook

The local bridge uses port **8787** by default.

WhatsApp Cloud API requires a **public HTTPS webhook endpoint**, so your local endpoint must be securely exposed/reverse-proxied and then registered in the Meta app.

This bridge handles new Cloud API messages. It is not an unofficial WhatsApp Web scraper and does not promise access to all historical personal-app conversations/settings.

---

# 33. Task Queue

The AEGIS Task Queue stores longer or permission-gated tasks.

Open:

**NextGen → Ultimate + WhatsApp**

Tasks can have statuses such as queued, waiting for permission, running, completed or failed.

If a task is waiting for an `ask` permission, the owner can confirm it from the UI or, where supported, by owner WhatsApp using the task ID.

---

# 34. Device Mesh

Open **Mesh**.

Infinity can maintain a trusted device registry and perform safe local discovery.

## Same-network discovery

**Scan Same Network** is limited to the local private IPv4 network segment. It combines local presence information and Windows neighbor/ARP data.

It does not:

- scan Internet ranges,
- brute-force credentials,
- probe passwords,
- perform hidden port scanning.

## Bluetooth

**Nearby Bluetooth** lists devices Windows reports as present/known.

It does not bypass Bluetooth pairing.

---

# 35. Plugins and Skill Store

## Plugins
Open **Plugins** to manage permission-declared plugin/MCP integrations.

Plugin execution remains permission-controlled.

## Skill Store
NextGen includes local skill manifests such as:

- Android Development
- School & Study
- GitHub Project
- Cyber Pulse Workspace

Skills can be enabled/disabled.

---

# 36. Security Center

Open **Security**.

Every powerful capability uses a policy.

Available policy types:

- `always_allow`
- `ask`
- `session`
- `deny`

Default policies in this build include:

| Capability | Default |
|---|---|
| Files read | Always allow |
| Files write | Ask |
| Command execution | Ask |
| App launch | Session |
| App control | Ask |
| Browser navigation | Session |
| Browser form submit | Ask |
| Message sending | Ask |
| Clipboard read | Ask |
| Clipboard write | Session |
| Microphone | Ask |
| Camera | Deny |
| Power control | Deny |
| Plugin execution | Ask |
| Remote network | Session |
| Network discovery | Ask |

Security Center remains authoritative even when Ops autonomy is set to **Owner**.

## Recommended rule

Keep these as **Ask** or **Deny** unless you have a specific reason to change them:

- message sending,
- power control,
- destructive command execution,
- plugin execution,
- sensitive file writes.

---

# 37. Permission Receipts

Open:

**Ops → Receipts + Recovery**

Infinity records:

- permission,
- action,
- outcome,
- source,
- time,
- associated mission/goal when available.

Use receipts to audit what AEGIS actually did.

---

# 38. Performance and Network Dashboard

Open:

**Ops → System + Network**

Infinity can show:

- system and Infinity CPU/RAM telemetry,
- process information,
- Infinity network connections,
- traffic counters,
- provider endpoint health,
- provider reputation.

The network dashboard observes Infinity-related connectivity and does not secretly scan public networks.

---

# 39. Provider Reputation

Infinity learns from observed provider/model/task results.

Smart Route can use that reputation when choosing an AI provider.

A provider that repeatedly performs well for a task category can receive a stronger route score than one that repeatedly fails or responds poorly.

---

# 40. Daily Owner Briefing

Infinity can generate a local owner briefing summarizing items such as:

- active project,
- detected workspace type,
- provider reputation,
- recent artifacts,
- recovery state.

Open:

**Ops → System + Network → Generate Owner Briefing**

---

# 41. Global Command Mode

On Windows, press:

**Ctrl + Space**

Infinity uses the Windows global hotkey system to bring Infinity forward and focus the command field.

Examples:

- `Open AEGIS`
- `Open Ops`
- `Open VS Code`
- `Ask AEGIS to explain this error`

---

# 42. Useful AEGIS Command Examples

## Coding

`Open VS Code, open the active project, run the tests and fix the errors.`

`Find where Firebase authentication is initialized.`

`Run Bug Hunter on the active project.`

`Search the project for every PIN validation path.`

`Create a checkpoint before you edit anything.`

## Desktop

`Open Chrome.`

`Open VS Code and focus the terminal.`

`Tell me what is currently visible on screen.`

`Open Infinity Ops.`

## Study

`Turn on Study Mode and quiz me on Grade 10 Geography.`

`Explain this topic at Grade 10 level, then give me five questions.`

## Project intelligence

`Summarize the architecture of my active Project Capsule.`

`Find the likely cause of the current build failure.`

## Recovery

`Stop the current mission.`

`Explain what changed in the last mission.`

Use **Ctrl + Alt + Esc** when you need a hard emergency stop.

---

# 43. Troubleshooting

## RUN-INFINITY says Python is unsupported

Install Python 3.11 or newer.

Test from Command Prompt:

`py -3.11 --version`

or:

`python --version`

## Requirements fail to install

Check:

`data/logs/launcher.log`

Then check internet connectivity and run `RUN-INFINITY.bat` again. Pip will normally reuse packages already downloaded.

## A required module is missing

Run:

`CHECK-REQUIREMENTS.bat`

or run `RUN-INFINITY.bat` again to repair the environment.

## Browser Agent does not work

`RUN-INFINITY.bat` normally verifies Chromium automatically.

You can also use:

`INSTALL-BROWSER.bat`

## Infinity crashes

Try:

`START-SAFE-MODE.bat`

Then inspect:

`data/last_crash.txt`

and:

`data/logs/launcher.log`

## AEGIS does not answer

Use:

**AI Nexus → Health Check**

Check authentication, model access, quota/rate limits, internet/DNS and provider availability.

## Local Ollama does not answer

Make sure the Ollama server is actually running. Infinity skips unreachable local runtimes.

## Microphone does not work

Check:

- Windows microphone permission,
- Infinity Security Center microphone permission,
- correct input device,
- live mic status,
- STT mode,
- Vosk model path if using offline mode.

## AEGIS does not control an app

Check:

- Security Center policy,
- whether the app is running under a different privilege level,
- whether UAC/admin boundaries are involved,
- whether Windows UI Automation can see the control.

Infinity does not bypass privilege boundaries.

## VS Code coding mission does not display

Install VS Code and make sure the `code` launcher is available.

## WhatsApp bridge says not configured

Re-open:

**NextGen → Ultimate + WhatsApp → Configure**

Make sure all required Cloud API values are saved and port 8787 is free.

---

# 44. Backup and Sharing Rules

Before experimenting with high-autonomy tasks:

1. Activate the correct Project Capsule.
2. Create a checkpoint or Time Machine snapshot.
3. Confirm the active goal.
4. Keep Ops visible for the first few missions.
5. Know the Emergency Stop hotkey.

Never share:

- the PRIVATE Infinity ZIP,
- `config/.env.local`,
- vault files,
- API credentials,
- WhatsApp Cloud API secrets,
- private knowledge stores.

Use a sanitized/shareable build for other people.

---

# 45. Owner Checklist

For the best experience:

- [ ] Run `RUN-INFINITY.bat`
- [ ] Verify AI Nexus providers
- [ ] Keep AEGIS on Smart Route
- [ ] Create Project Capsules
- [ ] Set the correct active project
- [ ] Check Security Center policies
- [ ] Test `Ctrl + Space`
- [ ] Memorize `Ctrl + Alt + Esc`
- [ ] Test live voice
- [ ] Configure offline Vosk if wanted
- [ ] Test AEGIS Vision
- [ ] Run Bug Hunter on a test project
- [ ] Create a manual checkpoint
- [ ] Test rollback on a disposable project
- [ ] Configure WhatsApp only after the local system is stable
- [ ] Keep the private build private

---

# 46. Core Safety Principle

Infinity is designed to be powerful, but control is split into layers:

**Owner intent → AEGIS planning → Security Center permission → Tool execution → Timeline/receipt → Recovery/rollback**

That structure is intentional. More autonomy should not mean less visibility or fewer recovery options.

---

## End of Manual

**Build family:** Infinity OS V7 REBORN  
**Owner build:** Ops 20 Features + Real-Time Owner Control + Ultimate + WhatsApp + Live Voice + NextGen  
**Platform:** Windows Desktop  
**Cyber Pulse status:** Desktop Infinity is independent; Infinity OS Android is the Cyber Pulse Infinity edition.
