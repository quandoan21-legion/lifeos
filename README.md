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

Future integrations:

- KOReader
- GitHub
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

Examples:

- KOReader connector.
- GitHub connector.
- Calendar connector.

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

**Analytics Database**

Stores:

- Events.
- Metrics.
- Aggregations.
- Historical data.

Purpose:

- Fast queries.
- Analytics.
- Reports.
- Dashboards.

---

# Planned Features

## Personal Tracking

- Daily journal.
- Habit tracking.
- Workout tracking.
- Weight tracking.
- Personal metrics.

---

## Reading Analytics

- KOReader integration.
- Reading session tracking.
- Reading statistics.
- Reading history.

---

## Coding Analytics

- Git integration.
- GitHub activity tracking.
- Coding statistics.

---

## Personal Reviews

- Daily reflection.
- Weekly review.
- Monthly review.
- Personal analytics dashboard.

---

# Roadmap

## Phase 1 — Foundation

- Define LifeOS data model.
- Build backend service.
- Setup database.
- Docker deployment.
- Basic API.

---

## Phase 2 — Obsidian Integration

- Obsidian plugin.
- Daily dashboard.
- Manual data entry.
- Habit tracking.

---

## Phase 3 — Data Connectors

- KOReader connector.
- Reading analytics.
- GitHub connector.
- Calendar connector.

---

## Phase 4 — Personal Analytics

- Weekly reports.
- Monthly reports.
- Productivity analysis.
- Personal insights.

---

# Current Status

Phase 1 — Foundation is in progress. The backend service is implemented with JWT-based authentication (issue #27 complete).

## What works

- User model with email, hashed password, full name, and active flag
- Password hashing with bcrypt
- JWT access tokens (30 min) and refresh tokens (7 days)
- `POST /api/v1/auth/login` — login, returns access + refresh token
- `POST /api/v1/auth/refresh` — exchange a refresh token for a new token pair
- `GET /api/v1/auth/me` — return the current authenticated user
- Protected endpoints require a valid Bearer access token
- Unit tests (10/10 passing)

---

# Getting Started

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (Astral's Python package manager)
- PostgreSQL database (or a Supabase project)

## Configuration

The backend reads configuration from a `.env` file at the project root. Required variables:

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

## API endpoints

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| GET | `/api/v1/health` | No | Health check |
| POST | `/api/v1/auth/login` | No | Login, returns token pair |
| POST | `/api/v1/auth/refresh` | No | Refresh access token |
| GET | `/api/v1/auth/me` | Yes | Get current user |

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

### Example: get current user

```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>"
```

---

# Long-term Goal

LifeOS is not just a tracking application.

The goal is to build a personal operating system that helps people understand, analyze, and improve the way they learn, work, and grow over time.

```
