# LifeOS

> An Obsidian-first Personal Operating System for collecting, analyzing, and reflecting on personal data.

## Overview

LifeOS is a self-hosted personal analytics platform designed to unify different areas of life into a single system.

Modern personal data is fragmented across many applications:

- Reading activity in KOReader.
- Coding activity from Git and GitHub.
- Calendar and schedule data.
- Knowledge management in Obsidian.
- Fitness, habits, and personal metrics from different applications.

Each application solves a specific problem, but there is no unified system that helps understand personal growth over time.

LifeOS aims to answer questions such as:

- How much time did I spend learning this month?
- How many hours did I read?
- How consistent was my training?
- What activities improve my productivity?
- What patterns can I discover about myself?

---

# Philosophy

LifeOS does not replace existing applications.

Instead, it works as a personal data integration and analytics layer.

The core workflow:

```
Collect → Normalize → Store → Analyze → Reflect
```

### Collect

Gather data from different sources.

Examples:

- KOReader reading sessions.
- GitHub activity.
- Calendar events.
- Fitness data.

### Normalize

Convert different data formats into a common event model.

### Store

Keep structured data for analytics while preserving human-readable records.

### Analyze

Generate statistics, trends, and personal insights.

### Reflect

Present information through dashboards, reports, and reviews.

---

# Design Principles

## Data Ownership

Personal data should belong to the user.

LifeOS follows these principles:

- Open formats whenever possible.
- Human-readable storage.
- Easy backup and migration.
- Self-hosted infrastructure.

The user owns the data.

---

## Obsidian-first

LifeOS uses Obsidian as the primary interface for personal knowledge and reflection.

Instead of building another closed productivity application, LifeOS integrates into an existing workflow.

Benefits:

- Markdown-based storage.
- Offline-first experience.
- Portable data.
- Extensible ecosystem.

Examples:

- Daily notes.
- Habit tracking.
- Workout logs.
- Reading summaries.
- Weekly reviews.

---

## Modular Architecture

LifeOS is built around independent connectors.

Adding a new data source should only require implementing a new connector.

Current integrations:

- KOReader (reading sessions)
- GitHub (coding activity)

Future integrations:

- Garmin
- Strava
- Calendar
- Other personal data sources

---

# Architecture

High-level system design:

```
                    Data Sources

        KOReader     GitHub     Calendar     Fitness
            |           |           |            |
            +-----------+-----------+------------+

                         |
                    Connectors

                         |

                  LifeOS Backend

              +-------------------+
              |                   |
              |                   |
        Analytics Database    Obsidian Vault
              |                   |
              |                   |
       Analytics Engine    Obsidian Plugin

                         |

                  Personal Devices
```

---

# Components

## Connectors

Connectors collect data from external applications.

Responsibilities:

- Authenticate with external services.
- Fetch raw data.
- Convert data into LifeOS events.
- Send data to the backend.

Current connectors:

- **KOReader connector** — reads `statistics.sqlite3` from a local filesystem path, groups page turns into reading sessions, and pushes them to the ingestion API.
- **GitHub connector** — fetches recent public activity from the GitHub Events API and normalizes it into LifeOS events.

---

## LifeOS Backend

The backend is the central processing layer.

Responsibilities:

- Receive incoming data.
- Normalize events.
- Provide APIs.
- Manage business logic.
- Generate analytics.

---

## Storage Layer

LifeOS separates human-readable data and machine-readable data.

### Human Layer

**Obsidian Vault**

Stores:

- Markdown notes.
- Personal records.
- Reflections.
- Daily logs.

Purpose:

- Human-readable.
- Portable.
- User-owned.

---

### Machine Layer

**Analytics Database (Supabase / PostgreSQL)**

Three tables power the connector system:

| Table | Purpose | Example records |
| --- | --- | --- |
| `activities` | Duration-based records | Reading sessions, workouts, coding sessions |
| `events` | Point-in-time records | Commits, pull requests, book finished |
| `metrics` | Measurable values | Weight, pages read, habit count |

All tables are owner-scoped via Row Level Security — each user can only see and modify their own data.

---

# Current Status

## What works

### Authentication (Phase 1)

