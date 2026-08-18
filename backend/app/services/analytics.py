from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import and_, case, cast, func, select, Date, Integer
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import Activity
from app.models.event import Event
from app.models.metric import Metric


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _start_of_day(d: date) -> datetime:
    return datetime(d.year, d.month, d.day, tzinfo=timezone.utc)


def _end_of_day(d: date) -> datetime:
    return _start_of_day(d) + timedelta(days=1) - timedelta(seconds=1)


def _date_range(days: int) -> tuple[datetime, datetime]:
    end = _utc_now()
    start = end - timedelta(days=days)
    return start, end


async def get_activity_summary(
    db: AsyncSession,
    user_id: UUID,
    start: datetime,
    end: datetime,
    source: str | None = None,
    category: str | None = None,
) -> dict[str, Any]:
    """Aggregate activities in a date range: total duration, count, unique titles."""
    stmt = (
        select(
            func.coalesce(func.sum(Activity.duration_minutes), 0).label("total_duration"),
            func.count(Activity.id).label("total_count"),
            func.count(func.distinct(Activity.title)).label("unique_titles"),
        )
        .where(
            and_(
                Activity.user_id == user_id,
                Activity.occurred_at >= start,
                Activity.occurred_at <= end,
            )
        )
    )
    if source is not None:
        stmt = stmt.where(Activity.source == source)
    if category is not None:
        stmt = stmt.where(Activity.category == category)

    result = await db.execute(stmt)
    row = result.one()
    return {
        "total_duration_minutes": int(row.total_duration or 0),
        "total_count": int(row.total_count or 0),
        "unique_titles": int(row.unique_titles or 0),
    }


async def get_event_summary(
    db: AsyncSession,
    user_id: UUID,
    start: datetime,
    end: datetime,
    source: str | None = None,
    event_type: str | None = None,
) -> dict[str, Any]:
    """Aggregate events in a date range: total count."""
    stmt = (
        select(func.count(Event.id).label("total_count"))
        .where(
            and_(
                Event.user_id == user_id,
                Event.occurred_at >= start,
                Event.occurred_at <= end,
            )
        )
    )
    if source is not None:
        stmt = stmt.where(Event.source == source)
    if event_type is not None:
        stmt = stmt.where(Event.event_type == event_type)

    result = await db.execute(stmt)
    row = result.one()
    return {"total_count": int(row.total_count or 0)}


async def get_source_breakdown(
    db: AsyncSession,
    user_id: UUID,
    start: datetime,
    end: datetime,
) -> list[dict[str, Any]]:
    """Breakdown of activities by source within a date range."""
    stmt = (
        select(
            Activity.source,
            func.coalesce(func.sum(Activity.duration_minutes), 0).label("total_duration"),
            func.count(Activity.id).label("total_count"),
        )
        .where(
            and_(
                Activity.user_id == user_id,
                Activity.occurred_at >= start,
                Activity.occurred_at <= end,
            )
        )
        .group_by(Activity.source)
        .order_by(func.sum(Activity.duration_minutes).desc())
    )
    result = await db.execute(stmt)
    rows = result.all()

    total_duration = sum(int(r.total_duration or 0) for r in rows) or 1
    return [
        {
            "source": r.source,
            "total_duration_minutes": int(r.total_duration or 0),
            "total_count": int(r.total_count or 0),
            "percentage": round(int(r.total_duration or 0) / total_duration * 100, 1),
        }
        for r in rows
    ]


async def get_category_breakdown(
    db: AsyncSession,
    user_id: UUID,
    start: datetime,
    end: datetime,
    source: str | None = None,
) -> list[dict[str, Any]]:
    """Breakdown of activities by category within a date range."""
    stmt = (
        select(
            Activity.category,
            func.coalesce(func.sum(Activity.duration_minutes), 0).label("total_duration"),
            func.count(Activity.id).label("total_count"),
        )
        .where(
            and_(
                Activity.user_id == user_id,
                Activity.occurred_at >= start,
                Activity.occurred_at <= end,
            )
        )
        .group_by(Activity.category)
        .order_by(func.sum(Activity.duration_minutes).desc())
    )
    if source is not None:
        stmt = stmt.where(Activity.source == source)

    result = await db.execute(stmt)
    rows = result.all()

    total_duration = sum(int(r.total_duration or 0) for r in rows) or 1
    return [
        {
            "category": r.category,
            "total_duration_minutes": int(r.total_duration or 0),
            "total_count": int(r.total_count or 0),
            "percentage": round(int(r.total_duration or 0) / total_duration * 100, 1),
        }
        for r in rows
    ]


