# Connectors — Technical Spec

Phase 3: Data Connectors cho LifeOS. Gồm 5 task, làm theo thứ tự.

---

## Task 1 — Event Data Model

### Mục tiêu

Tạo model `Event` — bảng normalized lưu dữ liệu từ mọi connector (KOReader, GitHub, ...). Đây là nền tảng cho toàn bộ hệ thống connector.

### Schema

Bảng `events`:

| Cột | Kiểu | Ghi chú |
|---|---|---|
| `id` | UUID (PK) | `UUIDMixin` |
| `user_id` | UUID (FK → users.id) | NOT NULL, indexed |
| `source` | String(50) | NOT NULL, indexed. VD: `koreader`, `github` |
| `event_type` | String(50) | NOT NULL. VD: `reading_session`, `commit`, `pull_request` |
| `occurred_at` | DateTime(tz=True) | NOT NULL, indexed |
| `payload` | JSONB | NOT NULL. Dữ liệu thô đã normalize |
| `created_at` | DateTime(tz=True) | `TimestampMixin` |
| `updated_at` | DateTime(tz=True) | `TimestampMixin` |

### Indexes

- Composite index `(user_id, occurred_at)` — query theo thời gian của user
- Composite index `(user_id, source, event_type)` — query theo source/type

### RLS (Supabase)

4 policy owner-scoped, `TO authenticated`:

```sql
ALTER TABLE events ENABLE ROW LEVEL SECURITY;

CREATE POLICY "select_own_events" ON events FOR SELECT
  TO authenticated USING (auth.uid() = user_id);
CREATE POLICY "insert_own_events" ON events FOR INSERT
  TO authenticated WITH CHECK (auth.uid() = user_id);
CREATE POLICY "update_own_events" ON events FOR UPDATE
  TO authenticated USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
CREATE POLICY "delete_own_events" ON events FOR DELETE
  TO authenticated USING (auth.uid() = user_id);
```

### Files

- `app/models/event.py` — class `Event(Base, UUIDMixin, TimestampMixin)`
- `app/models/__init__.py` — export `Event`
- Migration SQL qua Supabase MCP

### Acceptance

- Bảng `events` tồn tại trong DB
- RLS enabled, 4 policy đúng
- Import `Event` từ `app.models` không lỗi

---

## Task 2 — Connector Base Interface

### Mục tiêu

Định nghĩa contract chung cho mọi connector. Connector nào cũng phải implement interface này.

### Abstract Base Class

```python
# app/connectors/base.py

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any


class BaseConnector(ABC):
    source: str  # VD "koreader", "github"

    @abstractmethod
    async def authenticate(self) -> None:
        """Xác thực với external service. Raise nếu fail."""
        ...

    @abstractmethod
    async def fetch_raw(self, since: datetime | None = None) -> list[dict[str, Any]]:
        """Fetch raw data từ external service kể từ thời điểm `since`.
        Trả về list raw record (chưa normalize)."""
        ...

    @abstractmethod
    def normalize(self, raw: dict[str, Any]) -> dict[str, Any]:
        """Convert 1 raw record thành LifeOS event payload.
        Trả về dict có keys: event_type, occurred_at, payload."""
        ...

    async def run(self, since: datetime | None = None) -> list[dict[str, Any]]:
        """Pipeline đầy đủ: authenticate → fetch_raw → normalize từng record.
        Trả về list normalized event dict."""
        await self.authenticate()
        raw_records = await self.fetch_raw(since)
        return [self.normalize(r) for r in raw_records]
```

### Connector Registry

```python
# app/connectors/registry.py

class ConnectorRegistry:
    _registry: dict[str, type[BaseConnector]] = {}

    @classmethod
    def register(cls, source: str):
        def decorator(connector_cls: type[BaseConnector]) -> type[BaseConnector]:
            cls._registry[source] = connector_cls
            return connector_cls
        return decorator

    @classmethod
    def get(cls, source: str) -> type[BaseConnector]:
        if source not in cls._registry:
            raise KeyError(f"Unknown connector: {source}")
        return cls._registry[source]

    @classmethod
    def list_sources(cls) -> list[str]:
        return list(cls._registry.keys())
```

