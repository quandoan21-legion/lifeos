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

🚧 Planning and architecture phase.

---

# Long-term Goal

LifeOS is not just a tracking application.

The goal is to build a personal operating system that helps people understand, analyze, and improve the way they learn, work, and grow over time.

```
