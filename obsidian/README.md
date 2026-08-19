# Obsidian Vault — LifeOS Templates

Hệ thống template Obsidian cho LifeOS. Mỗi template ghi một loại dữ liệu, được parse tự động bởi ObsidianConnector và đẩy vào database qua Syncthing watcher.

---

## Mục lục

1. [Daily Note — Ghi chép hàng ngày](#1-daily-note)
2. [Workout Session — Ghi chép buổi tập](#2-workout-session)
3. [Body Metrics — Theo dõi cân nặng và chỉ số cơ thể](#3-body-metrics)
4. [Reading Session — Phiên đọc sách (KOReader)](#4-reading-session)
5. [Coding Session — Phiên code (GitHub)](#5-coding-session)
6. [Activity Log — Hoạt động thủ công](#6-activity-log)
7. [Weekly Review — Đánh giá tuần](#7-weekly-review)
8. [Monthly Review — Đánh giá tháng](#8-monthly-review)
9. [Bảng tham chiếu nhanh](#bang-tham-chieu-nhanh)

---

## 1. Daily Note

**File:** `Templates/Daily Note.md`
**Frontmatter type:** `daily`

Ghi chép tổng hợp mọi hoạt động trong ngày. Đây là file bạn dùng nhiều nhất — mở mỗi sáng, điền dần trong ngày.

### Cách ghi từng phần

#### Morning Intentions
Viết 3 mục tiêu tập trung trong ngày. Phần này không được parse, chỉ để bạn tự nhắc mình.

#### Activities Log → Reading (KOReader)

| Cột | Ý nghĩa | Cách ghi | Dữ liệu tạo ra |
|-----|---------|----------|----------------|
| Book | Tên sách | Text tự do | → activity (title) |
| Pages | Số trang đọc | Số nguyên, vd: `15` | → activity metadata (pages_read) |
| Duration | Thời gian đọc | `30 min`, `1 hr`, `45` | → activity (duration_minutes) |
| Notes | Ghi chú | Text, có thể để trống | → activity metadata (notes) |

**Ví dụ:**

| Book | Pages | Duration | Notes |
|------|-------|----------|-------|
| Atomic Habits | 22 | 35 min | Chapter 3 |
| Deep Work | 15 | 20 min | |

→ Tạo 2 activity records, category: reading, source: koreader.

#### Activities Log → Coding (GitHub)

| Cột | Ý nghĩa | Cách ghi | Dữ liệu tạo ra |
|-----|---------|----------|----------------|
| Repo | Tên repository | Text, vd: `lifeos` | → event metadata (repo) |
| Type | Loại event | `commit`, `pull_request`, `issue`, `code_review`, `branch_create`, `star`, `other` | → event (event_type) |
| Count | Số lượng | Số nguyên, vd: `5` | → event metadata (count) |
| Notes | Ghi chú | Text | → event metadata (notes) |

**Ví dụ:**

| Repo | Type | Count | Notes |
|------|------|-------|-------|
| lifeos | commit | 8 | Auth module |
| lifeos | pull_request | 2 | |

→ Tạo 2 event records, source: github.

#### Activities Log → Exercise

| Cột | Ý nghĩa | Cách ghi | Dữ liệu tạo ra |
|-----|---------|----------|----------------|
| Exercise | Tên bài tập | Text, vd: `Bench Press`, `Push-ups` | → metric (metric_name) |
| Sets | Số hiệp | Số nguyên, vd: `4` | → metric "Bench Press sets" |
| Reps | Số lần lặp mỗi hiệp | Số nguyên, vd: `10` | → metric "Bench Press reps" |
| Weight (kg) | Trọng lượng | Số thập phân, vd: `60`, `60.5`. Để trống nếu bài bodyweight | → metric "Bench Press weight" |
| Notes | Ghi chú | Text | → metric metadata |

**Ví dụ:**

| Exercise | Sets | Reps | Weight (kg) | Notes |
|----------|------|------|------------|-------|
| Bench Press | 4 | 10 | 60 | Felt easy |
| Push-ups | 3 | 20 | | Bodyweight |
| Squat | 5 | 5 | 80 | |

→ Tạo:
- 3 metric "Bench Press sets" = 4, "Push-ups sets" = 3, "Squat sets" = 5
- 3 metric "Bench Press reps" = 10, "Push-ups reps" = 20, "Squat reps" = 5
- 2 metric "Bench Press weight" = 60, "Squat weight" = 80 (Push-ups không có weight nên bỏ qua)

#### Activities Log → Other Activities

| Cột | Ý nghĩa | Cách ghi | Dữ liệu tạo ra |
|-----|---------|----------|----------------|
| Activity | Tên hoạt động | Text, vd: `Writing blog`, `Walking` | → activity (title) |
| Category | Phân loại | Text, vd: `writing`, `walking`, `general` | → activity (category) |
| Duration | Thời gian | `30 min`, `1 hr`, `45` | → activity (duration_minutes) |
| Notes | Ghi chú | Text | → activity metadata (notes) |

**Ví dụ:**

| Activity | Category | Duration | Notes |
|----------|----------|----------|-------|
| Writing blog | writing | 45 min | Draft 1 |
| Walking | walking | 30 min | |

→ Tạo 2 activity records, source: manual.

#### Body Metrics

| Cột | Ý nghĩa | Cách ghi | Dữ liệu tạo ra |
|-----|---------|----------|----------------|
| Metric | Tên chỉ số | `Weight`, `Waist`, `Body Fat`, `Steps`, hoặc tên tùy chỉnh | → metric (metric_name, tự động chuyển snake_case) |
| Value | Giá trị | Số thập phân, vd: `70.5`, `85`, `15` | → metric (metric_value) |
| Unit | Đơn vị | `kg`, `cm`, `%`, `count`, `bpm`, `hours` | → metric (unit) |
| Notes | Ghi chú | Text | → metric metadata |

**Ví dụ:**

| Metric | Value | Unit | Notes |
|--------|-------|------|-------|
| Weight | 70.5 | kg | Morning |
| Waist | 82 | cm | |
| Steps | 8500 | count | |

→ Tạo 3 metric records: weight = 70.5 kg, waist = 82 cm, steps = 8500 count.

#### Metrics (bảng chung)

Giống hệt Body Metrics ở trên — dùng cho bất kỳ metric nào bạn muốn ghi riêng lẻ (không thuộc nhóm body metrics). Cú pháp cột giống nhau.

#### Energy & Mood

| Dòng | Ý nghĩa | Cách ghi | Dữ liệu tạo ra |
|------|---------|----------|----------------|
| Energy (1-10) | Năng lượng trong ngày | Số 1-10, vd: `7` | → metric "energy" = 7, unit: rating |
| Mood (1-10) | Tâm trạng | Số 1-10, vd: `6` | → metric "mood" = 6, unit: rating |
| Sleep hours | Giờ ngủ đêm qua | Số thập phân, vd: `7.5` | → metric "sleep_hours" = 7.5, unit: hours |

**Ví dụ:**

```markdown
- Energy (1-10): 7
- Mood (1-10): 6
- Sleep hours: 7.5
```

→ Tạo 3 metric records.

#### Habits

Tick checkbox cho thói quen hoàn thành. Mỗi dòng tạo 1 metric.

| Cách ghi | Ý nghĩa | Dữ liệu tạo ra |
|----------|---------|----------------|
| `- [x] Drink 2L water` | Đã hoàn thành | → metric "habit_drink_2l_water" = 1, unit: bool |
| `- [ ] Meditate` | Chưa hoàn thành | → metric "habit_meditate" = 0, unit: bool |

Bạn có thể thêm/bớt dòng tùy ý — tên habit tự động được chuyển thành snake_case.

#### Highlights, Reflections, Tomorrow

Không được parse — chỉ dành cho ghi chép cá nhân.

---

## 2. Workout Session

**File:** `Templates/Workout Session.md`
**Frontmatter type:** `workout-session`

Dùng khi muốn ghi chi tiết một buổi tập riêng biệt (không ghi trong Daily Note).

### Frontmatter

| Trường | Ý nghĩa | Cách ghi | Dữ liệu tạo ra |
|--------|---------|----------|----------------|
| date | Ngày tập | `YYYY-MM-DD` | → activity (occurred_at) |
| title | Tên buổi tập | Text, vd: `Push Day`, `Morning Run` | → activity (title) |
| workout_type | Loại tập | `gym`, `running`, `cycling`, `yoga`, `swimming`, `calisthenics`, hoặc text tùy chỉnh | → activity metadata (workout_type) |
| duration_minutes | Tổng thời gian | Số nguyên, vd: `60` | → activity (duration_minutes) |
| occurred_at | Thời gian bắt đầu | `YYYY-MM-DDTHH:mm:ssZ` | → activity (occurred_at) |

### Strength Exercises table

Giống bảng Exercise trong Daily Note. Mỗi dòng tạo:
- 1 metric "tên bài sets"
- 1 metric "tên bài reps"
- 1 metric "tên bài weight" (nếu có trọng lượng)

### Cardio table

| Cột | Ý nghĩa | Cách ghi | Dữ liệu tạo ra |
|-----|---------|----------|----------------|
| Activity | Tên hoạt động cardio | `Running`, `Cycling` | → metric/activity (title) |
| Distance (km) | Khoảng cách | Số thập phân, vd: `5.2` | → metric "Running distance" = 5.2 km |
| Duration (min) | Thời gian | Số nguyên, vd: `30` | → activity (duration_minutes) |
| Avg Heart Rate | Nhịp tim trung bình | Số nguyên, vd: `145` | → metric "Running avg_hr" = 145 bpm |
| Notes | Ghi chú | Text | → metadata |

### Post-Workout Notes

Không được parse — dành cho ghi chép cá nhân (RPE, energy, soreness).

---

## 3. Body Metrics

**File:** `Templates/Body Metrics.md`
**Frontmatter type:** `body-metrics`

Dùng khi muốn ghi chỉ số cơ thể riêng biệt (không ghi trong Daily Note). Tốt cho việc cân đo hàng tuần/tháng.

### Measurements table

| Cột | Ý nghĩa | Cách ghi |
|-----|---------|----------|
| Metric | Tên chỉ số | `Weight`, `Waist`, `Chest`, `Hip`, `Body Fat`, `Muscle Mass`, `BMI`, `Resting HR`, `Sleep Hours`, `Steps`, hoặc tên tùy chỉnh |
| Value | Giá trị | Số thập phân |
| Unit | Đơn vị | `kg`, `cm`, `%`, `bpm`, `hours`, `count` |
| Notes | Ghi chú | Text |

**Tên metric tự động chuyển snake_case:** `Body Fat` → `body_fat`, `Resting HR` → `resting_hr`, `Sleep Hours` → `sleep_hours`.

**Ví dụ:**

| Metric | Value | Unit | Notes |
|--------|-------|------|-------|
| Weight | 70.5 | kg | Morning, before eating |
| Waist | 82 | cm | Measured at navel |
| Body Fat | 15 | % | From scale |
| Muscle Mass | 32 | kg | |
| Resting HR | 58 | bpm | |
| Sleep Hours | 7.5 | hours | |

→ Tạo 6 metric records.

---

## 4. Reading Session

**File:** `Templates/Reading Session.md`
**Frontmatter type:** `reading-session`

Dùng khi muốn ghi chi tiết một phiên đọc sách riêng biệt.

### Frontmatter

| Trường | Ý nghĩa | Cách ghi | Dữ liệu tạo ra |
|--------|---------|----------|----------------|
| date | Ngày đọc | `YYYY-MM-DD` | → activity (occurred_at) |
| title | Tên sách | Text | → activity (title) |
| author | Tác giả | Text | → activity metadata (author) |
| duration_seconds | Thời gian đọc (giây) | Số nguyên, vd: `2100` (35 phút) | → activity (duration_minutes, tự đổi) |
| pages_read | Số trang đọc | Số nguyên | → activity metadata (pages_read) |
| total_pages | Tổng số trang sách | Số nguyên | → activity metadata (total_pages) |
| device | Thiết bị đọc | `Kobo`, `Kindle`, `Phone` | → activity metadata (device) |

---

## 5. Coding Session

**File:** `Templates/Coding Session.md`
**Frontmatter type:** `coding-session`

Dùng khi muốn ghi chi tiết một phiên code riêng biệt.

### Frontmatter

| Trường | Ý nghĩa | Cách ghi | Dữ liệu tạo ra |
|--------|---------|----------|----------------|
| date | Ngày | `YYYY-MM-DD` | → event (occurred_at) |
| event_type | Loại event | `commit`, `pull_request`, `issue`, `issue_comment`, `code_review`, `branch_create`, `star`, `other` | → event (event_type) |
| repo | Repository | Text, vd: `lifeos` | → event metadata (repo) |
| action | Hành động | Text, vd: `opened`, `merged`, `pushed` | → event metadata (action) |
| size | Kích thước | Số nguyên (số commits) | → event metadata (size) |
| ref | Branch/Tag | Text, vd: `main`, `feature/auth` | → event metadata (ref) |

---

## 6. Activity Log

**File:** `Templates/Activity Log.md`
**Frontmatter type:** `activity`

Dùng khi muốn ghi một hoạt động thủ công riêng biệt (không thuộc reading, coding, hay exercise).

### Frontmatter

| Trường | Ý nghĩa | Cách ghi | Dữ liệu tạo ra |
|--------|---------|----------|----------------|
| date | Ngày | `YYYY-MM-DD` | → activity (occurred_at) |
| source | Nguồn | `manual` (mặc định) | → activity (source) |
| category | Phân loại | `writing`, `walking`, `learning`, `general`, hoặc text tùy chỉnh | → activity (category) |
| title | Tên hoạt động | Text | → activity (title) |
| duration_minutes | Thời gian | Số nguyên, vd: `45` | → activity (duration_minutes) |
| occurred_at | Thời gian chính xác | `YYYY-MM-DDTHH:mm:ssZ` | → activity (occurred_at) |

---

## 7. Weekly Review

**File:** `Templates/Weekly Review.md`
**Frontmatter type:** `weekly`

Template đánh giá cuối tuần. Các bảng trong Weekly Review **không được parse** — chúng là form trống để bạn tự điền sau khi xem dashboard analytics. Dữ liệu thực tế lấy từ API.

### Các phần mới

- **Exercise Summary**: Tổng hợp số buổi tập, thời gian, bài tập nổi bật
- **Body Metrics Trend**: So sánh cân nặng/vòng eo/% mỡ tuần này vs tuần trước

---

## 8. Monthly Review

**File:** `Templates/Monthly Review.md`
**Frontmatter type:** `monthly`

Template đánh giá cuối tháng. Tương tự Weekly Review, các bảng không được parse.

### Các phần mới

- **Exercise Summary**: Tổng hợp tập luyện cả tháng
- **Body Metrics Trend**: So sánh chỉ số đầu tháng vs cuối tháng

---

## Bảng tham chiếu nhanh

### File nào ghi loại dữ liệu nào?

| Loại dữ liệu | File dùng | Loại record tạo ra |
|-------------|----------|-------------------|
| Đọc sách (tổng hợp ngày) | Daily Note → Reading table | activity (category: reading) |
| Đọc sách (chi tiết phiên) | Reading Session | activity (category: reading) |
| Code (tổng hợp ngày) | Daily Note → Coding table | event (source: github) |
| Code (chi tiết phiên) | Coding Session | event (source: github) |
| Tập gym (tổng hợp ngày) | Daily Note → Exercise table | metric (sets, reps, weight) |
| Tập gym (chi tiết phiên) | Workout Session → Strength table | metric (sets, reps, weight) |
| Cardio (chi tiết phiên) | Workout Session → Cardio table | activity + metric (distance, hr) |
| Cân nặng, vòng eo, % mỡ (trong ngày) | Daily Note → Body Metrics table | metric (weight, waist, body_fat) |
| Cân nặng, vòng eo, % mỡ (riêng biệt) | Body Metrics | metric (weight, waist, body_fat) |
| Năng lượng, tâm trạng, giấc ngủ | Daily Note → Energy & Mood | metric (energy, mood, sleep_hours) |
| Thói quen hàng ngày | Daily Note → Habits | metric (habit_xxx = 0 hoặc 1) |
| Hoạt động thủ công | Daily Note → Other Activities HOẶC Activity Log | activity (source: manual) |
| Metric tùy chỉnh | Daily Note → Metrics table | metric (tên tùy chỉnh) |

### Quy tắc ghi bảng

1. **Luôn giữ hàng header và hàng separator** (`|---|---|`). Parser cần 2 hàng này để nhận diện bảng.
2. **Để trống ô nếu không có dữ liệu** — không ghi `N/A` hay `-`.
3. **Số thập phân dùng dấu chấm**: `70.5` (không phải `70,5`).
4. **Thời gian dùng format**: `30 min`, `1 hr`, `1.5 hr`, hoặc số nguyên (tự hiểu là phút).
5. **Tên metric tự động chuyển snake_case**: `Body Fat` → `body_fat`, `Resting HR` → `resting_hr`.
6. **Tên bài tập giữ nguyên trong metric_name**: `Bench Press` → `Bench Press sets`, `Bench Press reps`, `Bench Press weight`.
7. **Weight để trống cho bài bodyweight** — parser sẽ bỏ qua metric weight, chỉ ghi sets và reps.

### Quy tắc frontmatter

1. **Không để placeholder `{{...}}`** trong frontmatter — file có placeholder sẽ bị bỏ qua (đây là file template chưa điền).
2. **Trường `type` là bắt buộc** — đây là cách parser biết file chứa loại dữ liệu gì.
3. **Trường `date` dùng format** `YYYY-MM-DD` (vd: `2026-08-19`).
4. **Trường `occurred_at` dùng format** `YYYY-MM-DDTHH:mm:ssZ` (vd: `2026-08-19T10:30:00Z`).

### Ví dụ Daily Note hoàn chỉnh

```markdown
---
date: 2026-08-19
weekday: Tuesday
type: daily
tags: [daily, lifeos]
---

# Tuesday, 19/08/2026

## Morning Intentions

- [ ] Finish auth module
- [ ] Read 30 min
- [ ] Gym push day

---

## Activities Log

### Reading (KOReader)

| Book | Pages | Duration | Notes |
|------|-------|----------|-------|
| Atomic Habits | 22 | 35 min | Chapter 3 |
| Deep Work | 15 | 20 min | |

### Coding (GitHub)

| Repo | Type | Count | Notes |
|------|------|-------|-------|
| lifeos | commit | 8 | Auth module |
| lifeos | pull_request | 2 | |

### Exercise

| Exercise | Sets | Reps | Weight (kg) | Notes |
|----------|------|------|------------|-------|
| Bench Press | 4 | 10 | 60 | Felt easy |
| Push-ups | 3 | 20 | | Bodyweight |
| Tricep Dips | 3 | 12 | 15 | |

### Other Activities

| Activity | Category | Duration | Notes |
|----------|----------|----------|-------|
| Writing blog | writing | 45 min | Draft 1 |

---

## Body Metrics

| Metric | Value | Unit | Notes |
|--------|-------|------|-------|
| Weight | 70.5 | kg | Morning |
| Waist | 82 | cm | |
| Steps | 8500 | count | |

---

## Metrics

| Metric | Value | Unit | Notes |
|--------|-------|------|-------|
| Caffeine | 2 | cups | |

---

## Energy & Mood

- Energy (1-10): 7
- Mood (1-10): 6
- Sleep hours: 7.5

---

## Habits

- [x] Drink 2L water
- [x] Walk 10k steps
- [ ] Meditate
- [x] Read 30 min
- [ ] No sugar

---

## Highlights

> [!tip] Best thing that happened today

- Finished the auth module

## Reflections

> [!abstract] End-of-day reflection

- What went well: Coding flow was great
- What could improve: Forgot to meditate
- Ideas / insights: Schedule meditation after lunch

---

## Tomorrow

- [ ] Review PRs
- [ ] Leg day
- [ ] Read 30 min
```

File này tạo ra:
- 2 activity (reading): Atomic Habits 35 min, Deep Work 20 min
- 2 event (github): 8 commits, 2 PRs
- 9 metric (exercise): Bench Press sets/reps/weight, Push-ups sets/reps, Tricep Dips sets/reps/weight
- 1 activity (writing): Writing blog 45 min
- 3 metric (body): weight 70.5 kg, waist 82 cm, steps 8500 count
- 1 metric (custom): caffeine 2 cups
- 3 metric (energy/mood): energy 7, mood 6, sleep_hours 7.5
- 5 metric (habits): habit_drink_2l_water=1, habit_walk_10k_steps=1, habit_meditate=0, habit_read_30_min=1, habit_no_sugar=0

**Tổng cộng: 26 records từ 1 file.**
