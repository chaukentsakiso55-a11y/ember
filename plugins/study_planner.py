"""Simple study-session planner displayed in the HUD content panel."""
from __future__ import annotations

PLUGIN = {
    "name": "study_planner",
    "description": (
        "Create and display a short study-session plan from a subject, goal, available minutes, and task list. "
        "Use when the user asks for a study plan for the current session, not for calendar scheduling."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "subject": {"type": "STRING", "description": "Subject or topic."},
            "goal": {"type": "STRING", "description": "What the user should achieve in this session."},
            "minutes": {"type": "INTEGER", "description": "Total available minutes."},
            "tasks": {"type": "ARRAY", "items": {"type": "STRING"}, "description": "Ordered study tasks."},
        },
        "required": ["subject", "goal", "minutes", "tasks"],
    },
    "behavior": "NON_BLOCKING",
    "scheduling": "SILENT",
}


def run(parameters: dict, player=None, session_memory=None) -> str:
    subject = str(parameters.get("subject") or "Study").strip()
    goal = str(parameters.get("goal") or "").strip()
    try:
        minutes = max(10, min(360, int(parameters.get("minutes") or 30)))
    except Exception:
        minutes = 30
    tasks = [str(x).strip() for x in (parameters.get("tasks") or []) if str(x).strip()][:12]
    if not tasks:
        tasks = ["Review the key ideas", "Practice a few questions", "Check mistakes and summarise"]

    # Allocate most time evenly, reserving a brief final review.
    review = max(3, min(10, minutes // 6))
    work = max(1, minutes - review)
    base = max(1, work // len(tasks))
    remaining = work
    lines = [f"Goal: {goal or 'Make clear progress on the topic'}", f"Total: {minutes} min", ""]
    for i, task in enumerate(tasks, 1):
        slot = remaining if i == len(tasks) else min(base, remaining)
        remaining -= slot
        lines.append(f"{i}. {task} — {slot} min")
    lines.append(f"\nFinal review — {review} min")
    text = "\n".join(lines)

    if player and hasattr(player, "show_content"):
        try:
            player.show_content(f"Study plan · {subject}", text)
            player.write_log(f"STUDY PLAN: {subject} — {minutes} min")
        except Exception:
            pass
    return f"I prepared a {minutes}-minute study plan for {subject}."