### Files

- `app/connectors/base.py` — `BaseConnector`
- `app/connectors/registry.py` — `ConnectorRegistry`
- `app/connectors/__init__.py` — export

### Acceptance

- `BaseConnector` không thể instantiate trực tiếp (abstract)
- Subclass implement đủ 3 method thì chạy được `run()`
- Registry register/get hoạt động đúng

---

## Task 3 — Ingestion API

### Mục tiêu

Endpoint nhận event đã normalize từ connector, lưu vào DB.

### Endpoints

#### `POST /api/v1/events/ingest`

Request body:

```json
{
  "events": [
    {
      "source": "koreader",
      "event_type": "reading_session",
      "occurred_at": "2026-08-18T10:30:00Z",
      "payload": { ... }
    }
  ]
}
```

Response (200):

```json
{
  "ingested": 5,
  "duplicates": 0
}
```

### Logic

1. Yêu cầu auth (`get_current_user`)
2. Validate mỗi event: `source` phải nằm trong registry, `event_type` non-empty, `occurred_at` valid
3. Dedup: kiểm tra `(user_id, source, event_type, occurred_at)` — nếu trùng thì skip, đếm vào `duplicates`
4. Insert các event mới, gán `user_id` = current user
5. Trả về count

### Schemas

```python
# app/schemas/event.py

class EventIn(BaseModel):
    source: str = Field(min_length=1, max_length=50)
    event_type: str = Field(min_length=1, max_length=50)
    occurred_at: datetime
    payload: dict[str, Any]

class IngestRequest(BaseModel):
    events: list[EventIn] = Field(min_length=1, max_length=500)

class IngestResponse(BaseModel):
    ingested: int
    duplicates: int

class EventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    source: str
    event_type: str
    occurred_at: datetime
    payload: dict[str, Any]
    created_at: datetime
```

#### `GET /api/v1/events`

Query params: `source` (optional), `event_type` (optional), `since` (optional), `limit` (default 100, max 500)

Response: `list[EventOut]`

### Files

- `app/schemas/event.py`
- `app/schemas/__init__.py` — export
- `app/api/v1/events.py` — router
- `app/api/v1/router.py` — include events router

### Acceptance

- POST ingest với token hợp lệ → lưu event vào DB
- POST ingest không token → 401
- GET events trả về event của user hiện tại
- Dedup hoạt động

---

## Task 4 — KOReader Connector

### Mục tiêu

Connector đọc file `metadata.sqlite` từ KOReader, trích xuất reading sessions, normalize thành LifeOS event.

### KOReader Data

KOReader lưu metadata trong SQLite tại:
- Linux: `~/.local/share/koreader/metadata.sqlite`
- macOS: `~/Library/Application Support/koreader/metadata.sqlite`

Bảng `page_data_view` chứa reading stats:

| Cột | Kiểu | Ghi chú |
|---|---|---|
| `book` | text | Đường dẫn file sách |
| `title` | text | Tên sách |
| `authors` | text | Tác giả |
| `start_time` | datetime | Bắt đầu session |
| `duration` | integer | Giây |
| `page` | integer | Số trang đã đọc |
| `total_pages` | integer | Tổng số trang |
| `device` | text | Device ID |

### Implementation

```python
# app/connectors/koreader.py

@ConnectorRegistry.register("koreader")
class KOReaderConnector(BaseConnector):
    source = "koreader"

    def __init__(self, db_path: str):
        self.db_path = db_path

    async def authenticate(self) -> None:
        # KOReader dùng file local, không cần auth
        # Chỉ kiểm tra file tồn tại
        if not Path(self.db_path).exists():
            raise FileNotFoundError(f"KOReader metadata not found: {self.db_path}")

    async def fetch_raw(self, since: datetime | None = None) -> list[dict]:
        # Đọc SQLite sync (sqlite3), filter by start_time > since
        ...

    def normalize(self, raw: dict) -> dict:
        return {
            "event_type": "reading_session",
            "occurred_at": raw["start_time"],
            "payload": {
                "book": raw["title"],
                "author": raw["authors"],
                "duration_seconds": raw["duration"],
                "pages_read": raw["page"],
                "total_pages": raw["total_pages"],
                "device": raw["device"],
            }
        }
```

