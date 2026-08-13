"""AI-powered routine parser with few-shot prompting, retry + exponential backoff,
and a rule-based fallback for when the AI is unavailable or returns invalid JSON.
"""

import asyncio
import json

from groq import AsyncGroq

from app.core.config import get_settings
from app.core.logger import get_logger
from app.schemas.schedule import ParsedRoutine, ParseRoutineRequest
from app.services.ai.rule_parser import parse_with_rules

logger = get_logger(__name__)
settings = get_settings()

# ─── Few-shot system prompt ─────────────────────────────────────────────

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

--- EXAMPLES ---

Input: "I wake up at 7am, college from 9 to 1pm, need 2 hours study, gym every evening, sleep at 11pm"
Output:
{
  "wake_time": "07:00",
  "sleep_time": "23:00",
  "fixed_events": [{"title": "College", "start": "09:00", "end": "13:00", "category": "work"}],
  "flexible_tasks": [
    {"title": "Study", "duration": 120, "priority": "high", "category": "study"},
    {"title": "Gym", "duration": 60, "priority": "medium", "category": "health"}
  ],
  "notes": null
}

Input: "Work 9-5, morning run, lunch break, need 1 hour revision before bed at midnight"
Output:
{
  "wake_time": null,
  "sleep_time": "00:00",
  "fixed_events": [{"title": "Work", "start": "09:00", "end": "17:00", "category": "work"}],
  "flexible_tasks": [
    {"title": "Morning Run", "duration": 30, "priority": "medium", "category": "health"},
    {"title": "Revision", "duration": 60, "priority": "high", "category": "study"}
  ],
  "notes": "Lunch break is flexible"
}

Input: "Gym at 6pm, study 3 hours for exams, wake at 6am, sleep 10pm"
Output:
{
  "wake_time": "06:00",
  "sleep_time": "22:00",
  "fixed_events": [{"title": "Gym", "start": "18:00", "end": "19:00", "category": "health"}],
  "flexible_tasks": [
    {"title": "Study", "duration": 180, "priority": "urgent", "category": "study"}
  ],
  "notes": null
}
"""

_MAX_RETRIES = 3
_RETRY_DELAYS = [0.5, 1.0, 2.0]  # seconds


class AIRoutineParserService:
    def __init__(self):
        self.client = (
            AsyncGroq(api_key=settings.groq_api_key) if settings.groq_api_key else None
        )

    async def parse_routine(self, data: ParseRoutineRequest) -> ParsedRoutine:
        """Parse a routine description, using AI with rule-based fallback."""
        if self.client and settings.groq_api_key:
            try:
                return await self._parse_with_ai(data)
            except Exception as exc:
                logger.warning("AI parsing failed, falling back to rules: %s", exc)
        return self._fallback(data.routine_text)

    # ─── AI path ───────────────────────────────────────────────────────

    async def _parse_with_ai(self, data: ParseRoutineRequest) -> ParsedRoutine:
        last_error: Exception | None = None

        for attempt in range(_MAX_RETRIES):
            try:
                response = await self.client.chat.completions.create(  # type: ignore[union-attr]
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
                    max_tokens=800,
                )
                content = response.choices[0].message.content or ""
                parsed_dict = json.loads(content)
                result = ParsedRoutine.model_validate(parsed_dict)

                # Quality gate: retry if AI returned nothing useful
                if not result.fixed_events and not result.flexible_tasks:
                    logger.info(
                        "AI returned empty result (attempt %d/%d), retrying…",
                        attempt + 1,
                        _MAX_RETRIES,
                    )
                    if attempt < _MAX_RETRIES - 1:
                        await asyncio.sleep(_RETRY_DELAYS[attempt])
                        continue
                    return self._fallback(data.routine_text)

                return result

            except json.JSONDecodeError as exc:
                last_error = exc
                logger.warning(
                    "AI returned invalid JSON (attempt %d/%d): %s",
                    attempt + 1,
                    _MAX_RETRIES,
                    exc,
                )
                # Attempt partial recovery from truncated/malformed JSON
                recovered = self._try_partial_recovery(content if "content" in dir() else "")
                if recovered:
                    return recovered

            except Exception as exc:
                last_error = exc
                logger.warning(
                    "AI parsing error (attempt %d/%d): %s", attempt + 1, _MAX_RETRIES, exc
                )

            if attempt < _MAX_RETRIES - 1:
                await asyncio.sleep(_RETRY_DELAYS[attempt])

        logger.warning("All AI attempts failed, using rule fallback: %s", last_error)
        return self._fallback(data.routine_text)

    # ─── Partial recovery ──────────────────────────────────────────────

    def _try_partial_recovery(self, raw: str) -> ParsedRoutine | None:
        """Try to extract valid JSON from a truncated or slightly malformed response."""
        import re

        # Find the first { ... } block
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            return None
        try:
            partial = json.loads(match.group())
            return ParsedRoutine.model_validate(partial)
        except Exception:
            return None

    # ─── Rule fallback ─────────────────────────────────────────────────

    def _fallback(self, text: str) -> ParsedRoutine:
        result = parse_with_rules(text)
        if not result.get("notes"):
            result["notes"] = "Parsed using rule-based fallback engine."
        else:
            result["notes"] += " (Parsed using rule-based fallback engine)"
        return ParsedRoutine.model_validate(result)
