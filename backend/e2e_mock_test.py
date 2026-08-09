import asyncio
import uuid
from datetime import date, datetime, time
from unittest.mock import AsyncMock, MagicMock
from app.models import User, Task, TaskCategory, TaskPriority, TaskStatus, Schedule, ScheduleStatus, UserPreferences
from app.services.scheduling.engine import SchedulingEngine
from app.schemas.schedule import ScheduleGenerateRequest
from app.services.gamification.xp_service import GamificationService

async def run_e2e_test():
    print("=== Starting End-to-End Backend Test ===")
    
    # 1. Setup mock database session and repositories
    db_session = AsyncMock()
    user_id = uuid.uuid4()
    
    # Create a mock user
    user = User(
        id=user_id,
        email="test@example.com",
        wake_time=time(7, 0),
        sleep_time=time(23, 0),
    )
    
    # Create some mock pending tasks
    task1 = Task(
        id=uuid.uuid4(),
        user_id=user_id,
        title="Finish MVP Backend",
        duration=120,
        priority=TaskPriority.URGENT,
        category=TaskCategory.WORK,
        status=TaskStatus.PENDING,
        created_at=datetime.now()
    )
    task2 = Task(
        id=uuid.uuid4(),
        user_id=user_id,
        title="Workout",
        duration=45,
        priority=TaskPriority.HIGH,
        category=TaskCategory.HEALTH,
        status=TaskStatus.PENDING,
        created_at=datetime.now()
    )
    pending_tasks = [task1, task2]
    
    print(f"[1] Simulating Natural Language Task Extraction (Extracted {len(pending_tasks)} tasks).")
    
    # 2. Scheduling Pipeline
    print("[2] Running Scheduling Engine...")
    engine = SchedulingEngine(db_session)
    
    # Mock repositories
    engine.task_repo.get_pending_for_user = AsyncMock(return_value=pending_tasks)
    engine.prefs_repo.get_by_user = AsyncMock(return_value=None)
    
    # Mock Schedule saving
    def mock_create(schedule):
        schedule.id = uuid.uuid4()
        schedule.created_at = datetime.now()
        schedule.updated_at = datetime.now()
        schedule.priority = TaskPriority.MEDIUM
        schedule.category = TaskCategory.OTHER
        return schedule
    engine.schedule_repo.get_by_user_and_date = AsyncMock(return_value=None)
    engine.schedule_repo.create = AsyncMock(side_effect=mock_create)
    
    req = ScheduleGenerateRequest(target_date=date.today())
    schedule_response = await engine.generate(user, req)
    
    print(f"    - Generated Schedule with {len(schedule_response.generated_schedule['blocks'])} blocks.")
    for block in schedule_response.generated_schedule['blocks']:
        print(f"      * {block['start']} - {block['end']} | {block['title']} (Fixed: {block['is_fixed']})")
    
    # 3. Task Execution & Gamification
    print("[3] Simulating Task Completion & Gamification...")
    gamification = GamificationService(db_session)
    
    # Mock user stats
    mock_stats = MagicMock()
    mock_stats.xp = 0
    mock_stats.level = 1
    mock_stats.streak_days = 2
    mock_stats.last_active_date = date.today()
    gamification.get_user_stats = AsyncMock(return_value=mock_stats)
    
    # Complete task1
    task1.status = TaskStatus.COMPLETED
    xp_result = await gamification.award_task_completion_xp(user_id, task1)
    
    print(f"    - Completed Task: {task1.title}")
    print(f"    - Awarded XP: {xp_result['awarded_xp']}")
    print(f"    - New Total XP: {xp_result['new_total_xp']} (Level {xp_result['current_level']})")
    
    # 4. Analytics Generation
    print("[4] Generating Analytics Report...")
    from app.services.analytics.analytics_service import AnalyticsService
    from app.schemas.analytics import PeriodAnalytics
    
    analytics_svc = AnalyticsService(db_session)
    analytics_svc.get_weekly = AsyncMock(return_value=PeriodAnalytics(
        period="Weekly",
        start_date="2026-08-03",
        end_date="2026-08-09",
        completion_rate=85.5,
        focus_hours=12.0,
        study_hours=8.0,
        missed_tasks=2,
        consistency_score=90.0,
        daily_breakdown=[],
        insights=["Great job completing your MVP!"]
    ))
    
    report = await analytics_svc.generate_weekly_report_markdown(user_id)
    print("\n--- WEEKLY REPORT ---")
    print(report)
    print("---------------------\n")
    print("=== End-to-End Test Completed Successfully! ===")

if __name__ == "__main__":
    asyncio.run(run_e2e_test())
