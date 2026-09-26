"""Persistent local notes plugin."""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

PLUGIN = {
    "name": "quick_notes",
    "description": (
        "Create, list, read, search, update, or delete small local notes for the user. "
        "Use for explicit note-taking requests; do not use instead of the assistant's long-term memory."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {"type": "STRING", "description": "create, list, read, search, update, or delete"},
            "title": {"type": "STRING", "description": "Note title."},
            "content": {"type": "STRING", "description": "Note body for create/update."},
            "query": {"type": "STRING", "description": "Search text for search."},
        },
        "required": ["action"],
    },
}

from core.feature_hub import workspace_path, temporary_memory_enabled

def _path():
    return workspace_path() / "notes.json"


def _load():
    try:
        data = json.loads(_path().read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _save(notes):
    if temporary_memory_enabled():
        return False
    path = _path(); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(notes, ensure_ascii=False, indent=2), encoding="utf-8")
    return True


def _key(text):
    return re.sub(r"\s+", " ", str(text or "").strip().casefold())


def run(parameters: dict, player=None, session_memory=None) -> str:
    action = _key(parameters.get("action"))
    title = str(parameters.get("title") or "").strip()
    content = str(parameters.get("content") or "").strip()
    query = _key(parameters.get("query"))
    notes = _load()

    if action == "list":
        if not notes:
            return "There are no quick notes yet."
        return "Quick notes: " + "; ".join(n.get("title", "Untitled") for n in notes[-30:])

    if action == "search":
        q = query or _key(title)
        if not q:
            return "Tell me what to search for in the notes."
        hits = [n for n in notes if q in _key(n.get("title")) or q in _key(n.get("content"))]
        if not hits:
            return "No quick notes matched that search."
        return "\n\n".join(f"{n.get('title','Untitled')}: {n.get('content','')}" for n in hits[:10])

    idx = next((i for i, n in enumerate(notes) if _key(n.get("title")) == _key(title)), None)

    if action == "read":
        if idx is None:
            return f"I could not find a note titled '{title}'."
        n = notes[idx]
        return f"{n.get('title','Untitled')}: {n.get('content','')}"

    if action == "delete":
        if temporary_memory_enabled(): return "Temporary memory is on; notes are not being changed."
        if idx is None:
            return f"I could not find a note titled '{title}'."
        removed = notes.pop(idx)
        _save(notes)
        return f"Deleted the quick note '{removed.get('title','Untitled')}'."

    if action in {"create", "update"}:
        if temporary_memory_enabled(): return "Temporary memory is on; notes are not being changed."
        if not title:
            return "A note title is required."
        if not content:
            return "The note content is empty."
        now = datetime.now().isoformat(timespec="seconds")
        if idx is None:
            notes.append({"title": title, "content": content, "updated": now})
            verb = "Created"
        else:
            notes[idx].update({"title": title, "content": content, "updated": now})
            verb = "Updated"
        _save(notes)
        if player:
            player.write_log(f"NOTES: {verb.lower()} — {title}")
        return f"{verb} the quick note '{title}'."

    return "Unknown notes action. Use create, list, read, search, update, or delete."
