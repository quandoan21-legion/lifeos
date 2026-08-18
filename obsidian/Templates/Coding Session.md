---
date: {{date:YYYY-MM-DD}}
source: github
category: coding
event_type:
repo:
action:
size:
ref:
type: coding-session
tags: [coding, github, lifeos]
---

# {{repo}} — {{event_type}}

## Event Details

| Field | Value |
|-------|-------|
| Repo | `{{repo}}` |
| Event type | `{{event_type}}` |
| Action | {{action}} |
| Size | {{size}} |
| Ref | `{{ref}}` |
| Occurred at | {{date:YYYY-MM-DDTHH:mm:ssZ}} |

## Event Type Reference

| GitHub Event | LifeOS type | Description |
|--------------|-------------|-------------|
| PushEvent | commit | Pushed commits |
| PullRequestEvent | pull_request | Opened/merged PR |
| IssuesEvent | issue | Created/closed issue |
| IssueCommentEvent | issue_comment | Commented on issue |
| PullRequestReviewEvent | code_review | Reviewed PR |
| CreateEvent | branch_create | Created branch/tag |
| WatchEvent | star | Starred repo |

## Notes

-

## Links

- [[Daily/{{date:YYYY-MM-DD}}|Daily Note]]
