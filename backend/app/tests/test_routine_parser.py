from datetime import time

import pytest

from app.schemas.schedule import ParseRoutineRequest
from app.services.ai.routine_parser import AIRoutineParserService


@pytest.fixture
def parser():
    p = AIRoutineParserService()
    p.client = None
    return p


@pytest.mark.asyncio
async def test_parse_routine_rules_wake_and_sleep(parser):
    text = "I wake up at 6. Sleep at 11."
    result = await parser.parse_routine(ParseRoutineRequest(routine_text=text))
    assert result.wake_time == time(6, 0)
    assert result.sleep_time == time(23, 0)


@pytest.mark.asyncio
async def test_parse_routine_rules_flexible_tasks(parser):
    text = "Need 2 hours of DSA. Need 1 hour of AI."
    result = await parser.parse_routine(ParseRoutineRequest(routine_text=text))
    titles = [t.title for t in result.flexible_tasks]
    assert "Dsa" in titles
    assert "Ai" in titles
    dsa = next(t for t in result.flexible_tasks if t.title == "Dsa")
    assert dsa.duration == 120


@pytest.mark.asyncio
async def test_parse_routine_rules_college(parser):
    text = "College from 9 to 4."
    result = await parser.parse_routine(ParseRoutineRequest(routine_text=text))
    assert len(result.fixed_events) >= 1
    assert result.fixed_events[0].title == "College"
