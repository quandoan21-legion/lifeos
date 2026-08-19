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

# Table of Contents

- [Philosophy](#philosophy)
- [Design Principles](#design-principles)
- [Architecture](#architecture)
- [Components](#components)
- [Current Status](#current-status)
- [Installation](#installation)
  - [Step 1: Prerequisites](#step-1-prerequisites)
  - [Step 2: Clone the Repository](#step-2-clone-the-repository)
  - [Step 3: Configure Environment Variables](#step-3-configure-environment-variables)
  - [Step 4: Run Database Migrations](#step-4-run-database-migrations)
  - [Step 5: Install Backend Dependencies](#step-5-install-backend-dependencies)
  - [Step 6: Create a User Account](#step-6-create-a-user-account)
  - [Step 7: Start the Backend Server](#step-7-start-the-backend-server)
  - [Step 8: Verify the Installation](#step-8-verify-the-installation)
  - [Step 9: Set Up Obsidian Vault](#step-9-set-up-obsidian-vault)
  - [Step 10: Configure Connectors](#step-10-configure-connectors)
- [Running with Docker](#running-with-docker)
- [API Endpoints](#api-endpoints)
- [Connectors](#connectors)
- [Roadmap](#roadmap)
- [Long-term Goal](#long-term-goal)

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

### Personal Analytics (Phase 4)

- Daily activity and event summaries
- Streak tracking (current and best, per source+category)
- Time-series trends (daily/weekly/monthly)
- Source and category breakdowns with percentages
- Event type counts with percentages
- Metric aggregation (sum, avg, min, max, latest)
- Combined dashboard endpoint (all data in one call)

### Obsidian Templates (Phase 2 — partial)

- Daily Note template (intentions, activity log, metrics, reflection)
- Weekly Review template (breakdown, streaks, top activities, wins/challenges)
- Monthly Review template (trend, books read, projects progress, goals)
- Activity Log template (manual activity entry)
- Reading Session template (KOReader)
- Coding Session template (GitHub)

---

# Installation

## Step 1: Prerequisites

Install the following on your machine before starting:

| Tool | Version | Purpose | Install Link |
|------|---------|---------|--------------|
| Python | 3.12+ | Backend runtime | [python.org](https://www.python.org/downloads/) |
| uv | latest | Python package manager | [docs.astral.sh/uv](https://docs.astral.sh/uv/) |
| Node.js | 18+ | Obsidian / frontend tooling | [nodejs.org](https://nodejs.org/) |
| Git | latest | Clone the repository | [git-scm.com](https://git-scm.com/) |
| Obsidian | latest | Note-taking interface | [obsidian.md](https://obsidian.md/) |
| Syncthing | latest | Sync KOReader data (optional) | [syncthing.net](https://syncthing.net/) |

You also need a **Supabase project** (free tier works):

1. Go to [supabase.com](https://supabase.com/) and create a new project.
2. Note down the following from your project dashboard:
   - **Project URL** (e.g. `https://xvreirbhaxxktipsiwmd.supabase.co`)
   - **Anon key** (public key, found in Settings → API)
   - **Database connection string** (Settings → Database → Connection string, use the "Direct connection" format with format `postgresql+psycopg://user:password@host:5432/postgres`)

---

## Step 2: Clone the Repository

```bash
git clone https://github.com/quandoan21-legion/lifeos.git
cd lifeos
```

---

## Step 3: Configure Environment Variables

Create a `.env` file at the project root (same level as `README.md`):

```bash
cp .env.example .env
```

If there is no `.env.example`, create one manually. Fill in the following:

```env
# === Required ===

# Supabase database connection string
# Go to Supabase Dashboard → Settings → Database → Connection string
# Use the format: postgresql+psycopg://user:password@host:5432/postgres
DATABASE_URL=postgresql+psycopg://your_user:your_password@db.xxxxx.supabase.co:5432/postgres

# Supabase public keys (for frontend / API access)
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your_anon_key_here

# JWT secret — change this to a random string for production
# Generate one with: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=change-this-to-a-random-secret

# === Optional (with defaults) ===

# ACCESS_TOKEN_EXPIRE_MINUTES=30
# REFRESH_TOKEN_EXPIRE_DAYS=7
# JWT_ALGORITHM=HS256
# LOG_LEVEL=INFO

# === Connector Configuration (optional, see Step 10) ===

# KOReader — path to statistics.sqlite3 (synced via Syncthing)
KOREADER_DB_PATH=

# GitHub — personal access token and username
GITHUB_TOKEN=
GITHUB_USERNAME=

# Obsidian vault path
OBSIDIAN_VAULT_PATH=

# Syncthing Event API (for real-time vault sync, see Step 10.3)
SYNCTHING_URL=http://localhost:8384
SYNCTHING_API_KEY=
SYNCTHING_FOLDER_ID=

# Connector CLI — credentials used to login and ingest
INGEST_EMAIL=
INGEST_PASSWORD=
```

> **Important:** Never commit the `.env` file. It is already in `.gitignore`.

---

## Step 4: Run Database Migrations

The migration creates three tables (`activities`, `events`, `metrics`) with Row Level Security policies.

### Option A: Using Supabase Dashboard

1. Go to your Supabase project dashboard.
2. Open the **SQL Editor**.
3. Copy the contents of `supabase/migrations/20260818025224_create_activities_events_metrics.sql`.
4. Paste into the SQL Editor and click **Run**.

### Option B: Using Supabase MCP (if available)

If you have the Supabase MCP tools configured, the migration can be applied programmatically. The migration file is at:

```
supabase/migrations/20260818025224_create_activities_events_metrics.sql
```

### Verify

After running the migration, verify the tables exist:

1. Go to Supabase Dashboard → Table Editor.
2. You should see three tables: `activities`, `events`, `metrics`.
3. Each table should have RLS enabled (a green shield icon).

---

## Step 5: Install Backend Dependencies

```bash
cd backend
uv sync
```

This creates a virtual environment and installs all dependencies from `pyproject.toml` and `uv.lock`.

Verify the installation:

```bash
uv run python -c "from app.core.config import settings; print(settings.app_name)"
```

You should see:

```
LifeOS API
```

---

## Step 6: Create a User Account

There is no public registration endpoint. Create users with the CLI tool:

```bash
cd backend
uv run python -m app.cli.create_user
```

You will be prompted for:

```
Email: your@email.com
Password: ********        (minimum 8 characters)
Full name: Your Name
```

If successful, you will see:

```
User 'your@email.com' created successfully.
```

> **Note:** This user is stored in the local `users` table (not Supabase Auth). The password is hashed with bcrypt.

---

## Step 7: Start the Backend Server

### Option A: Run directly with uvicorn

```bash
cd backend
uv run uvicorn app.main:app --reload
```

The API starts on `http://localhost:8000`.

### Option B: Run with Docker (see [Running with Docker](#running-with-docker))

---

## Step 8: Verify the Installation

Open your browser and navigate to:

```
http://localhost:8000/docs
```

You should see the FastAPI interactive Swagger UI with all available endpoints.

### Test the health check:

```bash
curl http://localhost:8000/api/v1/health
```

Expected response:

```json
{"status": "ok"}
```

### Test login:

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "your@email.com", "password": "yourpassword"}'
```

Expected response:

```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_at": "2026-08-18T12:30:00Z"
}
```

### Test the dashboard:

```bash
curl "http://localhost:8000/api/v1/analytics/dashboard?days=7" \
  -H "Authorization: Bearer <access_token>"
```

If everything is set up correctly, you will receive a JSON response with empty arrays (no data yet).

---

## Step 9: Set Up Obsidian Vault

The `obsidian/` folder contains a pre-built vault with templates.

### 9.1 Open the vault in Obsidian

1. Open Obsidian.
2. Click **Open folder as vault**.
3. Select the `obsidian/` folder inside the LifeOS project.

### 9.2 Install the Templater plugin

1. Go to Settings → Community plugins.
2. Turn off **Safe Mode** (if enabled).
3. Click **Browse** and search for **Templater**.
4. Click **Install**, then **Enable**.

### 9.3 Configure Templater

1. Go to Settings → Templater.
2. Set **Template folder location** to `Templates`.
3. Enable **Trigger Templater on new file creation** (recommended).

### 9.4 Configure Daily Notes

1. Go to Settings → Daily notes.
2. Set the following:

| Setting | Value |
|--------|-------|
| Date format | `YYYY-MM-DD` |
| New file location | `Daily` |
| Template file location | `Templates/Daily Note` |

### 9.5 Configure Weekly Notes (optional)

| Setting | Value |
|--------|-------|
| Date format | `YYYY-[W]ww` |
| New file location | `Weekly` |
| Template file location | `Templates/Weekly Review` |

### 9.6 Create your first daily note

Click the calendar icon in the left ribbon (or press `Ctrl/Cmd + N` if Daily Notes core plugin is enabled). A new daily note will be created from the template.

### Available Templates

| Template | Purpose |
|----------|---------|
| Daily Note | Morning intentions, activity log, metrics, energy/mood, highlights, reflections |
| Weekly Review | Week-at-a-glance, source/category breakdown, streaks, top activities, wins/challenges |
| Monthly Review | Monthly summary, weekly trend, books read, project progress, goals |
| Activity Log | Manual activity entry (source: manual) |
| Reading Session | KOReader reading session (book, pages, duration) |
| Coding Session | GitHub activity (repo, event type, action) |

See `obsidian/README.md` for detailed template documentation.

---

## Step 10: Configure Connectors

Connectors automatically fetch data from external services and push it to the LifeOS backend.

### 10.1 KOReader Connector (reading sessions)

#### What it does

Reads `statistics.sqlite3` from KOReader, groups page-turn records into reading sessions (consecutive page turns within 10 minutes for the same book), and pushes them to the ingestion API.

#### Setup

1. **Find the statistics file on your e-reader:**

   | Device | Path |
   |--------|------|
   | Kobo | `.adds/koreader/settings/` |
   | Kindle | `koreader/settings/` |
   | Linux | `~/.local/share/koreader/` |

   Look for `statistics.sqlite3`.

2. **Install Syncthing on both devices:**

   - Install [Syncthing](https://syncthing.net/) on the machine running LifeOS backend.
   - On your e-reader, use KOReader's built-in Syncthing plugin.
   - Share the KOReader settings folder so `statistics.sqlite3` syncs to your backend machine.

3. **Set the file path in `.env`:**

   ```env
   KOREADER_DB_PATH=/path/to/synced/statistics.sqlite3
   ```

4. **Set ingestion credentials in `.env`** (same user created in Step 6):

   ```env
   INGEST_EMAIL=your@email.com
   INGEST_PASSWORD=yourpassword
   ```

5. **Test with a dry run:**

   ```bash
   cd backend
   uv run python -m app.cli.run_connector koreader --dry-run
   ```

   This prints found sessions without ingesting. Verify the output looks correct.

6. **Run the connector:**

   ```bash
   # Ingest last 24 hours (default)
   uv run python -m app.cli.run_connector koreader

   # Ingest last 7 days
   uv run python -m app.cli.run_connector koreader --since-hours 168
   ```

7. **(Optional) Automate with cron:**

   ```cron
   0 * * * * cd /path/to/lifeos/backend && uv run python -m app.cli.run_connector koreader --since-hours 1
   ```

---

### 10.2 GitHub Connector (coding activity)

#### What it does

Fetches your recent public GitHub activity (commits, PRs, issues, reviews) via the GitHub Events API and normalizes each event into a LifeOS event record.

#### Setup

1. **Create a GitHub personal access token:**

   - Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Generate a new token (no scopes needed for public activity)
   - Copy the token

2. **Set credentials in `.env`:**

   ```env
   GITHUB_TOKEN=ghp_your_token_here
   GITHUB_USERNAME=your_github_username
   INGEST_EMAIL=your@email.com
   INGEST_PASSWORD=yourpassword
   ```

3. **Test with a dry run:**

   ```bash
   cd backend
   uv run python -m app.cli.run_connector github --dry-run
   ```

4. **Run the connector:**

   ```bash
   # Ingest last 24 hours (default)
   uv run python -m app.cli.run_connector github

   # Ingest last 7 days
   uv run python -m app.cli.run_connector github --since-hours 168
   ```

5. **(Optional) Automate with cron:**

   ```cron
   0 * * * * cd /path/to/lifeos/backend && uv run python -m app.cli.run_connector github --since-hours 1
   ```

#### GitHub event type mapping

| GitHub Event | LifeOS event_type |
|--------------|-------------------|
| PushEvent | commit |
| PullRequestEvent | pull_request |
| IssuesEvent | issue |
| IssueCommentEvent | issue_comment |
| PullRequestReviewEvent | code_review |
| CreateEvent | branch_create |
| WatchEvent | star |
| Other | other |

---

### 10.3 Syncthing Vault Watcher (real-time Obsidian sync)

#### What it does

Listens to the Syncthing Event API in real-time. Whenever Syncthing finishes syncing a `.md` file from another device (e.g. your phone), the watcher immediately parses that file and pushes the extracted records to the ingestion API.

This solves the problem where editing notes on your phone and syncing via Syncthing would not update the database — the watcher reacts to each file-sync event as it happens.

#### Setup

1. **Install Syncthing** on the machine running LifeOS backend and on your phone (e.g. via the Mobian Sync or Syncthing-Fork Android app).

2. **Share your Obsidian vault folder** between both devices in Syncthing. Note the **Folder ID** (visible in the Syncthing Web UI).

3. **Get your Syncthing API key:**
   - Open the Syncthing Web UI (`http://localhost:8384`).
   - Click **Actions** → **API Key**.
   - Copy the key.

4. **Set configuration in `.env`:**

   ```env
   OBSIDIAN_VAULT_PATH=/path/to/your/obsidian/vault
   SYNCTHING_URL=http://localhost:8384
   SYNCTHING_API_KEY=your-syncthing-api-key
   SYNCTHING_FOLDER_ID=your-folder-id
   INGEST_EMAIL=your@email.com
   INGEST_PASSWORD=yourpassword
   ```

   > `SYNCTHING_FOLDER_ID` is optional — leave it empty to listen to all folders.

5. **Test with a dry run (process current events and exit):**

   ```bash
   cd backend
   uv run python -m app.cli.watch_syncthing --once --dry-run
   ```

6. **Run as a long-running service:**

   ```bash
   cd backend
   uv run python -m app.cli.watch_syncthing
   ```

   The watcher polls the Syncthing Event API every 2 seconds. When a `.md` file finishes syncing, it is parsed and ingested immediately.

7. **(Optional) Run as a systemd service:**

   Create `/etc/systemd/system/lifeos-syncthing-watcher.service`:

   ```ini
   [Unit]
   Description=LifeOS Syncthing Vault Watcher
   After=network.target

   [Service]
   Type=simple
   WorkingDirectory=/path/to/lifeos/backend
   ExecStart=/path/to/uv run python -m app.cli.watch_syncthing
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

   Then:

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable --now lifeos-syncthing-watcher
   ```

---

# Running with Docker

If you prefer Docker over running the backend directly:

```bash
cd backend
docker compose up --build
```

The API starts on `http://localhost:8000`.

The Docker setup:
- Builds from `Dockerfile` (Python 3.12-slim base image)
- Installs dependencies with `uv sync --frozen`
- Mounts the `app/` directory for hot-reload during development
- Reads environment variables from `.env`
- Restarts automatically unless stopped manually

---

# Running Tests

```bash
cd backend
uv run pytest -v
```

Tests cover authentication (login, token refresh, protected endpoints) and database operations.

---

# API Endpoints

## Authentication

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/health` | No | Health check |
| POST | `/api/v1/auth/login` | No | Login, returns token pair |
| POST | `/api/v1/auth/refresh` | No | Refresh access token |
| GET | `/api/v1/auth/me` | Yes | Get current user |

## Data Ingestion

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/events/ingest` | Yes | Ingest activities, events, metrics (batch) |
| GET | `/api/v1/events/activities` | Yes | List activities (filter by source, category, since) |
| GET | `/api/v1/events/events` | Yes | List events (filter by source, event_type, since) |
| GET | `/api/v1/events/metrics` | Yes | List metrics (filter by source, metric_name, since) |

## Analytics

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/analytics/summary` | Yes | Daily activity summaries (duration, count, unique titles) |
| GET | `/api/v1/analytics/events/summary` | Yes | Daily event count summaries |
| GET | `/api/v1/analytics/streaks` | Yes | Current and best streaks (consecutive active days) |
| GET | `/api/v1/analytics/trend` | Yes | Time-series trend (daily/weekly/monthly granularity) |
| GET | `/api/v1/analytics/sources` | Yes | Activity duration breakdown by source |
| GET | `/api/v1/analytics/categories` | Yes | Activity duration breakdown by category |
| GET | `/api/v1/analytics/event-types` | Yes | Event count breakdown by event_type |
| GET | `/api/v1/analytics/metrics` | Yes | Aggregated metric values (sum, avg, min, max, latest) |
| GET | `/api/v1/analytics/dashboard` | Yes | Combined dashboard (all summaries, streaks, top items, recent events) |

## API Examples

### Login

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

### Ingest a reading session

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

### Query activities

```bash
curl "http://localhost:8000/api/v1/events/activities?source=koreader&limit=10" \
  -H "Authorization: Bearer <access_token>"
```

### Get dashboard

```bash
curl "http://localhost:8000/api/v1/analytics/dashboard?days=7" \
  -H "Authorization: Bearer <access_token>"
```

Response (abbreviated):

```json
{
  "period_start": "2026-08-11",
  "period_end": "2026-08-18",
  "activities": [
    {"period_start": "2026-08-18", "period_end": "2026-08-18", "total_duration_minutes": 45, "total_count": 2, "unique_titles": 1}
  ],
  "source_breakdown": [
    {"source": "koreader", "total_duration_minutes": 45, "total_count": 2, "percentage": 100.0}
  ],
  "streaks": [
    {"source": "koreader", "category": "reading", "current_streak": 3, "best_streak": 5, "last_active_date": "2026-08-18"}
  ],
  "top_activities": [
    {"title": "The Pragmatic Programmer", "source": "koreader", "category": "reading", "total_duration_minutes": 120, "session_count": 3}
  ]
}
```

### Get reading trend (last 30 days, weekly)

```bash
curl "http://localhost:8000/api/v1/analytics/trend?days=30&granularity=weekly&source=koreader" \
  -H "Authorization: Bearer <access_token>"
```

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

## Phase 2 — Obsidian Integration (partial)

- Obsidian templates (done)
- Syncthing vault watcher — real-time sync (done)
- Obsidian plugin (planned)
- Daily dashboard (planned)
- Manual data entry (planned)
- Habit tracking (planned)

---

## Phase 3 — Data Connectors (done)

- KOReader connector
- Reading analytics
- GitHub connector
- Ingestion API with deduplication

---

## Phase 4 — Personal Analytics (done)

- Daily activity summaries (duration, count, unique titles per day)
- Daily event count summaries
- Streak tracking (current and best consecutive active days, per source+category)
- Time-series trends (daily/weekly/monthly granularity, filterable by source/category)
- Source breakdown (activity duration split by data source)
- Category breakdown (activity duration split by category)
- Event type counts (events grouped by type with percentages)
- Metric aggregation (sum, avg, min, max, latest per metric name)
- Combined dashboard endpoint (all summaries + streaks + top activities + recent events in one call)

---

# Long-term Goal

LifeOS is not just a tracking application.

The goal is to build a personal operating system that helps people understand, analyze, and improve the way they learn, work, and grow over time.
