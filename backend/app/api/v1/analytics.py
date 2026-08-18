from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.analytics import (
    CategoryBreakdown,
    DashboardResponse,
    EventTypeCount,
    MetricSummary,
    PeriodSummary,
    SourceBreakdown,
    StreakInfo,
    TrendPoint,
    TrendResponse,
)
from app.services import analytics

router = APIRouter(prefix="/analytics", tags=["analytics"])


def _parse_range(
    days: int, since: datetime | None, until: datetime | None
) -> tuple[datetime, datetime]:
    """Resolve a date range from `days` or explicit `since`/`until`."""
    end = until or datetime.now(timezone.utc)
    if since is not None:
        start = since
    else:
        start = end.fromtimestamp(end.timestamp() - days * 86400, tz=timezone.utc)
    return start, end


@router.get("/summary", response_model=list[PeriodSummary])
async def activity_summary(
    days: int = Query(default=7, ge=1, le=365),
    source: str | None = None,
    category: str | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[PeriodSummary]:
    """Daily activity summaries (total duration, count, unique titles) for the given range."""
    start, end = _parse_range(days, since, until)
    summaries = await analytics.get_daily_summaries(
        db, current_user.id, start, end, source=source, category=category
    )
    return [PeriodSummary(**s) for s in summaries]


@router.get("/events/summary", response_model=list[PeriodSummary])
async def event_summary(
    days: int = Query(default=7, ge=1, le=365),
    source: str | None = None,
    event_type: str | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[PeriodSummary]:
    """Daily event count summaries for the given range."""
    start, end = _parse_range(days, since, until)
    summaries = await analytics.get_daily_event_counts(
        db, current_user.id, start, end, source=source, event_type=event_type
    )
    return [PeriodSummary(**s) for s in summaries]


@router.get("/streaks", response_model=list[StreakInfo])
async def streaks(
    source: str | None = None,
    category: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[StreakInfo]:
    """Current and best streaks (consecutive days with activity), grouped by source+category."""
    result = await analytics.get_streaks(
        db, current_user.id, source=source, category=category
    )
    return [StreakInfo(**s) for s in result]


@router.get("/trend", response_model=TrendResponse)
async def trend(
    days: int = Query(default=30, ge=1, le=365),
    granularity: str = Query(default="daily", pattern="^(daily|weekly|monthly)$"),
    source: str | None = None,
    category: str | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TrendResponse:
    """Time-series of total activity duration per day/week/month."""
    start, end = _parse_range(days, since, until)
    points = await analytics.get_trend(
        db, current_user.id, start, end, granularity=granularity,
        source=source, category=category,
    )
    return TrendResponse(
        metric="duration_minutes",
        granularity=granularity,
        points=[TrendPoint(**p) for p in points],
    )


@router.get("/sources", response_model=list[SourceBreakdown])
async def source_breakdown(
    days: int = Query(default=7, ge=1, le=365),
    since: datetime | None = None,
    until: datetime | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[SourceBreakdown]:
    """Breakdown of activity duration by source within the date range."""
    start, end = _parse_range(days, since, until)
    result = await analytics.get_source_breakdown(db, current_user.id, start, end)
    return [SourceBreakdown(**r) for r in result]


@router.get("/categories", response_model=list[CategoryBreakdown])
async def category_breakdown(
    days: int = Query(default=7, ge=1, le=365),
    source: str | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[CategoryBreakdown]:
    """Breakdown of activity duration by category within the date range."""
    start, end = _parse_range(days, since, until)
    result = await analytics.get_category_breakdown(
        db, current_user.id, start, end, source=source
    )
    return [CategoryBreakdown(**r) for r in result]


@router.get("/event-types", response_model=list[EventTypeCount])
async def event_type_counts(
    days: int = Query(default=7, ge=1, le=365),
    source: str | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[EventTypeCount]:
    """Count of events grouped by event_type within the date range."""
    start, end = _parse_range(days, since, until)
    result = await analytics.get_event_type_counts(
        db, current_user.id, start, end, source=source
    )
    return [EventTypeCount(**r) for r in result]


@router.get("/metrics", response_model=list[MetricSummary])
async def metric_summary(
    days: int = Query(default=30, ge=1, le=365),
    source: str | None = None,
    metric_name: str | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[MetricSummary]:
    """Aggregated metric values (sum, avg, min, max, latest) per metric_name."""
    start, end = _parse_range(days, since, until)
    result = await analytics.get_metric_summary(
        db, current_user.id, start, end, source=source, metric_name=metric_name
    )
    return [MetricSummary(**r) for r in result]


@router.get("/dashboard", response_model=DashboardResponse)
async def dashboard(
    days: int = Query(default=7, ge=1, le=365),
    source: str | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DashboardResponse:
    """Combined dashboard: daily summaries, breakdowns, streaks, top activities, recent events."""
    start, end = _parse_range(days, since, until)

    activities = await analytics.get_daily_summaries(
        db, current_user.id, start, end, source=source
    )
    events = await analytics.get_daily_event_counts(
        db, current_user.id, start, end, source=source
    )
    metrics = await analytics.get_metric_summary(
        db, current_user.id, start, end, source=source
    )
    source_bd = await analytics.get_source_breakdown(db, current_user.id, start, end)
    category_bd = await analytics.get_category_breakdown(
        db, current_user.id, start, end, source=source
    )
    event_types = await analytics.get_event_type_counts(
        db, current_user.id, start, end, source=source
    )
    streak_data = await analytics.get_streaks(db, current_user.id)
    top_acts = await analytics.get_top_activities(
        db, current_user.id, start, end, limit=5, source=source
    )
    recent = await analytics.get_recent_events(
        db, current_user.id, limit=10, source=source
    )

    return DashboardResponse(
        period_start=start.date(),
        period_end=end.date(),
        activities=[PeriodSummary(**s) for s in activities],
        events=[PeriodSummary(**s) for s in events],
        metrics=[MetricSummary(**m) for m in metrics],
        source_breakdown=[SourceBreakdown(**s) for s in source_bd],
        category_breakdown=[CategoryBreakdown(**c) for c in category_bd],
        event_type_counts=[EventTypeCount(**e) for e in event_types],
        streaks=[StreakInfo(**s) for s in streak_data],
        top_activities=top_acts,
        recent_events=recent,
    )
