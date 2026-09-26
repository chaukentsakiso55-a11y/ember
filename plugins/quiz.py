"""Interactive quiz plugin for EMBER.

Gemini supplies the questions; the existing HUD renders and collects answers.
No network or extra package is required by this plugin.
"""
from __future__ import annotations

import re

PLUGIN = {
    "name": "quiz",
    "description": (
        "Open an interactive on-screen quiz. Use this when the user asks to be tested, "
        "quizzed, drilled, or given practice questions. Supply the questions and answers; "
        "the HUD handles answering and reports the completed results back to the conversation."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "topic": {"type": "STRING", "description": "Short quiz topic/title."},
            "questions": {
                "type": "ARRAY",
                "description": "Questions to show, normally 3-15 items.",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "question": {"type": "STRING", "description": "Question text."},
                        "type": {"type": "STRING", "description": "mcq, short, true_false, or open."},
                        "options": {
                            "type": "ARRAY",
                            "items": {"type": "STRING"},
                            "description": "Answer choices for MCQ/true-false; omit for typed answers."
                        },
                        "answer": {"type": "STRING", "description": "Expected answer."},
                        "note": {"type": "STRING", "description": "Optional brief explanation shown after answering."},
                    },
                    "required": ["question", "answer"],
                },
            },
        },
        "required": ["topic", "questions"],
    },
    "behavior": "NON_BLOCKING",
    "scheduling": "SILENT",
}


def _norm(value: str) -> str:
    value = str(value or "").strip().casefold()
    value = re.sub(r"\s+", " ", value)
    value = re.sub(r"^[a-d][\).:\-]\s*", "", value)
    return value.strip(" .,!?:;\t\r\n")


def _grade(question: dict, given: str):
    expected = _norm(question.get("answer", ""))
    actual = _norm(given)
    qtype = _norm(question.get("type", ""))
    options = question.get("options") or []

    # Choice questions and true/false can be marked deterministically.
    if options or qtype in {"mcq", "multiple choice", "true_false", "true false", "true/false"}:
        return bool(expected) and actual == expected

    # Strict short/fill-in answers are safe to auto-mark. Open-ended questions
    # go back to the model for semantic marking when the quiz finishes.
    if qtype in {"short", "short answer", "fill", "fill_in", "fill in"}:
        return bool(expected) and actual == expected
    return None


def run(parameters: dict, player=None, session_memory=None) -> str:
    topic = str(parameters.get("topic") or "Quiz").strip()
    raw = parameters.get("questions") or []
    questions = []
    for item in raw[:20]:
        if not isinstance(item, dict):
            continue
        q = str(item.get("question") or "").strip()
        ans = str(item.get("answer") or "").strip()
        if not q or not ans:
            continue
        options = [str(x).strip() for x in (item.get("options") or []) if str(x).strip()]
        questions.append({
            "question": q,
            "type": str(item.get("type") or ("mcq" if options else "open")),
            "options": options,
            "answer": ans,
            "note": str(item.get("note") or "").strip(),
        })

    if not questions:
        return "I need at least one valid quiz question."
    if player is None or not hasattr(player, "show_quiz"):
        return "The interactive quiz panel is not available in this build."

    try:
        player.show_quiz(topic, questions, grade=_grade)
        player.write_log(f"QUIZ: {topic} — {len(questions)} question(s) ready")
        return f"The {topic} quiz is open with {len(questions)} question(s)."
    except Exception as exc:
        return f"Could not open the quiz: {exc}"
