import argparse
import asyncio
import json
import sys
from datetime import datetime, timedelta, timezone

from app.cli.ingest import ingest_records
from app.connectors import ConnectorRegistry
from app.core.config import settings


async def sync_obsidian(
    vault_path: str, since_hours: int, full: bool, dry_run: bool
) -> None:
    connector_cls = ConnectorRegistry.get("obsidian")
    connector = connector_cls(vault_path=vault_path)

    since = None if full else datetime.now(timezone.utc) - timedelta(
        hours=since_hours
    )
    records = await connector.run(since=since)

    print(f"Obsidian: {len(records)} records found")
    if dry_run:
        for r in records:
            print(json.dumps(r, default=str, indent=2))
        return

    await ingest_records(records)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sync Obsidian vault to LifeOS"
    )
    parser.add_argument(
        "--vault-path", default=None, help="Path to Obsidian vault"
    )
    parser.add_argument(
        "--since-hours",
        type=int,
        default=24,
        help="Sync files modified in last N hours",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Sync all files regardless of mtime",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print records without ingesting",
    )
    args = parser.parse_args()

    vault_path = args.vault_path or settings.OBSIDIAN_VAULT_PATH
    if not vault_path:
        print("Provide --vault-path or set OBSIDIAN_VAULT_PATH in .env")
        sys.exit(1)

    asyncio.run(
        sync_obsidian(vault_path, args.since_hours, args.full, args.dry_run)
    )


if __name__ == "__main__":
    main()
