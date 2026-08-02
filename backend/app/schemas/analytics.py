from typing import Any

from pydantic import BaseModel, Field


class CategoryBreakdown(BaseModel):
    category: str
    hours: float
    task_count: int


class DashboardAnalytics(BaseModel):
    completion_rate: float = Field(description="Percentage of completed tasks")
    focus_hours: float
    study_hours: float
    average_sleep_hours: float | None = None
    missed_tasks: int
    consistency_score: float = Field(description="0-100 consistency score")
    total_tasks: int
    completed_tasks: int
    category_breakdown: list[CategoryBreakdown] = Field(default_factory=list)


class PeriodAnalytics(BaseModel):
    period: str
    start_date: str
    end_date: str
    completion_rate: float
    focus_hours: float
    study_hours: float
    missed_tasks: int
    consistency_score: float
    daily_breakdown: list[dict[str, Any]] = Field(default_factory=list)
    insights: list[str] | None = None
