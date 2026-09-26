"""Deterministic local text utilities."""
from __future__ import annotations

import re

PLUGIN = {
    "name": "text_toolkit",
    "description": (
        "Perform deterministic local text operations without another model call: count words/characters, "
        "change case, collapse whitespace, deduplicate lines, sort lines, or reverse text."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "operation": {"type": "STRING", "description": "stats, upper, lower, title, clean, dedupe_lines, sort_lines, or reverse"},
            "text": {"type": "STRING", "description": "Text to process."},
        },
        "required": ["operation", "text"],
    },
}


def run(parameters: dict, player=None, session_memory=None) -> str:
    op = str(parameters.get("operation") or "").strip().casefold()
    text = str(parameters.get("text") or "")
    if op == "stats":
        words = re.findall(r"\b\w+\b", text, flags=re.UNICODE)
        lines = text.splitlines() or ([""] if text else [])
        return f"Words: {len(words)} | Characters: {len(text)} | Lines: {len(lines)}"
    if op == "upper":
        return text.upper()
    if op == "lower":
        return text.lower()
    if op == "title":
        return text.title()
    if op == "clean":
        return re.sub(r"[ \t]+", " ", re.sub(r"\n{3,}", "\n\n", text)).strip()
    if op == "dedupe_lines":
        out, seen = [], set()
        for line in text.splitlines():
            key = line.strip().casefold()
            if key not in seen:
                seen.add(key); out.append(line)
        return "\n".join(out)
    if op == "sort_lines":
        return "\n".join(sorted(text.splitlines(), key=str.casefold))
    if op == "reverse":
        return text[::-1]
    return "Unknown text operation."
