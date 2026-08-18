from datetime import datetime
from decimal import Decimal
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ActivityIn(BaseModel):
    record_type: Literal["activity"] = "activity"
    source: str = Field(min_length=1, max_length=50)
    category: str = Field(min_length=1, max_length=50)
    title: str = Field(min_length=1, max_length=255)
    duration_minutes: int = Field(ge=0)
    occurred_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class EventIn(BaseModel):
    record_type: Literal["event"] = "event"
    source: str = Field(min_length=1, max_length=50)
    event_type: str = Field(min_length=1, max_length=50)
    occurred_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class MetricIn(BaseModel):
    record_type: Literal["metric"] = "metric"
    source: str = Field(min_length=1, max_length=50)
    metric_name: str = Field(min_length=1, max_length=100)
    metric_value: Decimal
    unit: str = Field(min_length=1, max_length=20)
    occurred_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


RecordIn = ActivityIn | EventIn | MetricIn


class IngestRequest(BaseModel):
    records: list[RecordIn] = Field(min_length=1, max_length=500)


class IngestResponse(BaseModel):
    ingested: int
    duplicates: int


class ActivityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    source: str
    category: str
    title: str
    duration_minutes: int
    occurred_at: datetime
    metadata: dict[str, Any]
    created_at: datetime


class EventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    source: str
    event_type: str
    occurred_at: datetime
    metadata: dict[str, Any]
    created_at: datetime


class MetricOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    source: str
    metric_name: str
    metric_value: Decimal
    unit: str
    occurred_at: datetime
    metadata: dict[str, Any]
    created_at: datetime
