from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PeriodSummary(BaseModel):
    """Aggregated totals for a single period (day/week/month)."""

    period_start: date
    period_end: date
    total_duration_minutes: int = 0
    total_count: int = 0
    unique_titles: int = 0


class SourceBreakdown(BaseModel):
    """Breakdown by source within a period."""

    source: str
    total_duration_minutes: int = 0
    total_count: int = 0
    percentage: float = 0.0


class CategoryBreakdown(BaseModel):
    """Breakdown by category within a period (activities only)."""

    category: str
    total_duration_minutes: int = 0
    total_count: int = 0
    percentage: float = 0.0


class StreakInfo(BaseModel):
    """Current and best streak for a given activity source+category."""

    source: str
    category: str | None = None
    current_streak: int = 0
    best_streak: int = 0
    last_active_date: date | None = None


class TrendPoint(BaseModel):
    """A single data point in a trend series."""

    date: date
    value: float
    label: str | None = None


class TrendResponse(BaseModel):
    """Time-series trend for activities or events."""

    metric: str
    granularity: str
    points: list[TrendPoint]


class EventTypeCount(BaseModel):
    """Count of events grouped by event_type."""

    event_type: str
    count: int
    percentage: float = 0.0


class MetricSummary(BaseModel):
    """Aggregated metric values for a period."""

    metric_name: str
    unit: str
    count: int = 0
    sum_value: float = 0.0
    avg_value: float = 0.0
    min_value: float = 0.0
    max_value: float = 0.0
    latest_value: float = 0.0
    latest_at: datetime | None = None


class DashboardResponse(BaseModel):
    """Combined dashboard: period summaries, streaks, top items, recent activity."""

    period_start: date
    period_end: date

    activities: list[PeriodSummary] = Field(default_factory=list)
    events: list[PeriodSummary] = Field(default_factory=list)
    metrics: list[MetricSummary] = Field(default_factory=list)

    source_breakdown: list[SourceBreakdown] = Field(default_factory=list)
    category_breakdown: list[CategoryBreakdown] = Field(default_factory=list)
    event_type_counts: list[EventTypeCount] = Field(default_factory=list)

    streaks: list[StreakInfo] = Field(default_factory=list)

    top_activities: list[dict[str, Any]] = Field(default_factory=list)
    recent_events: list[dict[str, Any]] = Field(default_factory=list)