async def get_event_type_counts(
    db: AsyncSession,
    user_id: UUID,
    start: datetime,
    end: datetime,
    source: str | None = None,
) -> list[dict[str, Any]]:
    """Count events grouped by event_type within a date range."""
    stmt = (
        select(
            Event.event_type,
            func.count(Event.id).label("count"),
        )
        .where(
            and_(
                Event.user_id == user_id,
                Event.occurred_at >= start,
                Event.occurred_at <= end,
            )
        )
        .group_by(Event.event_type)
        .order_by(func.count(Event.id).desc())
    )
    if source is not None:
        stmt = stmt.where(Event.source == source)

    result = await db.execute(stmt)
    rows = result.all()

    total = sum(int(r.count or 0) for r in rows) or 1
    return [
        {
            "event_type": r.event_type,
            "count": int(r.count or 0),
            "percentage": round(int(r.count or 0) / total * 100, 1),
        }
        for r in rows
    ]


async def get_streaks(
    db: AsyncSession,
    user_id: UUID,
    source: str | None = None,
    category: str | None = None,
) -> list[dict[str, Any]]:
    """Calculate current and best streaks (consecutive days with activity).

    Groups by (source, category) and returns a streak entry per group.
    """
    stmt = (
        select(
            Activity.source,
            Activity.category,
            cast(Activity.occurred_at, Date).label("day"),
        )
        .where(Activity.user_id == user_id)
        .distinct()
        .order_by(Activity.source, Activity.category, "day")
    )
    if source is not None:
        stmt = stmt.where(Activity.source == source)
    if category is not None:
        stmt = stmt.where(Activity.category == category)

    result = await db.execute(stmt)
    rows = result.all()

    # Group days by (source, category)
    groups: dict[tuple[str, str], list[date]] = {}
    for r in rows:
        key = (r.source, r.category)
        groups.setdefault(key, []).append(r.day)

    today = _utc_now().date()
    streaks: list[dict[str, Any]] = []

    for (src, cat), days in groups.items():
        day_set = set(days)
        best = 0
        current = 0

        # Sort days ascending
        sorted_days = sorted(days)

        # Calculate best streak
        run = 1
        for i in range(1, len(sorted_days)):
            if (sorted_days[i] - sorted_days[i - 1]).days == 1:
                run += 1
            else:
                best = max(best, run)
                run = 1
        best = max(best, run) if sorted_days else 0

        # Calculate current streak (counting back from today)
        check_date = today
        if check_date not in day_set:
            # Allow today to be "not yet active" — check yesterday
            check_date = today - timedelta(days=1)

        while check_date in day_set:
            current += 1
            check_date -= timedelta(days=1)

        streaks.append({
            "source": src,
            "category": cat,
            "current_streak": current,
            "best_streak": best,
            "last_active_date": sorted_days[-1] if sorted_days else None,
        })

    # Sort by current streak descending
    streaks.sort(key=lambda s: s["current_streak"], reverse=True)
    return streaks


async def get_trend(
    db: AsyncSession,
    user_id: UUID,
    start: datetime,
    end: datetime,
    granularity: str = "daily",
    source: str | None = None,
    category: str | None = None,
) -> list[dict[str, Any]]:
    """Time-series of total activity duration per day/week/month."""
    day_col = cast(Activity.occurred_at, Date).label("day")

    stmt = (
        select(
            day_col,
            func.coalesce(func.sum(Activity.duration_minutes), 0).label("value"),
        )
        .where(
            and_(
                Activity.user_id == user_id,
                Activity.occurred_at >= start,
                Activity.occurred_at <= end,
            )
        )
        .group_by(day_col)
        .order_by(day_col)
    )
    if source is not None:
        stmt = stmt.where(Activity.source == source)
    if category is not None:
        stmt = stmt.where(Activity.category == category)

    result = await db.execute(stmt)
    rows = result.all()

    if granularity == "weekly":
        return _aggregate_weekly(rows)
    elif granularity == "monthly":
        return _aggregate_monthly(rows)
    else:
        return [
            {"date": r.day, "value": float(r.value or 0), "label": r.day.isoformat()}
            for r in rows
        ]