### Config

Thêm vào `Settings`:

```python
KOREADER_DB_PATH: str | None = None
```

### Files

- `app/connectors/koreader.py`
- `app/connectors/__init__.py` — import để trigger registry
- `app/core/config.py` — thêm `KOREADER_DB_PATH`

### Acceptance

- Cho file SQLite mẫu → `run()` trả về list event dict
- Event có `source = "koreader"`, `event_type = "reading_session"`
- `since` filter đúng
- File không tồn tại → raise FileNotFoundError

---

## Task 5 — GitHub Connector

### Mục tiêu

Connector fetch activity từ GitHub API (commits, PRs, issues, reviews), normalize thành LifeOS event.

### GitHub API

Endpoint: `GET https://api.github.com/users/{username}/events`

Response: list event với type `PushEvent`, `PullRequestEvent`, `IssuesEvent`, etc.

Auth: header `Authorization: token {personal_access_token}`

Rate limit: 60 req/giờ không auth, 5000 req/giờ có token.

### Event Types Mapping

| GitHub Event | LifeOS event_type |
|---|---|
| `PushEvent` | `commit` |
| `PullRequestEvent` | `pull_request` |
| `IssuesEvent` | `issue` |
| `IssueCommentEvent` | `issue_comment` |
| `PullRequestReviewEvent` | `code_review` |
| `CreateEvent` | `branch_create` |
| `WatchEvent` | `star` |

### Implementation

```python
# app/connectors/github.py

@ConnectorRegistry.register("github")
class GitHubConnector(BaseConnector):
    source = "github"

    BASE_URL = "https://api.github.com"

    def __init__(self, token: str, username: str):
        self.token = token
        self.username = username

    async def authenticate(self) -> None:
        # Validate token bằng GET /user
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.BASE_URL}/user",
                headers=self._headers(),
            )
            if resp.status_code != 200:
                raise ValueError("Invalid GitHub token")

    async def fetch_raw(self, since: datetime | None = None) -> list[dict]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.BASE_URL}/users/{self.username}/events",
                headers=self._headers(),
                params={"per_page": 100},
            )
            resp.raise_for_status()
            events = resp.json()
            if since:
                events = [e for e in events if datetime.fromisoformat(e["created_at"].replace("Z","+00:00")) > since]
            return events

    def normalize(self, raw: dict) -> dict:
        return {
            "event_type": _map_event_type(raw["type"]),
            "occurred_at": raw["created_at"],
            "payload": {
                "repo": raw["repo"]["name"],
                "action": raw.get("payload", {}).get("action"),
                "size": raw.get("payload", {}).get("size"),
                "ref": raw.get("payload", {}).get("ref"),
            }
        }

    def _headers(self) -> dict:
        return {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }
```

### Config

Thêm vào `Settings`:

```python
GITHUB_TOKEN: str | None = None
GITHUB_USERNAME: str | None = None
```

### Files

- `app/connectors/github.py`
- `app/connectors/__init__.py` — import để trigger registry
- `app/core/config.py` — thêm `GITHUB_TOKEN`, `GITHUB_USERNAME`

### Acceptance

- Token hợp lệ → `authenticate()` pass
- Token sai → raise ValueError
- `fetch_raw()` trả về list GitHub event
- `normalize()` map đúng event_type
- `run()` trả về list normalized event

---

## Thứ tự thực hiện

```
Task 1 (Event Model) → Task 2 (Base Interface) → Task 3 (Ingestion API)
                                                        ↓
                                          Task 4 (KOReader) + Task 5 (GitHub)
```

Task 4 và 5 có thể làm song song sau khi Task 1-3 xong.
