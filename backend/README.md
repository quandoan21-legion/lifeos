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
| `db_echo`           | False   | Echo SQL statements to logs           |

### Architecture

The database layer lives in `app/database/`:

| File              | Purpose                                                      |
| ----------------- | ------------------------------------------------------------ |
| `connection.py`   | Sync and async engine creation + connection health checks    |
| `session.py`      | Session factories and FastAPI dependency injection            |
| `base.py`          | Declarative base + UUID and timestamp mixins                 |
| `utils.py`         | `init_db()`, `drop_db()`, and table inspection helpers       |

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

## Project structure

```
backend/
├── app/
│   ├── api/
│   │   ├── middleware/
│   │   └── v1/
│   ├── core/
│   │   ├── config.py
│   │   └── logging.py
│   ├── database/
│   │   ├── base.py
│   │   ├── connection.py
│   │   ├── session.py
│   │   └── utils.py
│   ├── models/
│   ├── schemas/
│   ├── services/
│   └── main.py
└── pyproject.toml
```

## Testing the database connection

```bash
uv run python test_db.py
```
