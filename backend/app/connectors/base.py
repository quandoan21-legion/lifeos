from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any


class BaseConnector(ABC):
    source: str

    @abstractmethod
    async def authenticate(self) -> None:
        """Authenticate with the external service. Raise on failure."""
        ...

    @abstractmethod
    async def fetch_raw(
        self, since: datetime | None = None
    ) -> list[dict[str, Any]]:
        """Fetch raw records from the source since the given timestamp."""
        ...

    @abstractmethod
    def normalize(self, raw: dict[str, Any]) -> dict[str, Any]:
        """Convert one raw record into a normalized record dict.

        Returns a dict with keys: record_type, occurred_at, payload.
        record_type is "activity", "event", or "metric".
        """
        ...

    async def run(
        self, since: datetime | None = None
    ) -> list[dict[str, Any]]:
        """Full pipeline: authenticate -> fetch_raw -> normalize each record."""
        await self.authenticate()
        raw_records = await self.fetch_raw(since)
        return [self.normalize(r) for r in raw_records]
