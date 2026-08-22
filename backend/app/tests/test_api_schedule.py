import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_generate_schedule(authenticated_client: AsyncClient):
    # First create a task to be scheduled
    resp = await authenticated_client.post(
        "/api/v1/tasks",
        json={"title": "Test AI Task", "duration": 60, "priority": "high"},
    )
    assert resp.status_code == 201

    # Call /generate
    gen_resp = await authenticated_client.post(
        "/api/v1/schedules/generate", json={"target_date": "2026-09-01"}
    )
    assert gen_resp.status_code == 200
    data = gen_resp.json()["data"]

    assert data["status"] == "active"
    assert "generated_schedule" in data
    assert "blocks" in data["generated_schedule"]

    blocks = data["generated_schedule"]["blocks"]
    # Check if "Test AI Task" is in the generated schedule blocks
    titles = [b["title"] for b in blocks]
    assert "Test AI Task" in titles


@pytest.mark.asyncio
async def test_regenerate_schedule(authenticated_client: AsyncClient):
    # Call /regenerate
    gen_resp = await authenticated_client.post(
        "/api/v1/schedules/regenerate",
        json={"target_date": "2026-09-01", "skipped_task_ids": []},
    )
    assert gen_resp.status_code == 200
    data = gen_resp.json()["data"]

    assert data["status"] == "active"
    assert "generated_schedule" in data


@pytest.mark.asyncio
async def test_generate_multi_day(authenticated_client: AsyncClient):
    gen_resp = await authenticated_client.post(
        "/api/v1/schedules/generate/multi-day",
        json={"start_date": "2026-09-01", "days": 3},
    )
    assert gen_resp.status_code == 200
    data = gen_resp.json()["data"]

    assert isinstance(data, list)
    assert len(data) == 3
    for day in data:
        assert "generated_schedule" in day
