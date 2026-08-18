import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from app.connectors.base import BaseConnector
from app.connectors.registry import ConnectorRegistry


@ConnectorRegistry.register("koreader")
class KOReaderConnector(BaseConnector):
    source = "koreader"

    def __init__(self, db_path: str):
        self.db_path = db_path

    async def authenticate(self) -> None:
        if not Path(self.db_path).exists():
            raise FileNotFoundError(
                f"KOReader metadata not found: {self.db_path}"
            )

    async def fetch_raw(
        self, since: datetime | None = None
    ) -> list[dict[str, Any]]:
        query = "SELECT * FROM page_data_view"
        params: tuple[Any, ...] = ()
        if since is not None:
            query += " WHERE start_time > ?"
            params = (since.isoformat(),)
        query += " ORDER BY start_time ASC"

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def normalize(self, raw: dict[str, Any]) -> dict[str, Any]:
        duration_seconds = raw.get("duration") or 0
        duration_minutes = max(1, round(duration_seconds / 60))

        return {
            "record_type": "activity",
            "source": self.source,
            "category": "reading",
            "title": raw.get("title") or raw.get("book") or "Unknown",
            "duration_minutes": duration_minutes,
            "occurred_at": raw.get("start_time"),
            "metadata": {
                "author": raw.get("authors"),
                "pages_read": raw.get("page"),
                "total_pages": raw.get("total_pages"),
                "device": raw.get("device"),
                "book_path": raw.get("book"),
            },
        }
