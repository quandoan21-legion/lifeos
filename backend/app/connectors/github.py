from datetime import datetime, timezone
from typing import Any

import httpx

from app.connectors.base import BaseConnector
from app.connectors.registry import ConnectorRegistry

_GITHUB_EVENT_TYPE_MAP = {
    "PushEvent": "commit",
    "PullRequestEvent": "pull_request",
    "IssuesEvent": "issue",
    "IssueCommentEvent": "issue_comment",
    "PullRequestReviewEvent": "code_review",
    "CreateEvent": "branch_create",
    "WatchEvent": "star",
}


def _map_event_type(github_type: str) -> str:
    return _GITHUB_EVENT_TYPE_MAP.get(github_type, "other")


def _parse_github_timestamp(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


@ConnectorRegistry.register("github")
class GitHubConnector(BaseConnector):
    source = "github"
    BASE_URL = "https://api.github.com"

    def __init__(self, token: str, username: str):
        self.token = token
        self.username = username

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }

    async def authenticate(self) -> None:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.BASE_URL}/user",
                headers=self._headers(),
            )
            if resp.status_code != 200:
                raise ValueError("Invalid GitHub token")

    async def fetch_raw(
        self, since: datetime | None = None
    ) -> list[dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.BASE_URL}/users/{self.username}/events",
                headers=self._headers(),
                params={"per_page": 100},
            )
            resp.raise_for_status()
            events = resp.json()

        if since is not None:
            events = [
                e
                for e in events
                if _parse_github_timestamp(e["created_at"]) > since
            ]
        return events

    def normalize(self, raw: list[dict[str, Any]]) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for event in raw:
            payload = event.get("payload", {})
            results.append({
                "record_type": "event",
                "source": self.source,
                "event_type": _map_event_type(event["type"]),
                "occurred_at": _parse_github_timestamp(event["created_at"]),
                "metadata": {
                    "repo": event.get("repo", {}).get("name"),
                    "action": payload.get("action"),
                    "size": payload.get("size"),
                    "ref": payload.get("ref"),
                    "github_id": event.get("id"),
                },
            })
        return results
