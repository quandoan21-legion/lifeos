import re
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from app.connectors.base import BaseConnector
from app.connectors.registry import ConnectorRegistry

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?\n)---\s*\n", re.DOTALL)
TEMPLATE_PLACEHOLDER = "{{"


@ConnectorRegistry.register("obsidian")
class ObsidianConnector(BaseConnector):
    source = "obsidian"

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self._template_folder = "Templates"

    async def authenticate(self) -> None:
        if not self.vault_path.exists():
            raise FileNotFoundError(
                f"Obsidian vault not found: {self.vault_path}"
            )

    async def fetch_raw(
        self, since: datetime | None = None
    ) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        for md_file in self.vault_path.rglob("*.md"):
            if self._template_folder in md_file.parts:
                continue

            mtime = datetime.fromtimestamp(
                md_file.stat().st_mtime, tz=timezone.utc
            )
            if since is not None and mtime < since:
                continue

            content = md_file.read_text(encoding="utf-8")
            frontmatter = self._parse_frontmatter(content)
            if frontmatter is None:
                continue
            if any(
                isinstance(v, str) and TEMPLATE_PLACEHOLDER in v
                for v in frontmatter.values()
            ):
                continue

            frontmatter["_file_path"] = str(
                md_file.relative_to(self.vault_path)
            )
            frontmatter["_mtime"] = mtime
            records.append(frontmatter)

        return records

    def normalize(self, raw: list[dict[str, Any]]) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for fm in raw:
            record = self._convert(fm)
            if record is not None:
                results.append(record)
        return results

    def _parse_frontmatter(self, content: str) -> dict[str, Any] | None:
        match = FRONTMATTER_RE.match(content)
        if match is None:
            return None
        try:
            data = yaml.safe_load(match.group(1))
            if not isinstance(data, dict):
                return None
            return data
        except yaml.YAMLError:
            return None

    def _convert(self, fm: dict[str, Any]) -> dict[str, Any] | None:
        record_type = fm.get("type", "")

        if record_type == "activity":
            return self._convert_activity(fm)
        elif record_type == "reading-session":
            return self._convert_reading(fm)
        elif record_type == "coding-session":
            return self._convert_coding(fm)
        return None

    def _convert_activity(self, fm: dict[str, Any]) -> dict[str, Any] | None:
        occurred_at = self._parse_datetime(
            fm.get("occurred_at") or fm.get("date")
        )
        if occurred_at is None:
            return None

        return {
            "record_type": "activity",
            "source": fm.get("source", "manual"),
            "category": fm.get("category", "general"),
            "title": fm.get("title", "Untitled"),
            "duration_minutes": int(fm.get("duration_minutes", 0) or 0),
            "occurred_at": occurred_at,
            "metadata": {
                "file_path": fm.get("_file_path"),
                "tags": fm.get("tags", []),
            },
        }

    def _convert_reading(self, fm: dict[str, Any]) -> dict[str, Any] | None:
        occurred_at = self._parse_datetime(
            fm.get("occurred_at") or fm.get("date")
        )
        if occurred_at is None:
            return None

        duration_seconds = int(fm.get("duration_seconds", 0) or 0)
        duration_minutes = max(1, round(duration_seconds / 60))

        return {
            "record_type": "activity",
            "source": fm.get("source", "koreader"),
            "category": "reading",
            "title": fm.get("title", "Unknown"),
            "duration_minutes": duration_minutes,
            "occurred_at": occurred_at,
            "metadata": {
                "file_path": fm.get("_file_path"),
                "author": fm.get("author"),
                "pages_read": fm.get("pages_read"),
                "total_pages": fm.get("total_pages"),
                "device": fm.get("device"),
                "tags": fm.get("tags", []),
            },
        }

    def _convert_coding(self, fm: dict[str, Any]) -> dict[str, Any] | None:
        occurred_at = self._parse_datetime(
            fm.get("occurred_at") or fm.get("date")
        )
        if occurred_at is None:
            return None

        return {
            "record_type": "event",
            "source": fm.get("source", "github"),
            "event_type": fm.get("event_type", "other"),
            "occurred_at": occurred_at,
            "metadata": {
                "file_path": fm.get("_file_path"),
                "repo": fm.get("repo"),
                "action": fm.get("action"),
                "size": fm.get("size"),
                "ref": fm.get("ref"),
                "tags": fm.get("tags", []),
            },
        }

    @staticmethod
    def _parse_datetime(value: Any) -> datetime | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
        if isinstance(value, date):
            return datetime.combine(value, datetime.min.time(), tzinfo=timezone.utc)
        if isinstance(value, str):
            try:
                dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
                return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
            except ValueError:
                return None
        return None