def _aggregate_weekly(rows: list[Any]) -> list[dict[str, Any]]:
    """Aggregate daily rows into weekly buckets (ISO week start = Monday)."""
    buckets: dict[date, float] = {}
    for r in rows:
        if r.day is None:
            continue
        monday = r.day - timedelta(days=r.day.weekday())
        buckets[monday] = buckets.get(monday, 0.0) + float(r.value or 0)

    return [
        {"date": d, "value": v, "label": f"W{d.isocalendar()[1]} {d.year}"}
        for d, v in sorted(buckets.items())
    ]


def _aggregate_monthly(rows: list[Any]) -> list[dict[str, Any]]:
    """Aggregate daily rows into monthly buckets."""
    buckets: dict[tuple[int, int], tuple[date, float]] = {}
    for r in rows:
        if r.day is None:
            continue
        key = (r.day.year, r.day.month)
        if key not in buckets:
            buckets[key] = (date(r.day.year, r.day.month, 1), 0.0)
        d, v = buckets[key]
        buckets[key] = (d, v + float(r.value or 0))

    return [
        {"date": d, "value": v, "label": d.strftime("%Y-%m")}
        for (d, v) in sorted(buckets.values(), key=lambda x: x[0])
    ]


async def get_metric_summary(
    db: AsyncSession,
    user_id: UUID,
    start: datetime,
    end: datetime,
    source: str | None = None,
    metric_name: str | None = None,
) -> list[dict[str, Any]]:
    """Aggregate metric values per metric_name within a date range."""
    stmt = (
        select(
            Metric.metric_name,
            Metric.unit,
            func.count(Metric.id).label("count"),
            func.coalesce(func.sum(Metric.metric_value), 0).label("sum_val"),
            func.coalesce(func.avg(Metric.metric_value), 0).label("avg_val"),
            func.coalesce(func.min(Metric.metric_value), 0).label("min_val"),
            func.coalesce(func.max(Metric.metric_value), 0).label("max_val"),
        )
        .where(
            and_(
                Metric.user_id == user_id,
                Metric.occurred_at >= start,
                Metric.occurred_at <= end,
            )
        )
        .group_by(Metric.metric_name, Metric.unit)
        .order_by(Metric.metric_name)
    )
    if source is not None:
        stmt = stmt.where(Metric.source == source)
    if metric_name is not None:
        stmt = stmt.where(Metric.metric_name == metric_name)

    result = await db.execute(stmt)
    rows = result.all()

    summaries: list[dict[str, Any]] = []
    for r in rows:
        count_val = int(r.count or 0)
        sum_val = float(r.sum_val or 0)
        # Get latest value for this metric
        latest_stmt = (
            select(Metric.metric_value, Metric.occurred_at)
            .where(
                and_(
                    Metric.user_id == user_id,
                    Metric.metric_name == r.metric_name,
                )
            )
            .order_by(Metric.occurred_at.desc())
            .limit(1)
        )
        if source is not None:
            latest_stmt = latest_stmt.where(Metric.source == source)
        latest_result = await db.execute(latest_stmt)
        latest_row = latest_result.one_or_none()

        summaries.append({
            "metric_name": r.metric_name,
            "unit": r.unit,
            "count": count_val,
            "sum_value": round(sum_val, 2),
            "avg_value": round(float(r.avg_val or 0), 2),
            "min_value": float(r.min_val or 0),
            "max_value": float(r.max_val or 0),
            "latest_value": float(latest_row.metric_value) if latest_row else 0.0,
            "latest_at": latest_row.occurred_at if latest_row else None,
        })

    return summaries


