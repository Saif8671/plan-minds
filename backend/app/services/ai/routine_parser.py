import json
import re
from datetime import time

from groq import AsyncGroq

from app.core.config import get_settings
from app.core.logger import get_logger
from app.schemas.schedule import (
    ParsedRoutine,
    ParseRoutineRequest,
)

logger = get_logger(__name__)
settings = get_settings()

SYSTEM_PROMPT = """You are a routine parsing assistant. Extract structured schedule information from natural language.

Return ONLY valid JSON with this exact schema:
{
  "wake_time": "HH:MM" or null,
  "sleep_time": "HH:MM" or null,
  "fixed_events": [{"title": "string", "start": "HH:MM", "end": "HH:MM", "category": "string or null"}],
  "flexible_tasks": [{"title": "string", "duration": minutes_int, "priority": "low|medium|high|urgent", "category": "string or null"}],
  "notes": "string or null"
}

Rules:
- Convert all times to 24-hour HH:MM format
- Duration is in minutes
- Infer reasonable defaults when ambiguous
- "every evening" for gym = flexible task, ~60 min, medium priority
- College/work with time range = fixed event
- "need X hours Y" = flexible task with duration X*60, title Y
- For "revision" or similar without duration, default to 60 minutes
"""


class AIRoutineParserService:
    def __init__(self):
        self.client = (
            AsyncGroq(
                api_key=settings.groq_api_key,
            )
            if settings.groq_api_key
            else None
        )

    async def parse_routine(self, data: ParseRoutineRequest) -> ParsedRoutine:
        # Try AI first if available, fall back to rules
        if self.client and settings.groq_api_key:
            try:
                return await self._parse_with_ai(data)
            except Exception as exc:
                logger.warning("AI parsing failed, falling back to rules: %s", exc)

        return self._parse_with_rules(data.routine_text)

    async def _parse_with_ai(self, data: ParseRoutineRequest) -> ParsedRoutine:
        max_retries = 2
        last_error = None

        for attempt in range(max_retries + 1):
            try:
                response = await self.client.chat.completions.create(
                    model=settings.groq_model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {
                            "role": "user",
                            "content": f"Timezone: {data.timezone}\n\nRoutine:\n{data.routine_text}",
                        },
                    ],
                    temperature=0.1,
                    response_format={"type": "json_object"},
                )
                content = response.choices[0].message.content
                parsed = json.loads(content)
                result = ParsedRoutine.model_validate(parsed)

                # Validate output quality
                if not result.fixed_events and not result.flexible_tasks:
                    if attempt < max_retries:
                        logger.info("AI returned empty result, retrying...")
                        continue
                    # Fall back to rules if AI keeps returning empty
                    return self._parse_with_rules(data.routine_text)

                return result
            except json.JSONDecodeError as exc:
                last_error = exc
                logger.warning(
                    "AI returned invalid JSON (attempt %d): %s", attempt + 1, exc
                )
            except Exception as exc:
                last_error = exc
                logger.warning("AI parsing error (attempt %d): %s", attempt + 1, exc)
                if attempt == max_retries:
                    break

        logger.warning("All AI attempts failed, falling back to rules: %s", last_error)
        return self._parse_with_rules(data.routine_text)

    def _parse_with_rules(self, text: str) -> ParsedRoutine:
        text_lower = text.lower()
        wake_time = self._extract_time(text_lower, ["wake up", "wake at", "i wake"])
        sleep_time = self._extract_time(
            text_lower, ["sleep at", "sleep by", "bed at", "sleep before"]
        )

        fixed_events = []
        flex_match = re.findall(
            r"(college|work|school|office|class|gym).*?(\d{1,2})(?::(\d{2}))?\s*(?:am|pm)?\s*(?:to|-)\s*(\d{1,2})(?::(\d{2}))?\s*(?:am|pm)?",
            text_lower,
        )
        for match in flex_match:
            title = match[0].title()
            start = self._to_time(int(match[1]), int(match[2] or 0))
            end = self._to_time(int(match[3]), int(match[4] or 0))
            fixed_events.append(
                {"title": title, "start": start, "end": end, "category": "work"}
            )

        flexible_tasks = []
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
            (
                r"need\s+revision",
                lambda m: ("Revision", 60),
            ),
        ]
        seen_titles = set()
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

        return ParsedRoutine(
            wake_time=wake_time,
            sleep_time=sleep_time,
            fixed_events=fixed_events,
            flexible_tasks=flexible_tasks,
        )

    def _extract_time(self, text: str, keywords: list[str]) -> time | None:
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

    def _to_time(self, hour: int, minute: int) -> time:
        if hour < 8:
            hour += 12
        return time(hour, minute)
