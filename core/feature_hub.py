"""EMBER feature-state hub.

Keeps user-facing feature preferences and lightweight local data in one place.
All files stay under config/ so the feature layer is portable with the project.
"""
from __future__ import annotations
import json, os, re, shutil, subprocess, sys, time
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"
STATE_FILE = CONFIG_DIR / "ember_features.json"
LEGACY_STATE_FILE = CONFIG_DIR / "amber_features.json"
PRIVACY_LOG = CONFIG_DIR / "privacy_audit.jsonl"
WORKSPACES_DIR = BASE_DIR / "workspaces"
VISION_DIR = BASE_DIR / "vision_memory"

_DEFAULT = {
    "model_mode": "auto",           # auto | online | local
    "temporary_memory": False,
    "active_workspace": "default",
    "theme": "amber",
    "avatar": "face",
    "voice_profile": "default",
    "kill_switch": False,
    "privacy_logging": True,
    "notification_digest": True,
    "whisper_mode": False,
    "mini_hud": True,
    "performance_profile": "balanced",
    "agent_supervisor": True,
    "visual_agent": True,
    "screen_understanding": True,
    "workflow_recording": False,
    "selected_agents": ["research", "coding", "study", "files", "vision", "planning"],
}


def _load() -> dict:
    # Read the new Ember state first, then transparently fall back to the old
    # AMBER filename so existing users keep every preference after upgrading.
    for path in (STATE_FILE, LEGACY_STATE_FILE):
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(obj, dict):
                return {**_DEFAULT, **obj}
        except Exception:
            continue
    return dict(_DEFAULT)


