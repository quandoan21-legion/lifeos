from sqlalchemy import inspect

from app.database.base import Base
from app.database.connection import async_engine, engine


def init_db() -> None:
    import app.models  # noqa: F401
    Base.metadata.create_all(bind=engine)


async def init_db_async() -> None:
    import app.models  # noqa: F401
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def drop_db() -> None:
    import app.models  # noqa: F401
    Base.metadata.drop_all(bind=engine)


async def drop_db_async() -> None:
    import app.models  # noqa: F401
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


def get_table_names() -> list[str]:
    inspector = inspect(engine)
    return inspector.get_table_names()
