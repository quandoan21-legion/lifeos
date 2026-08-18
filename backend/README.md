# LifeOS Backend

FastAPI backend for the LifeOS application with SQLAlchemy 2.x ORM.

## Setup

```bash
cd backend
uv sync
```

## Running the server

```bash
uv run uvicorn app.main:app --reload
```

The server starts on `http://localhost:8000`.

## Database

The backend uses SQLAlchemy 2.x with PostgreSQL (hosted on Supabase).

### Configuration

Database connection is configured via the `DATABASE_URL` environment variable in `.env`:

```
DATABASE_URL=postgresql+psycopg://<user>:<password>@<host>:<port>/<database>
```

Additional pool settings (optional):

| Variable           | Default | Description                          |
| ------------------ | ------- | ------------------------------------ |
| `db_pool_size`     | 5       | Number of permanent connections      |
| `db_max_overflow`  | 10      | Extra connections beyond pool size   |
| `db_pool_recycle`  | 300     | Seconds before a connection is recycled |
| `db_echo`          | False   | Echo SQL statements to logs          |

### Architecture

The database layer lives in `app/database/`:

| File              | Purpose                                                      |
| ----------------- | ------------------------------------------------------------ |
| `connection.py`   | Sync and async engine creation + connection health checks    |
| `session.py`      | Session factories and FastAPI dependency injection            |
| `base.py`         | Declarative base + UUID and timestamp mixins                 |
| `utils.py`        | `init_db()`, `drop_db()`, and table inspection helpers       |

### Using sessions in FastAPI routes

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

router = APIRouter()

@router.get("/items")
async def list_items(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT 1"))
    return result.scalar()
```

### Creating models

Models inherit from `Base` and use the provided mixins:

```python
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base, TimestampMixin, UUIDMixin

class Item(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "items"
    name: Mapped[str] = mapped_column(String(255), nullable=False)
```

- `UUIDMixin` provides an auto-generated UUID primary key (`id`)
- `TimestampMixin` provides `created_at` and `updated_at` columns

### Sync vs Async

- **Async sessions** (`get_db`) are used in FastAPI route handlers
- **Sync sessions** (`get_sync_db`) are used in scripts, tests, and CLI utilities

### Initializing tables

```python
from app.database.utils import init_db

init_db()  # Creates all tables defined by models
```

For async contexts:

```python
from app.database.utils import init_db_async

await init_db_async()
```

## Testing the database connection

```bash
uv run python test_db.py
```

---

## Connectors

Connectors collect data from external sources (KOReader, GitHub, etc.), normalize it, and push it to the LifeOS ingestion API.

### Connector architecture

```
BaseConnector (abstract)
├── KOReaderConnector  — reads statistics.sqlite3, groups page turns into sessions
└── GitHubConnector    — fetches activity from GitHub Events API
```

Every connector implements three methods:

| Method | Description |
| --- | --- |
| `authenticate()` | Validate access to the data source (file exists, API token valid) |
| `fetch_raw(since)` | Fetch raw records since the given timestamp |
| `normalize(raw)` | Convert raw records into LifeOS record dicts |

The `run(since)` method chains all three: authenticate → fetch → normalize.

### Connector registry

Connectors self-register via the `@ConnectorRegistry.register("source_name")` decorator. To list available sources:

```python
from app.connectors import ConnectorRegistry

print(ConnectorRegistry.list_sources())  # ['koreader', 'github']
```

### Running connectors

Use the CLI runner:

```bash
# Dry run (print records without ingesting)
uv run python -m app.cli.run_connector koreader --db-path /path/to/statistics.sqlite3 --dry-run
uv run python -m app.cli.run_connector github --dry-run

# Ingest last 24 hours
uv run python -m app.cli.run_connector koreader
uv run python -m app.cli.run_connector github

# Ingest last 7 days
uv run python -m app.cli.run_connector koreader --since-hours 168
uv run python -m app.cli.run_connector github --since-hours 168
```

The CLI logs into the LifeOS API using `INGEST_EMAIL` / `INGEST_PASSWORD` from `.env`, then posts records to `POST /api/v1/events/ingest`.

### Connector configuration

Set these in the project root `.env`:

| Variable | Description |
| --- | --- |
| `KOREADER_DB_PATH` | Path to KOReader `statistics.sqlite3` (synced via Syncthing) |
| `GITHUB_TOKEN` | GitHub personal access token |
| `GITHUB_USERNAME` | Your GitHub username |
| `INGEST_EMAIL` | LifeOS user email (for connector CLI login) |
| `INGEST_PASSWORD` | LifeOS user password (for connector CLI login) |

### Adding a new connector

1. Create `app/connectors/your_source.py`
2. Subclass `BaseConnector`, set `source`, implement `authenticate`, `fetch_raw`, `normalize`
3. Decorate with `@ConnectorRegistry.register("your_source")`
4. Import the module in `app/connectors/__init__.py` to trigger registration

Example:

```python
from app.connectors.base import BaseConnector
from app.connectors.registry import ConnectorRegistry

@ConnectorRegistry.register("my_source")
class MyConnector(BaseConnector):
    source = "my_source"

    async def authenticate(self) -> None:
        ...

    async def fetch_raw(self, since=None) -> list[dict]:
        ...

    def normalize(self, raw: list[dict]) -> list[dict]:
        ...
```

---

## Project structure

```
backend/
├── app/
│   ├── api/
│   │   ├── middleware/
│   │   └── v1/
│   │       ├── auth.py
│   │       ├── events.py
│   │       └── router.py
│   ├── cli/
│   │   ├── create_user.py
│   │   └── run_connector.py
│   ├── connectors/
│   │   ├── base.py
│   │   ├── registry.py
│   │   ├── koreader.py
│   │   └── github.py
│   ├── core/
│   │   ├── config.py
│   │   └── logging.py
│   ├── database/
│   │   ├── base.py
│   │   ├── connection.py
│   │   ├── session.py
│   │   └── utils.py
│   ├── models/
│   │   ├── user.py
│   │   ├── activity.py
│   │   ├── event.py
│   │   └── metric.py
│   ├── schemas/
│   │   ├── auth.py
│   │   └── event.py
│   ├── services/
│   └── main.py
└── pyproject.toml
```