def _save(data: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def state() -> dict:
    return _load()


def get(key: str, default=None):
    return _load().get(key, default)


def set_value(key: str, value):
    d = _load(); d[key] = value; _save(d); return value


def set_model_mode(mode: str) -> str:
    m = str(mode or "").strip().lower()
    if m not in {"auto", "online", "local"}: raise ValueError("mode must be auto, online, or local")
    set_value("model_mode", m); return m


def temporary_memory_enabled() -> bool:
    return bool(get("temporary_memory", False))


def kill_switch_enabled() -> bool:
    return bool(get("kill_switch", False))


def set_kill_switch(enabled: bool) -> bool:
    set_value("kill_switch", bool(enabled))
    audit("security", "kill_switch", "enabled" if enabled else "disabled")
    return bool(enabled)


def audit(event: str, resource: str, detail: str = "") -> None:
    if not bool(get("privacy_logging", True)):
        return
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    rec = {"ts": datetime.now().isoformat(timespec="seconds"), "event": event, "resource": resource, "detail": str(detail)[:500]}
    with PRIVACY_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def privacy_tail(limit: int = 50) -> list[dict]:
    try:
        lines = PRIVACY_LOG.read_text(encoding="utf-8").splitlines()[-max(1, min(500, int(limit))):]
        return [json.loads(x) for x in lines if x.strip()]
    except Exception:
        return []


def _slug(name: str) -> str:
    s = re.sub(r"[^A-Za-z0-9._-]+", "-", str(name or "").strip()).strip("-._")
    return s[:64] or "default"


def workspace_path(name: str | None = None) -> Path:
    n = _slug(name or get("active_workspace", "default"))
    p = WORKSPACES_DIR / n
    p.mkdir(parents=True, exist_ok=True)
    return p


def create_workspace(name: str, description: str = "", project_path: str = "") -> dict:
    n = _slug(name); p = workspace_path(n)
    meta_path = p / "workspace.json"
    try:
        old = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    except Exception:
        old = {}
    meta = {
        "name": n,
        "description": description.strip() or str(old.get("description", "")),
        "project_path": str(project_path or old.get("project_path", "")).strip(),
        "created": str(old.get("created") or datetime.now().isoformat(timespec="seconds")),
        "updated": datetime.now().isoformat(timespec="seconds"),
    }
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    mem = p / "memory.json"
    if not mem.exists(): mem.write_text("{}", encoding="utf-8")
    for filename, default in (("notes.json", "[]"), ("tasks.json", "[]")):
        q = p / filename
        if not q.exists(): q.write_text(default, encoding="utf-8")
    return meta


def active_workspace_meta() -> dict:
    p = workspace_path() / "workspace.json"
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def set_workspace_project(path: str) -> dict:
    meta = active_workspace_meta()
    return create_workspace(meta.get("name") or get("active_workspace", "default"),
                            meta.get("description", ""), path)

def list_workspaces() -> list[dict]:
    WORKSPACES_DIR.mkdir(parents=True, exist_ok=True)
    out = []
    for p in sorted([x for x in WORKSPACES_DIR.iterdir() if x.is_dir()]):
        try: meta = json.loads((p / "workspace.json").read_text(encoding="utf-8"))
        except Exception: meta = {"name": p.name, "description": ""}
        meta["active"] = p.name == get("active_workspace", "default")
        out.append(meta)
    if not out:
        create_workspace("default", "General EMBER workspace")
        return list_workspaces()
    return out


def select_workspace(name: str) -> str:
    n = _slug(name); create_workspace(n) if not (WORKSPACES_DIR / n).exists() else None
    set_value("active_workspace", n); audit("workspace", "select", n); return n


def workspace_memory(action: str, key: str = "", value: str = "", query: str = ""):
    p = workspace_path() / "memory.json"
    try: data = json.loads(p.read_text(encoding="utf-8"))
    except Exception: data = {}
    a = str(action or "").lower().strip()
    if a in {"put", "save", "set"}:
        if temporary_memory_enabled(): return "Temporary memory is on; this item was not persisted."
        if not key: return "A memory key is required."
        data[key] = {"value": value, "updated": datetime.now().isoformat(timespec="seconds"), "pinned": bool(data.get(key, {}).get("pinned", False))}
        p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"); return f"Saved workspace memory '{key}'."
    if a == "delete":
        if key in data: data.pop(key); p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"); return f"Deleted '{key}'."
        return "Memory item not found."
    if a == "pin":
        if key not in data: return "Memory item not found."
        data[key]["pinned"] = True; p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"); return f"Pinned '{key}'."
    if a == "list":
        return data
    if a == "search":
        q = (query or key).casefold(); return {k:v for k,v in data.items() if q in k.casefold() or q in str(v.get("value", "")).casefold()}
    return "Use save, list, search, pin, or delete."


def save_vision_memory(label: str, image_bytes: bytes, extension: str = ".jpg") -> str:
    if temporary_memory_enabled(): return "Temporary memory is on; vision memory was not saved."
    VISION_DIR.mkdir(parents=True, exist_ok=True)
    safe = _slug(label); stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = VISION_DIR / f"{stamp}-{safe}{extension if extension.startswith('.') else '.'+extension}"
    path.write_bytes(image_bytes); audit("vision", "save", path.name); return str(path)


def list_vision_memory() -> list[str]:
    VISION_DIR.mkdir(parents=True, exist_ok=True)
    return [p.name for p in sorted(VISION_DIR.iterdir(), reverse=True) if p.is_file()][:100]


def delete_vision_memory(name: str) -> bool:
    VISION_DIR.mkdir(parents=True, exist_ok=True)
    target = (VISION_DIR / Path(str(name)).name).resolve()
    if target.parent != VISION_DIR.resolve() or not target.is_file():
        return False
    target.unlink()
    audit("vision", "delete", target.name)
    return True


THEME_PRESETS = {
    "amber": "#ffb000",
    "cyber": "#00d4ff",
    "violet": "#8a5cff",
    "emerald": "#00e5a0",
    "rose": "#ff4f9a",
    "mono": "#d8f8ff",
}

def set_theme(name: str) -> str:
    key = str(name or "amber").strip().lower()
    if key not in THEME_PRESETS:
        raise ValueError("theme must be one of: " + ", ".join(THEME_PRESETS))
    set_value("theme", key); return key


def system_summary() -> dict:
    return {
        "model_mode": get("model_mode", "auto"),
        "temporary_memory": temporary_memory_enabled(),
        "workspace": get("active_workspace", "default"),
        "theme": get("theme", "amber"),
        "avatar": get("avatar", "face"),
        "voice_profile": get("voice_profile", "default"),
        "kill_switch": kill_switch_enabled(),
        "performance_profile": get("performance_profile", "balanced"),
    }
