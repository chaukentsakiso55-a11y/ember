"""Small persistent local task list plugin."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

PLUGIN = {
    "name": "task_list",
    "description": (
        "Maintain a simple local to-do list: add tasks, list open/completed tasks, mark tasks done, "
        "reopen them, or remove them. Use when the user explicitly asks to manage a task list."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {"type": "STRING", "description": "add, list, done, reopen, or remove"},
            "task": {"type": "STRING", "description": "Task text or an exact/partial task name."},
            "filter": {"type": "STRING", "description": "For list: open, done, or all."},
        },
        "required": ["action"],
    },
}

from core.feature_hub import workspace_path, temporary_memory_enabled

def _path():
    return workspace_path() / "tasks.json"


def _load():
    try:
        data = json.loads(_path().read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _save(items):
    if temporary_memory_enabled():
        return False
    path = _path(); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    return True


def _find(items, needle):
    n = str(needle or "").strip().casefold()
    if not n:
        return None
    exact = next((i for i, x in enumerate(items) if str(x.get("task", "")).casefold() == n), None)
    if exact is not None:
        return exact
    hits = [i for i, x in enumerate(items) if n in str(x.get("task", "")).casefold()]
    return hits[0] if len(hits) == 1 else None


def run(parameters: dict, player=None, session_memory=None) -> str:
    action = str(parameters.get("action") or "").strip().casefold()
    task = str(parameters.get("task") or "").strip()
    filt = str(parameters.get("filter") or "open").strip().casefold()
    items = _load()

    if action == "add":
        if temporary_memory_enabled(): return "Temporary memory is on; tasks are not being changed."
        if not task:
            return "Tell me the task to add."
        items.append({"task": task, "done": False, "created": datetime.now().isoformat(timespec="seconds")})
        _save(items)
        return f"Added task: {task}"

    if action == "list":
        view = items
        if filt == "open":
            view = [x for x in items if not x.get("done")]
        elif filt == "done":
            view = [x for x in items if x.get("done")]
        if not view:
            return f"There are no {filt if filt in {'open','done'} else ''} tasks.".replace("  ", " ")
        lines = [f"{'✓' if x.get('done') else '○'} {x.get('task','')}" for x in view[:50]]
        return "\n".join(lines)

    if action in {"done", "reopen", "remove"} and temporary_memory_enabled():
        return "Temporary memory is on; tasks are not being changed."
    idx = _find(items, task)
    if idx is None:
        return "I could not uniquely match that task. Say more of its title."

    if action == "done":
        items[idx]["done"] = True
        items[idx]["completed"] = datetime.now().isoformat(timespec="seconds")
        _save(items)
        return f"Marked done: {items[idx]['task']}"
    if action == "reopen":
        items[idx]["done"] = False
        items[idx].pop("completed", None)
        _save(items)
        return f"Reopened: {items[idx]['task']}"
    if action == "remove":
        removed = items.pop(idx)
        _save(items)
        return f"Removed task: {removed['task']}"

    return "Unknown task action. Use add, list, done, reopen, or remove."
