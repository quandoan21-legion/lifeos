from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.activity import Activity
from app.models.event import Event
from app.models.metric import Metric
from app.models.user import User
from app.schemas.event import (
    ActivityIn,
    ActivityOut,
    EventIn,
    EventOut,
    IngestRequest,
    IngestResponse,
    MetricIn,
    MetricOut,
)

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/ingest", response_model=IngestResponse)
async def ingest(
    request: IngestRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> IngestResponse:
    ingested = 0
    duplicates = 0

    for record in request.records:
        if isinstance(record, ActivityIn):
            existing = await db.execute(
                select(Activity).where(
                    and_(
                        Activity.user_id == current_user.id,
                        Activity.source == record.source,
                        Activity.category == record.category,
                        Activity.title == record.title,
                        Activity.occurred_at == record.occurred_at,
                    )
                )
            )
            if existing.scalar_one_or_none() is not None:
                duplicates += 1
                continue

            db.add(
                Activity(
                    user_id=current_user.id,
                    source=record.source,
                    category=record.category,
                    title=record.title,
                    duration_minutes=record.duration_minutes,
                    occurred_at=record.occurred_at,
                    metadata_=record.metadata,
                )
            )
            ingested += 1

        elif isinstance(record, EventIn):
            existing = await db.execute(
                select(Event).where(
                    and_(
                        Event.user_id == current_user.id,
                        Event.source == record.source,
                        Event.event_type == record.event_type,
                        Event.occurred_at == record.occurred_at,
                    )
                )
            )
            if existing.scalar_one_or_none() is not None:
                duplicates += 1
                continue

            db.add(
                Event(
                    user_id=current_user.id,
                    source=record.source,
                    event_type=record.event_type,
                    occurred_at=record.occurred_at,
                    metadata_=record.metadata,
                )
            )
            ingested += 1

        elif isinstance(record, MetricIn):
            existing = await db.execute(
                select(Metric).where(
                    and_(
                        Metric.user_id == current_user.id,
                        Metric.source == record.source,
                        Metric.metric_name == record.metric_name,
                        Metric.occurred_at == record.occurred_at,
                    )
                )
            )
            if existing.scalar_one_or_none() is not None:
                duplicates += 1
                continue

            db.add(
                Metric(
                    user_id=current_user.id,
                    source=record.source,
                    metric_name=record.metric_name,
                    metric_value=record.metric_value,
                    unit=record.unit,
                    occurred_at=record.occurred_at,
                    metadata_=record.metadata,
                )
            )
            ingested += 1

    await db.commit()
    return IngestResponse(ingested=ingested, duplicates=duplicates)


@router.get("/activities", response_model=list[ActivityOut])
async def list_activities(
    source: str | None = None,
    category: str | None = None,
    since: datetime | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ActivityOut]:
    stmt = select(Activity).where(Activity.user_id == current_user.id)
    if source is not None:
        stmt = stmt.where(Activity.source == source)
    if category is not None:
        stmt = stmt.where(Activity.category == category)
    if since is not None:
        stmt = stmt.where(Activity.occurred_at >= since)
    stmt = stmt.order_by(Activity.occurred_at.desc()).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/events", response_model=list[EventOut])
async def list_events(
    source: str | None = None,
    event_type: str | None = None,
    since: datetime | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[EventOut]:
    stmt = select(Event).where(Event.user_id == current_user.id)
    if source is not None:
        stmt = stmt.where(Event.source == source)
    if event_type is not None:
        stmt = stmt.where(Event.event_type == event_type)
    if since is not None:
        stmt = stmt.where(Event.occurred_at >= since)
    stmt = stmt.order_by(Event.occurred_at.desc()).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/metrics", response_model=list[MetricOut])
async def list_metrics(
    source: str | None = None,
    metric_name: str | None = None,
    since: datetime | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[MetricOut]:
    stmt = select(Metric).where(Metric.user_id == current_user.id)
    if source is not None:
        stmt = stmt.where(Metric.source == source)
    if metric_name is not None:
        stmt = stmt.where(Metric.metric_name == metric_name)
    if since is not None:
        stmt = stmt.where(Metric.occurred_at >= since)
    stmt = stmt.order_by(Metric.occurred_at.desc()).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())
