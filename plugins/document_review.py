"""Structured document-review display plugin.

The model performs the reasoning; this plugin validates the structured result and
renders it in EMBER's existing review panel.
"""
from __future__ import annotations

PLUGIN = {
    "name": "document_review",
    "description": (
        "Display a structured review of a document the user asked you to examine. "
        "Use after reading the document: provide a plain-language summary, important findings, "
        "quotes/snippets where useful, suggestions, and unresolved points. This is a presentation tool, "
        "not a substitute for professional legal, medical, or financial advice."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "title": {"type": "STRING", "description": "Document name or review title."},
            "summary": {"type": "STRING", "description": "Short plain-language summary."},
            "findings": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "heading": {"type": "STRING"},
                        "detail": {"type": "STRING"},
                        "severity": {"type": "STRING", "description": "serious, caution, or note"},
                        "quote": {"type": "STRING", "description": "Short relevant excerpt; optional."},
                        "suggestion": {"type": "STRING", "description": "Practical next step; optional."},
                    },
                    "required": ["heading", "detail", "severity"],
                },
            },
            "unclear": {"type": "ARRAY", "items": {"type": "STRING"}},
        },
        "required": ["title", "summary", "findings"],
    },
    "behavior": "NON_BLOCKING",
    "scheduling": "SILENT",
}


def run(parameters: dict, player=None, session_memory=None) -> str:
    title = str(parameters.get("title") or "Document review").strip()
    summary = str(parameters.get("summary") or "").strip()
    findings = []
    for item in (parameters.get("findings") or [])[:30]:
        if not isinstance(item, dict):
            continue
        heading = str(item.get("heading") or "").strip()
        detail = str(item.get("detail") or "").strip()
        if not heading or not detail:
            continue
        severity = str(item.get("severity") or "note").strip().lower()
        if severity not in {"serious", "caution", "note"}:
            severity = "note"
        findings.append({
            "heading": heading,
            "detail": detail,
            "severity": severity,
            "quote": str(item.get("quote") or "").strip()[:500],
            "suggestion": str(item.get("suggestion") or "").strip(),
        })
    unclear = [str(x).strip() for x in (parameters.get("unclear") or []) if str(x).strip()][:20]

    if player is None or not hasattr(player, "show_review"):
        return "The document review panel is not available in this build."
    try:
        player.show_review(title, summary, findings, unclear)
        player.write_log(f"REVIEW: {title} — {len(findings)} finding(s)")
        return f"I opened the structured review for {title}."
    except Exception as exc:
        return f"Could not display the document review: {exc}"
