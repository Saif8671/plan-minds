"""Shared rule-based routine/schedule parser.

Used by both AIRoutineParserService (as fallback) and AIAnalyzeService
so that neither calls private methods on the other.
"""

import re
from datetime import time


def parse_with_rules(text: str) -> dict:
    """Parse a routine description using hand-crafted regex rules.

    Returns a dict compatible with ParsedRoutine and AIAnalyzeResponse schemas.
    """
    text_lower = text.lower()
    wake_time = _extract_time(text_lower, ["wake up", "wake at", "i wake"])
    sleep_time = _extract_time(
        text_lower, ["sleep at", "sleep by", "bed at", "sleep before"]
    )

    fixed_events: list[dict] = []
    flex_match = re.findall(
        r"(college|work|school|office|class|gym).*?(\d{1,2})(?::(\d{2}))?\s*(?:am|pm)?\s*(?:to|-)\s*(\d{1,2})(?::(\d{2}))?\s*(?:am|pm)?",
        text_lower,
    )
    for match in flex_match:
        title = match[0].title()
        start = _to_time(int(match[1]), int(match[2] or 0))
        end = _to_time(int(match[3]), int(match[4] or 0))
        fixed_events.append(
            {"title": title, "start": start, "end": end, "category": "work"}
        )

    flexible_tasks: list[dict] = []
    duration_patterns = [
        (
            r"need\s+(\d+)\s*hours?\s*(?:of\s+)?([a-zA-Z]+(?:\s+[a-zA-Z]+)?)",
            lambda m: (m.group(2).strip(), int(m.group(1)) * 60),
        ),
        (
            r"(\d+)\s*hours?\s*(?:of\s+)?([a-zA-Z]+(?:\s+[a-zA-Z]+)?)",
            lambda m: (m.group(2).strip(), int(m.group(1)) * 60),
        ),
        (
            r"([a-zA-Z]+)\s+every\s+(morning|evening|day)",
            lambda m: (m.group(1).strip(), 60),
        ),
        (r"study\s+(\d+)\s*hours?", lambda m: ("Study", int(m.group(1)) * 60)),
        (r"need\s+revision", lambda m: ("Revision", 60)),
    ]
    seen_titles: set[str] = set()
    for pattern, extractor in duration_patterns:
        for match in re.finditer(pattern, text_lower):
            title, duration = extractor(match)
            title = title.strip().title()
            if not title:
                continue
            if title.lower() not in seen_titles:
                seen_titles.add(title.lower())
                flexible_tasks.append(
                    {
                        "title": title,
                        "duration": duration,
                        "priority": "medium",
                        "category": "study",
                    }
                )

    # Handle standalone "Gym 6PM" pattern
    gym_match = re.search(
        r"gym\s+(?:at\s+)?(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", text_lower
    )
    if gym_match and "gym" not in [e["title"].lower() for e in fixed_events]:
        hour = int(gym_match.group(1))
        minute = int(gym_match.group(2) or 0)
        ampm = gym_match.group(3)
        if ampm == "pm" and hour < 12:
            hour += 12
        elif not ampm and hour < 12:
            hour += 12  # Assume PM for gym
        end_hour = hour + 1  # Default 1 hour
        if "gym" not in seen_titles:
            fixed_events.append(
                {
                    "title": "Gym",
                    "start": time(hour, minute),
                    "end": time(min(end_hour, 23), minute),
                    "category": "health",
                }
            )

    return {
        "wake_time": wake_time,
        "sleep_time": sleep_time,
        "fixed_events": fixed_events,
        "flexible_tasks": flexible_tasks,
        "notes": None,
    }


# ─── Internal helpers ─────────────────────────────────────────────────


def _extract_time(text: str, keywords: list[str]) -> time | None:
    is_sleep = any("sleep" in k or "bed" in k for k in keywords)
    for keyword in keywords:
        pattern = rf"{keyword}\s*(?:at\s*)?(\d{{1,2}})(?::(\d{{2}}))?\s*(am|pm)?"
        match = re.search(pattern, text)
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2) or 0)
            ampm = match.group(3)
            if ampm == "pm" and hour < 12:
                hour += 12
            elif ampm == "am" and hour == 12:
                hour = 0
            elif not ampm and is_sleep and 1 <= hour < 12:
                hour = hour + 12 if hour < 12 else hour
            return time(hour, minute)
    return None


def _to_time(hour: int, minute: int) -> time:
    if hour < 8:
        hour += 12
    return time(hour, minute)