- User model with email, hashed password, full name, and active flag
- Password hashing with bcrypt
- JWT access tokens (30 min) and refresh tokens (7 days)
- `POST /api/v1/auth/login` — login, returns access + refresh token
- `POST /api/v1/auth/refresh` — exchange a refresh token for a new token pair
- `GET /api/v1/auth/me` — return the current authenticated user
- Protected endpoints require a valid Bearer access token

### Data Connectors (Phase 3)

- Three-table event data model (`activities`, `events`, `metrics`) with RLS
- `BaseConnector` abstract interface + connector registry
- Ingestion API with deduplication
- KOReader connector (reads `statistics.sqlite3`, groups page turns into reading sessions)
- GitHub connector (fetches activity from GitHub Events API)
- CLI runner: `python -m app.cli.run_connector <source>`

---

# Getting Started

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (Astral's Python package manager)
- PostgreSQL database (or a Supabase project)
- [Syncthing](https://syncthing.net/) (for KOReader data sync)

## Configuration

The backend reads configuration from a `.env` file at the project root.

Required variables:

| Variable | Description |
| --- | --- |
| `DATABASE_URL` | PostgreSQL connection string, e.g. `postgresql+psycopg://user:password@host:5432/dbname` |
| `SECRET_KEY` | Secret used to sign JWT tokens. Change this in production. |

Optional variables (with defaults):

| Variable | Default | Description |
| --- | --- | --- |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 30 | Access token lifetime |
| `REFRESH_TOKEN_EXPIRE_DAYS` | 7 | Refresh token lifetime |
| `JWT_ALGORITHM` | HS256 | JWT signing algorithm |
| `LOG_LEVEL` | INFO | Application log level |

Connector variables (see Setup sections below):

| Variable | Description |
| --- | --- |
| `KOREADER_DB_PATH` | Path to KOReader `statistics.sqlite3` (synced via Syncthing) |
| `GITHUB_TOKEN` | GitHub personal access token |
| `GITHUB_USERNAME` | Your GitHub username |
| `INGEST_EMAIL` | LifeOS user email (used by connector CLI to login) |
| `INGEST_PASSWORD` | LifeOS user password (used by connector CLI to login) |

## Running the backend locally

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload
```

The API starts on `http://localhost:8000`. Interactive docs are available at `http://localhost:8000/docs`.

## Running with Docker

```bash
cd backend
docker compose up --build
```

The API starts on `http://localhost:8000`.

## Creating a user

There is no public registration endpoint. Create users with the CLI tool:

```bash
cd backend
uv run python -m app.cli.create_user
```

You will be prompted for an email, password (min 8 characters), and full name.

## Running tests

```bash
cd backend
uv run pytest -v
```

---

# API Endpoints

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| GET | `/api/v1/health` | No | Health check |
| POST | `/api/v1/auth/login` | No | Login, returns token pair |
| POST | `/api/v1/auth/refresh` | No | Refresh access token |
| GET | `/api/v1/auth/me` | Yes | Get current user |
| POST | `/api/v1/events/ingest` | Yes | Ingest activities, events, metrics (batch) |
| GET | `/api/v1/events/activities` | Yes | List activities (filter by source, category, since) |
| GET | `/api/v1/events/events` | Yes | List events (filter by source, event_type, since) |
| GET | `/api/v1/events/metrics` | Yes | List metrics (filter by source, metric_name, since) |

### Example: login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "securepassword123"}'
```

Response:

```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_at": "2026-08-18T12:30:00Z"
}
```

### Example: ingest a reading session

```bash
curl -X POST http://localhost:8000/api/v1/events/ingest \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "records": [
      {
        "record_type": "activity",
        "source": "koreader",
        "category": "reading",
        "title": "The Pragmatic Programmer",
        "duration_minutes": 35,
        "occurred_at": "2026-08-18T10:00:00Z",
        "metadata": {"pages_read": 12}
      }
    ]
  }'
```

Response:

```json
{
  "ingested": 1,
  "duplicates": 0
}
```

### Example: query activities

```bash
curl "http://localhost:8000/api/v1/events/activities?source=koreader&limit=10" \
  -H "Authorization: Bearer <access_token>"
