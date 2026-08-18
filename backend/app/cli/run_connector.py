import argparse
import asyncio
import json
import sys
from datetime import datetime, timedelta, timezone

import httpx

from app.connectors import ConnectorRegistry
from app.core.config import settings


async def run_koreader(db_path: str, since_hours: int, dry_run: bool) -> None:
    connector_cls = ConnectorRegistry.get("koreader")
    connector = connector_cls(db_path=db_path)
    since = datetime.now(timezone.utc) - timedelta(hours=since_hours)
    records = await connector.run(since=since)

    print(f"KOReader: {len(records)} sessions found")
    if dry_run:
        for r in records:
            print(json.dumps(r, default=str, indent=2))
        return

    await _ingest(records)


async def run_github(since_hours: int, dry_run: bool) -> None:
    if not settings.GITHUB_TOKEN or not settings.GITHUB_USERNAME:
        print("GITHUB_TOKEN and GITHUB_USERNAME must be set in .env")
        sys.exit(1)

    connector_cls = ConnectorRegistry.get("github")
    connector = connector_cls(
        token=settings.GITHUB_TOKEN, username=settings.GITHUB_USERNAME
    )
    since = datetime.now(timezone.utc) - timedelta(hours=since_hours)
    records = await connector.run(since=since)

    print(f"GitHub: {len(records)} events found")
    if dry_run:
        for r in records:
            print(json.dumps(r, default=str, indent=2))
        return

    await _ingest(records)


async def _ingest(records: list[dict]) -> None:
    if not records:
        print("No records to ingest.")
        return

    base_url = f"http://localhost:{settings.app_port}/api/v1"
    login_resp = await httpx.AsyncClient().post(
        f"{base_url}/auth/login",
        json={"email": settings.ingest_email, "password": settings.ingest_password},
    )
    if login_resp.status_code != 200:
        print(f"Login failed: {login_resp.status_code} {login_resp.text}")
        sys.exit(1)

    token = login_resp.json()["access_token"]
    resp = await httpx.AsyncClient().post(
        f"{base_url}/events/ingest",
        headers={"Authorization": f"Bearer {token}"},
        json={"records": records},
    )
    if resp.status_code != 200:
        print(f"Ingest failed: {resp.status_code} {resp.text}")
        sys.exit(1)

    print(f"Ingested: {resp.json()}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a LifeOS connector")
    parser.add_argument("source", choices=["koreader", "github"])
    parser.add_argument("--db-path", default=None, help="Path to statistics.sqlite3")
    parser.add_argument(
        "--since-hours", type=int, default=24, help="Fetch records from last N hours"
    )
    parser.add_argument("--dry-run", action="store_true", help="Print records without ingesting")
    args = parser.parse_args()

    if args.source == "koreader":
        db_path = args.db_path or settings.KOREADER_DB_PATH
        if not db_path:
            print("Provide --db-path or set KOREADER_DB_PATH in .env")
            sys.exit(1)
        asyncio.run(run_koreader(db_path, args.since_hours, args.dry_run))
    elif args.source == "github":
        asyncio.run(run_github(args.since_hours, args.dry_run))


if __name__ == "__main__":
    main()
