import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from app.connectors.base import BaseConnector
from app.connectors.registry import ConnectorRegistry

SESSION_GAP = timedelta(minutes=10)


@ConnectorRegistry.register("koreader")
class KOReaderConnector(BaseConnector):
    source = "koreader"

    def __init__(self, db_path: str):
        self.db_path = db_path

    async def authenticate(self) -> None:
        if not Path(self.db_path).exists():
            raise FileNotFoundError(
                f"KOReader statistics database not found: {self.db_path}"
            )

    async def fetch_raw(
        self, since: datetime | None = None
    ) -> list[dict[str, Any]]:
        query = """
            SELECT
                b.title    AS title,
                p.page     AS page,
                p.start_time AS start_time,
                p.duration  AS duration
            FROM page_stat_data p
            JOIN book b ON b.id = p.id_book
        """
        params: tuple[Any, ...] = ()
        if since is not None:
            query += " WHERE p.start_time > ?"
            params = (int(since.timestamp()),)
        query += " ORDER BY p.start_time ASC"

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def normalize(self, raw: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return self._group_into_sessions(raw)

    async def run(
        self, since: datetime | None = None
    ) -> list[dict[str, Any]]:
        await self.authenticate()
        raw_records = await self.fetch_raw(since)
        return self.normalize(raw_records)

    def _group_into_sessions(
        self, rows: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        if not rows:
            return []

        sessions: list[dict[str, Any]] = []
        current: dict[str, Any] | None = None

        for row in rows:
            start = datetime.fromtimestamp(
                row["start_time"], tz=timezone.utc
            )
            duration = row["duration"] or 0
            title = row["title"] or "Unknown"

            if (
                current is None
                or current["title"] != title
                or start - current["_last_time"] > SESSION_GAP
            ):
                if current is not None:
                    sessions.append(self._build_session(current))
                current = {
                    "title": title,
                    "start": start,
                    "duration": duration,
                    "pages": [row["page"]],
                    "_last_time": start + timedelta(seconds=duration),
                }
            else:
                current["duration"] += duration
                current["pages"].append(row["page"])
                current["_last_time"] = start + timedelta(seconds=duration)

        if current is not None:
            sessions.append(self._build_session(current))

        return sessions

    def _build_session(self, s: dict[str, Any]) -> dict[str, Any]:
        duration_minutes = max(1, round(s["duration"] / 60))
        return {
            "record_type": "activity",
            "source": self.source,
            "category": "reading",
            "title": s["title"],
            "duration_minutes": duration_minutes,
            "occurred_at": s["start"],
            "metadata": {
                "pages_read": len(s["pages"]),
                "first_page": s["pages"][0],
                "last_page": s["pages"][-1],
            },
        }
