"""Integration tests — task lifecycle (create → list → start → complete → verify XP)."""

import pytest
import pytest_asyncio


@pytest.mark.asyncio
async def test_create_task(authenticated_client):
    resp = await authenticated_client.post(
        "/api/v1/tasks",
        json={"title": "Write tests", "duration": 60, "priority": "high"},
    )
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["title"] == "Write tests"
    assert data["priority"] == "high"
    assert data["status"] == "pending"
    return data["id"]


@pytest.mark.asyncio
async def test_list_tasks(authenticated_client):
    # Create a task first
    await authenticated_client.post(
        "/api/v1/tasks",
        json={"title": "Task Alpha", "duration": 30},
    )
    resp = await authenticated_client.get("/api/v1/tasks")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_task_lifecycle_start_complete(authenticated_client):
    # Create
    create_resp = await authenticated_client.post(
        "/api/v1/tasks",
        json={"title": "Morning Run", "duration": 45, "priority": "medium"},
    )
    assert create_resp.status_code == 201
    task_id = create_resp.json()["data"]["id"]

    # Start
    start_resp = await authenticated_client.post(f"/api/v1/tasks/{task_id}/start")
    assert start_resp.status_code == 200
    assert start_resp.json()["data"]["status"] == "in_progress"

    # Complete
    complete_resp = await authenticated_client.patch(f"/api/v1/tasks/{task_id}/complete")
    assert complete_resp.status_code == 200
    assert complete_resp.json()["data"]["status"] == "completed"
    assert complete_resp.json()["data"]["completed"] is True


@pytest.mark.asyncio
async def test_skip_task(authenticated_client):
    create_resp = await authenticated_client.post(
        "/api/v1/tasks",
        json={"title": "Skippable Task", "duration": 30},
    )
    task_id = create_resp.json()["data"]["id"]

    skip_resp = await authenticated_client.post(
        f"/api/v1/tasks/{task_id}/skip",
        json={"reason": "Not enough time today"},
    )
    assert skip_resp.status_code == 200
    assert skip_resp.json()["data"]["status"] == "skipped"


@pytest.mark.asyncio
async def test_update_task(authenticated_client):
    create_resp = await authenticated_client.post(
        "/api/v1/tasks",
        json={"title": "Initial Title", "duration": 60},
    )
    task_id = create_resp.json()["data"]["id"]

    patch_resp = await authenticated_client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"title": "Updated Title", "priority": "urgent"},
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["data"]["title"] == "Updated Title"
    assert patch_resp.json()["data"]["priority"] == "urgent"


@pytest.mark.asyncio
async def test_delete_task(authenticated_client):
    create_resp = await authenticated_client.post(
        "/api/v1/tasks",
        json={"title": "To Delete", "duration": 15},
    )
    task_id = create_resp.json()["data"]["id"]

    delete_resp = await authenticated_client.delete(f"/api/v1/tasks/{task_id}")
    assert delete_resp.status_code == 204

    # Verify gone
    get_resp = await authenticated_client.get(f"/api/v1/tasks/{task_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_filter_tasks_by_status(authenticated_client):
    # Create one completed task
    cr = await authenticated_client.post("/api/v1/tasks", json={"title": "Done", "duration": 30})
    task_id = cr.json()["data"]["id"]
    await authenticated_client.patch(f"/api/v1/tasks/{task_id}/complete")

    resp = await authenticated_client.get("/api/v1/tasks?status=completed")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert all(t["status"] == "completed" for t in data["items"])
