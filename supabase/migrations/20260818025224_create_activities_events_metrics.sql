/*
# Create activities, events, and metrics tables

1. New Tables
- `activities` — duration-based records (reading sessions, workouts, coding sessions).
  - id (uuid PK)
  - user_id (uuid FK auth.users, NOT NULL, DEFAULT auth.uid())
  - source (varchar 50, NOT NULL) — e.g. "koreader", "obsidian", "github"
  - category (varchar 50, NOT NULL) — e.g. "reading", "workout", "coding"
  - title (varchar 255, NOT NULL) — e.g. book title, workout type
  - duration_minutes (integer, NOT NULL, CHECK >= 0)
  - occurred_at (timestamptz, NOT NULL)
  - metadata (jsonb, NOT NULL DEFAULT '{}')
  - created_at, updated_at (timestamptz)
- `events` — point-in-time records (commits, PRs, book finished).
  - id (uuid PK)
  - user_id (uuid FK auth.users, NOT NULL, DEFAULT auth.uid())
  - source (varchar 50, NOT NULL)
  - event_type (varchar 50, NOT NULL) — e.g. "commit", "pull_request", "book_finished"
  - occurred_at (timestamptz, NOT NULL)
  - metadata (jsonb, NOT NULL DEFAULT '{}')
  - created_at, updated_at (timestamptz)
- `metrics` — measurable values (weight, pages read, habit count).
  - id (uuid PK)
  - user_id (uuid FK auth.users, NOT NULL, DEFAULT auth.uid())
  - source (varchar 50, NOT NULL)
  - metric_name (varchar 100, NOT NULL) — e.g. "weight", "pages_read", "habit_done"
  - metric_value (numeric(12,2), NOT NULL)
  - unit (varchar 20, NOT NULL) — e.g. "kg", "pages", "count"
  - occurred_at (timestamptz, NOT NULL)
  - metadata (jsonb, NOT NULL DEFAULT '{}')
  - created_at, updated_at (timestamptz)

2. Indexes
- activities: (user_id, occurred_at), (user_id, source, category)
- events: (user_id, occurred_at), (user_id, source, event_type)
- metrics: (user_id, occurred_at), (user_id, metric_name)

3. Security
- Enable RLS on all three tables.
- Owner-scoped CRUD (4 policies each): SELECT/INSERT/UPDATE/DELETE
  scoped to authenticated user via auth.uid() = user_id.
- user_id defaults to auth.uid() so inserts omitting user_id succeed.
*/

CREATE TABLE IF NOT EXISTS activities (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL DEFAULT auth.uid() REFERENCES auth.users(id) ON DELETE CASCADE,
    source varchar(50) NOT NULL,
    category varchar(50) NOT NULL,
    title varchar(255) NOT NULL,
    duration_minutes integer NOT NULL CHECK (duration_minutes >= 0),
    occurred_at timestamptz NOT NULL,
    metadata jsonb NOT NULL DEFAULT '{}',
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_activities_user_occurred
    ON activities (user_id, occurred_at);
CREATE INDEX IF NOT EXISTS idx_activities_user_source_category
    ON activities (user_id, source, category);

ALTER TABLE activities ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "select_own_activities" ON activities;
CREATE POLICY "select_own_activities" ON activities FOR SELECT
    TO authenticated USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "insert_own_activities" ON activities;
CREATE POLICY "insert_own_activities" ON activities FOR INSERT
    TO authenticated WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "update_own_activities" ON activities;
CREATE POLICY "update_own_activities" ON activities FOR UPDATE
    TO authenticated USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "delete_own_activities" ON activities;
CREATE POLICY "delete_own_activities" ON activities FOR DELETE
    TO authenticated USING (auth.uid() = user_id);


CREATE TABLE IF NOT EXISTS events (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL DEFAULT auth.uid() REFERENCES auth.users(id) ON DELETE CASCADE,
    source varchar(50) NOT NULL,
    event_type varchar(50) NOT NULL,
    occurred_at timestamptz NOT NULL,
    metadata jsonb NOT NULL DEFAULT '{}',
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_events_user_occurred
    ON events (user_id, occurred_at);
CREATE INDEX IF NOT EXISTS idx_events_user_source_type
    ON events (user_id, source, event_type);

ALTER TABLE events ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "select_own_events" ON events;
CREATE POLICY "select_own_events" ON events FOR SELECT
    TO authenticated USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "insert_own_events" ON events;
CREATE POLICY "insert_own_events" ON events FOR INSERT
    TO authenticated WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "update_own_events" ON events;
CREATE POLICY "update_own_events" ON events FOR UPDATE
    TO authenticated USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "delete_own_events" ON events;
CREATE POLICY "delete_own_events" ON events FOR DELETE
    TO authenticated USING (auth.uid() = user_id);


CREATE TABLE IF NOT EXISTS metrics (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL DEFAULT auth.uid() REFERENCES auth.users(id) ON DELETE CASCADE,
    source varchar(50) NOT NULL,
    metric_name varchar(100) NOT NULL,
    metric_value numeric(12,2) NOT NULL,
    unit varchar(20) NOT NULL,
    occurred_at timestamptz NOT NULL,
    metadata jsonb NOT NULL DEFAULT '{}',
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_metrics_user_occurred
    ON metrics (user_id, occurred_at);
CREATE INDEX IF NOT EXISTS idx_metrics_user_name
    ON metrics (user_id, metric_name);

ALTER TABLE metrics ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "select_own_metrics" ON metrics;
CREATE POLICY "select_own_metrics" ON metrics FOR SELECT
    TO authenticated USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "insert_own_metrics" ON metrics;
CREATE POLICY "insert_own_metrics" ON metrics FOR INSERT
    TO authenticated WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "update_own_metrics" ON metrics;
CREATE POLICY "update_own_metrics" ON metrics FOR UPDATE
    TO authenticated USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "delete_own_metrics" ON metrics;
CREATE POLICY "delete_own_metrics" ON metrics FOR DELETE
    TO authenticated USING (auth.uid() = user_id);
