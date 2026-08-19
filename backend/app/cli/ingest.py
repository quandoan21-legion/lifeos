import sys

import httpx

from app.core.config import settings


async def ingest_records(records: list[dict]) -> None:
    if not records:
        print("No records to ingest.")
        return

    base_url = f"http://localhost:{settings.app_port}/api/v1"
    login_resp = await httpx.AsyncClient().post(
        f"{base_url}/auth/login",
        json={
            "email": settings.ingest_email,
            "password": settings.ingest_password,
        },
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