```

---

# Connectors

## KOReader Connector

### How it works

KOReader stores reading statistics in a SQLite file called `statistics.sqlite3` inside the KOReader settings folder on your e-reader device. The connector reads this file, groups individual page-turn records into reading sessions (consecutive page turns within 10 minutes for the same book count as one session), and pushes them to the LifeOS ingestion API.

### Setup (requires manual configuration)

1. **Find the statistics file on your device**

   The file is located inside the KOReader settings folder:

   | Device | Path |
   | --- | --- |
   | Kobo | `.adds/koreader/settings/` |
   | Kindle | `koreader/settings/` |
   | Linux | `~/.local/share/koreader/` |

   Look for `statistics.sqlite3`.

2. **Install Syncthing on both devices**

   - Install [Syncthing](https://syncthing.net/) on the machine running LifeOS backend.
   - On your e-reader, use KOReader's built-in Syncthing plugin (available in KOReader app settings).
   - Share the KOReader settings folder so `statistics.sqlite3` syncs to your backend machine automatically.

3. **Set the file path in `.env`**

   ```env
   KOREADER_DB_PATH=/path/to/synced/statistics.sqlite3
   ```

4. **Create a LifeOS user for ingestion** (if you haven't already)

   ```bash
   cd backend
   uv run python -m app.cli.create_user
   ```

   Then set the credentials in `.env`:

   ```env
   INGEST_EMAIL=your@email.com
   INGEST_PASSWORD=yourpassword
   ```

5. **Run the connector**

   ```bash
   # Dry run — see what would be ingested
   uv run python -m app.cli.run_connector koreader --dry-run

   # Ingest last 24 hours
   uv run python -m app.cli.run_connector koreader

   # Ingest last 7 days
   uv run python -m app.cli.run_connector koreader --since-hours 168
   ```

6. **(Optional) Automate with cron**

   ```cron
   0 * * * * cd /path/to/backend && uv run python -m app.cli.run_connector koreader --since-hours 1
   ```

---

## GitHub Connector

### How it works

The connector calls the GitHub Events API to fetch your recent public activity (commits, pull requests, issues, reviews, etc.) and normalizes each event into a LifeOS event record.

### Setup (requires manual configuration)

1. **Create a GitHub personal access token**

   - Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Generate a new token (no scopes needed for public activity)
   - Copy the token

2. **Set credentials in `.env`**

   ```env
   GITHUB_TOKEN=ghp_your_token_here
   GITHUB_USERNAME=your_github_username
   INGEST_EMAIL=your@email.com
   INGEST_PASSWORD=yourpassword
   ```

3. **Run the connector**

   ```bash
   # Dry run — see what would be ingested
   uv run python -m app.cli.run_connector github --dry-run

   # Ingest last 24 hours
   uv run python -m app.cli.run_connector github

   # Ingest last 7 days
   uv run python -m app.cli.run_connector github --since-hours 168
   ```

4. **(Optional) Automate with cron**

   ```cron
   0 * * * * cd /path/to/backend && uv run python -m app.cli.run_connector github --since-hours 1
   ```

### GitHub event type mapping

| GitHub Event | LifeOS event_type |
| --- | --- |
| PushEvent | commit |
| PullRequestEvent | pull_request |
| IssuesEvent | issue |
| IssueCommentEvent | issue_comment |
| PullRequestReviewEvent | code_review |
| CreateEvent | branch_create |
| WatchEvent | star |
| Other | other |

---

# Roadmap

## Phase 1 — Foundation (done)

- Define LifeOS data model
- Build backend service
- Setup database
- Docker deployment
- Basic API
- JWT authentication

---

## Phase 2 — Obsidian Integration

- Obsidian plugin
- Daily dashboard
- Manual data entry
- Habit tracking

---

## Phase 3 — Data Connectors (done)

- KOReader connector
- Reading analytics
- GitHub connector
- Ingestion API with deduplication

---

## Phase 4 — Personal Analytics

- Weekly reports
- Monthly reports
- Productivity analysis
- Personal insights

---

# Long-term Goal

LifeOS is not just a tracking application.

The goal is to build a personal operating system that helps people understand, analyze, and improve the way they learn, work, and grow over time.
