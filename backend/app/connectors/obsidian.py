import re
from datetime import date, datetime, timezone
from pathlib import Path
from decimal import Decimal
from typing import Any

import yaml

from app.connectors.base import BaseConnector
from app.connectors.registry import ConnectorRegistry

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?\n)---\s*\n", re.DOTALL)
TEMPLATE_PLACEHOLDER = "{{"
TABLE_ROW_RE = re.compile(r"^\|(.+)\|\s*$")
ENERGY_MOOD_RE = re.compile(
    r"^-\s*(?:Energy|Mood|Sleep)\s*(?:\([^)]*\))?\s*:\s*(.+?)\s*$",
    re.IGNORECASE,
)


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

            body = FRONTMATTER_RE.sub("", content)
            frontmatter["_file_path"] = str(
                md_file.relative_to(self.vault_path)
            )
            frontmatter["_mtime"] = mtime
            frontmatter["_body"] = body
            records.append(frontmatter)

        return records

    def normalize(self, raw: list[dict[str, Any]]) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for fm in raw:
            records = self._convert(fm)
            if records is None:
                continue
            if isinstance(records, list):
                results.extend(records)
            else:
                results.append(records)
        return results

    def parse_file(self, file_path: Path) -> list[dict[str, Any]]:
        """Parse a single markdown file and return normalized records.

        Used by the Syncthing watcher to process one file at a time
        as soon as Syncthing reports it has finished syncing.
        """
        try:
            content = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return []

        if self._template_folder in file_path.parts:
            return []

        frontmatter = self._parse_frontmatter(content)
        if frontmatter is None:
            return []
        if any(
            isinstance(v, str) and TEMPLATE_PLACEHOLDER in v
            for v in frontmatter.values()
        ):
            return []

        body = FRONTMATTER_RE.sub("", content)
        frontmatter["_file_path"] = str(file_path.relative_to(self.vault_path))
        frontmatter["_mtime"] = datetime.fromtimestamp(
            file_path.stat().st_mtime, tz=timezone.utc
        )
        frontmatter["_body"] = body

        records = self._convert(frontmatter)
        if records is None:
            return []
        if isinstance(records, list):
            return records
        return [records]

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

    def _convert(
        self, fm: dict[str, Any]
    ) -> dict[str, Any] | list[dict[str, Any]] | None:
        record_type = fm.get("type", "")

        if record_type == "activity":
            return self._convert_activity(fm)
        elif record_type == "reading-session":
            return self._convert_reading(fm)
        elif record_type == "coding-session":
            return self._convert_coding(fm)
        elif record_type == "daily":
            return self._convert_daily(fm)
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

    def _convert_daily(self, fm: dict[str, Any]) -> list[dict[str, Any]]:
        occurred_at = self._parse_datetime(fm.get("date"))
        if occurred_at is None:
            return []

        body: str = fm.get("_body", "")
        file_path = fm.get("_file_path")
        tags = fm.get("tags", [])
        records: list[dict[str, Any]] = []

        records.extend(
            self._parse_reading_table(body, occurred_at, file_path, tags)
        )
        records.extend(
            self._parse_coding_table(body, occurred_at, file_path, tags)
        )
        records.extend(
            self._parse_other_activities_table(
                body, occurred_at, file_path, tags
            )
        )
        records.extend(
            self._parse_metrics_table(body, occurred_at, file_path, tags)
        )
        records.extend(
            self._parse_energy_mood(body, occurred_at, file_path, tags)
        )

        return records

    def _parse_reading_table(
        self,
        body: str,
        occurred_at: datetime,
        file_path: str | None,
        tags: list[Any],
    ) -> list[dict[str, Any]]:
        rows = self._extract_table(body, "Reading", ["Book", "Pages", "Duration"])
        records: list[dict[str, Any]] = []
        for row in rows:
            title = row.get("book", "").strip()
            if not title:
                continue
            pages = self._parse_int(row.get("pages"))
            duration_minutes = self._parse_duration(row.get("duration", ""))
            records.append({
                "record_type": "activity",
                "source": "koreader",
                "category": "reading",
                "title": title,
                "duration_minutes": duration_minutes,
                "occurred_at": occurred_at,
                "metadata": {
                    "file_path": file_path,
                    "pages_read": pages,
                    "notes": row.get("notes", "").strip() or None,
                    "tags": tags,
                },
            })
        return records

    def _parse_coding_table(
        self,
        body: str,
        occurred_at: datetime,
        file_path: str | None,
        tags: list[Any],
    ) -> list[dict[str, Any]]:
        rows = self._extract_table(body, "Coding", ["Repo", "Type", "Count"])
        records: list[dict[str, Any]] = []
        for row in rows:
            repo = row.get("repo", "").strip()
            if not repo:
                continue
            event_type = row.get("type", "").strip() or "other"
            count = self._parse_int(row.get("count"))
            records.append({
                "record_type": "event",
                "source": "github",
                "event_type": event_type,
                "occurred_at": occurred_at,
                "metadata": {
                    "file_path": file_path,
                    "repo": repo,
                    "count": count,
                    "notes": row.get("notes", "").strip() or None,
                    "tags": tags,
                },
            })
        return records

    def _parse_other_activities_table(
        self,
        body: str,
        occurred_at: datetime,
        file_path: str | None,
        tags: list[Any],
    ) -> list[dict[str, Any]]:
        rows = self._extract_table(
            body, "Other Activities", ["Activity", "Category", "Duration"]
        )
        records: list[dict[str, Any]] = []
        for row in rows:
            title = row.get("activity", "").strip()
            if not title:
                continue
            category = row.get("category", "").strip() or "general"
            duration_minutes = self._parse_duration(row.get("duration", ""))
            records.append({
                "record_type": "activity",
                "source": "manual",
                "category": category,
                "title": title,
                "duration_minutes": duration_minutes,
                "occurred_at": occurred_at,
                "metadata": {
                    "file_path": file_path,
                    "notes": row.get("notes", "").strip() or None,
                    "tags": tags,
                },
            })
        return records

    def _parse_metrics_table(
        self,
        body: str,
        occurred_at: datetime,
        file_path: str | None,
        tags: list[Any],
    ) -> list[dict[str, Any]]:
        rows = self._extract_table(body, "Metrics", ["Metric", "Value", "Unit"])
        records: list[dict[str, Any]] = []
        for row in rows:
            name = row.get("metric", "").strip()
            value_str = row.get("value", "").strip()
            if not name or not value_str:
                continue
            try:
                value = Decimal(value_str)
            except Exception:
                continue
            unit = row.get("unit", "").strip() or "count"
            records.append({
                "record_type": "metric",
                "source": "obsidian",
                "metric_name": name,
                "metric_value": value,
                "unit": unit,
                "occurred_at": occurred_at,
                "metadata": {
                    "file_path": file_path,
                    "notes": row.get("notes", "").strip() or None,
                    "tags": tags,
                },
            })
        return records

    def _parse_energy_mood(
        self,
        body: str,
        occurred_at: datetime,
        file_path: str | None,
        tags: list[Any],
    ) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        in_section = False
        for line in body.splitlines():
            if line.strip().startswith("## Energy"):
                in_section = True
                continue
            if in_section and line.strip().startswith("##"):
                break
            if not in_section:
                continue
            match = ENERGY_MOOD_RE.match(line.strip())
            if match is None:
                continue
            label_raw = line.strip()
            if label_raw.lower().startswith("- energy"):
                name = "energy"
                unit = "rating"
            elif label_raw.lower().startswith("- mood"):
                name = "mood"
                unit = "rating"
            elif label_raw.lower().startswith("- sleep"):
                name = "sleep_hours"
                unit = "hours"
            else:
                continue
            value_str = match.group(1).strip()
            try:
                value = Decimal(value_str)
            except Exception:
                continue
            records.append({
                "record_type": "metric",
                "source": "obsidian",
                "metric_name": name,
                "metric_value": value,
                "unit": unit,
                "occurred_at": occurred_at,
                "metadata": {
                    "file_path": file_path,
                    "tags": tags,
                },
            })
        return records

    @staticmethod
    def _extract_table(
        body: str,
        section_hint: str,
        expected_cols: list[str],
    ) -> list[dict[str, str]]:
        lines = body.splitlines()
        start_idx: int | None = None
        for i, line in enumerate(lines):
            if section_hint.lower() in line.lower():
                start_idx = i
                break
        if start_idx is None:
            return []

        for i in range(start_idx + 1, len(lines)):
            if "|" not in lines[i]:
                continue
            header_line = lines[i]
            if i + 1 < len(lines) and TABLE_ROW_RE.match(lines[i + 1]):
                if TABLE_ROW_RE.match(header_line):
                    headers = [
                        c.strip().lower()
                        for c in header_line.strip().strip("|").split("|")
                    ]
                    rows: list[dict[str, str]] = []
                    for row_line in lines[i + 2 :]:
                        if not TABLE_ROW_RE.match(row_line):
                            break
                        cells = [
                            c.strip()
                            for c in row_line.strip().strip("|").split("|")
                        ]
                        if len(cells) != len(headers):
                            break
                        rows.append(dict(zip(headers, cells)))
                    return rows
            break
        return []

    @staticmethod
    def _parse_int(value: Any) -> int | None:
        if value is None:
            return None
        s = str(value).strip()
        if not s:
            return None
        try:
            return int(s)
        except ValueError:
            return None

    @staticmethod
    def _parse_duration(value: str) -> int:
        s = value.strip().lower()
        if not s:
            return 0
        m = re.search(r"(\d+)\s*min", s)
        if m:
            return int(m.group(1))
        m = re.search(r"(\d+)\s*h(?:r|our)?", s)
        if m:
            return int(m.group(1)) * 60
        try:
            return int(s)
        except ValueError:
            return 0

    @staticmethod
    def _parse_datetime(value: Any) -> datetime | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
        if isinstance(value, date):
            return datetime.combine(
                value, datetime.min.time(), tzinfo=timezone.utc
            )
        if isinstance(value, str):
            try:
                dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
                return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
            except ValueError:
                return None
        return None