async def get_top_activities(
    db: AsyncSession,
    user_id: UUID,
    start: datetime,
    end: datetime,
    limit: int = 5,
    source: str | None = None,
    category: str | None = None,
) -> list[dict[str, Any]]:
    """Top activities by total duration within a date range."""
    stmt = (
        select(
            Activity.title,
            Activity.source,
            Activity.category,
            func.coalesce(func.sum(Activity.duration_minutes), 0).label("total_duration"),
            func.count(Activity.id).label("session_count"),
        )
        .where(
            and_(
                Activity.user_id == user_id,
                Activity.occurred_at >= start,
                Activity.occurred_at <= end,
            )
        )
        .group_by(Activity.title, Activity.source, Activity.category)
        .order_by(func.sum(Activity.duration_minutes).desc())
        .limit(limit)
    )
    if source is not None:
        stmt = stmt.where(Activity.source == source)
    if category is not None:
        stmt = stmt.where(Activity.category == category)

    result = await db.execute(stmt)
    rows = result.all()

    return [
        {
            "title": r.title,
            "source": r.source,
            "category": r.category,
            "total_duration_minutes": int(r.total_duration or 0),
            "session_count": int(r.session_count or 0),
        }
        for r in rows
    ]


async def get_recent_events(
    db: AsyncSession,
    user_id: UUID,
    limit: int = 10,
    source: str | None = None,
) -> list[dict[str, Any]]:
    """Most recent events (point-in-time records) for the user."""
    stmt = (
        select(Event)
        .where(Event.user_id == user_id)
        .order_by(Event.occurred_at.desc())
        .limit(limit)
    )
    if source is not None:
        stmt = stmt.where(Event.source == source)

    result = await db.execute(stmt)
    events = result.scalars().all()

    return [
        {
            "id": str(e.id),
            "source": e.source,
            "event_type": e.event_type,
            "occurred_at": e.occurred_at.isoformat() if e.occurred_at else None,
            "metadata": e.metadata_,
        }
        for e in events
    ]


async def get_daily_summaries(
    db: AsyncSession,
    user_id: UUID,
    start: datetime,
    end: datetime,
    source: str | None = None,
    category: str | None = None,
) -> list[dict[str, Any]]:
    """Per-day activity summaries within a date range."""
    day_col = cast(Activity.occurred_at, Date).label("day")
    stmt = (
        select(
            day_col,
            func.coalesce(func.sum(Activity.duration_minutes), 0).label("total_duration"),
            func.count(Activity.id).label("total_count"),
            func.count(func.distinct(Activity.title)).label("unique_titles"),
        )
        .where(
            and_(
                Activity.user_id == user_id,
                Activity.occurred_at >= start,
                Activity.occurred_at <= end,
            )
        )
        .group_by(day_col)
        .order_by(day_col)
    )
    if source is not None:
        stmt = stmt.where(Activity.source == source)
    if category is not None:
        stmt = stmt.where(Activity.category == category)

    result = await db.execute(stmt)
    rows = result.all()

    summaries: list[dict[str, Any]] = []
    for r in rows:
        day: date = r.day
        summaries.append({
            "period_start": day,
            "period_end": day,
            "total_duration_minutes": int(r.total_duration or 0),
            "total_count": int(r.total_count or 0),
            "unique_titles": int(r.unique_titles or 0),
        })
    return summaries


async def get_daily_event_counts(
    db: AsyncSession,
    user_id: UUID,
    start: datetime,
    end: datetime,
    source: str | None = None,
    event_type: str | None = None,
) -> list[dict[str, Any]]:
    """Per-day event count summaries within a date range."""
    day_col = cast(Event.occurred_at, Date).label("day")
    stmt = (
        select(
            day_col,
            func.count(Event.id).label("total_count"),
        )
        .where(
            and_(
                Event.user_id == user_id,
                Event.occurred_at >= start,
                Event.occurred_at <= end,
            )
        )
        .group_by(day_col)
        .order_by(day_col)
    )
    if source is not None:
        stmt = stmt.where(Event.source == source)
    if event_type is not None:
        stmt = stmt.where(Event.event_type == event_type)

    result = await db.execute(stmt)
    rows = result.all()

    summaries: list[dict[str, Any]] = []
    for r in rows:
        day: date = r.day
        summaries.append({
            "period_start": day,
            "period_end": day,
            "total_count": int(r.total_count or 0),
        })
    return summaries
