import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any

import httpx

from app.cli.ingest import ingest_records
from app.connectors.obsidian import ObsidianConnector
from app.core.config import settings


async def fetch_events(
    client: httpx.AsyncClient, since_id: int
) -> list[dict[str, Any]]:
    resp = await client.get(
        f"{settings.SYNCTHING_URL}/rest/events",
        params={"since": since_id, "limit": 100},
        headers={"X-API-Key": settings.SYNCTHING_API_KEY or ""},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


async def process_file(
    connector: ObsidianConnector, vault_root: Path, relative_path: str
) -> list[dict[str, Any]]:
    file_path = vault_root / relative_path
    if not file_path.exists() or file_path.suffix != ".md":
        return []
    return connector.parse_file(file_path)


async def watch_loop(
    vault_path: str, dry_run: bool, once: bool
) -> None:
    if not settings.SYNCTHING_API_KEY:
        print("SYNCTHING_API_KEY must be set in .env")
        sys.exit(1)

    vault_root = Path(vault_path)
    if not vault_root.exists():
        print(f"Vault not found: {vault_path}")
        sys.exit(1)

    connector = ObsidianConnector(vault_path=vault_path)
    await connector.authenticate()

    folder_id = settings.SYNCTHING_FOLDER_ID
    last_id = 0
    pending: list[dict[str, Any]] = []

    async with httpx.AsyncClient() as client:
        while True:
            try:
                events = await fetch_events(client, last_id)
            except httpx.HTTPError as exc:
                print(f"Error fetching events: {exc}")
                if once:
                    break
                await asyncio.sleep(5)
                continue

            for event in events:
                last_id = max(last_id, event.get("id", 0))

                if event.get("type") != "ItemFinished":
                    continue
                data = event.get("data", {})
                if folder_id and data.get("folder") != folder_id:
                    continue

                item_type = data.get("type")
                item_path = data.get("item", "")
                if item_type != "file" or not item_path.endswith(".md"):
                    continue

                records = await process_file(
                    connector, vault_root, item_path
                )
                if records:
                    pending.extend(records)
                    print(
                        f"Synced {item_path}: {len(records)} records parsed"
                    )

            if pending:
                if dry_run:
                    for r in pending:
                        print(json.dumps(r, default=str, indent=2))
                    pending.clear()
                else:
                    await ingest_records(pending)
                    pending.clear()

            if once:
                break
            await asyncio.sleep(2)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Watch Syncthing events and sync Obsidian vault changes"
    )
    parser.add_argument(
        "--vault-path", default=None, help="Path to Obsidian vault"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print records without ingesting",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Process current events and exit (no polling)",
    )
    args = parser.parse_args()

    vault_path = args.vault_path or settings.OBSIDIAN_VAULT_PATH
    if not vault_path:
        print("Provide --vault-path or set OBSIDIAN_VAULT_PATH in .env")
        sys.exit(1)

    asyncio.run(watch_loop(vault_path, args.dry_run, args.once))


if __name__ == "__main__":
    main()
