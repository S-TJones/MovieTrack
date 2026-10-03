# Audit Activity Analysis

## Event catalogue

The application records the following audit actions in `backend/app/audit/actions.py`:

- `USER_REGISTERED`
- `LOGIN_SUCCESS`
- `LOGIN_FAILED`
- `LOGOUT`
- `MOVIE_SEARCHED`
- `MOVIE_VIEWED`
- `MOVIE_ADDED_TO_COLLECTION`
- `MOVIE_REMOVED_FROM_COLLECTION`
- `RATING_CREATED`
- `RATING_UPDATED`
- `RATING_DELETED`
- `AI_SEARCH_REQUESTED`
- `AI_RECOMMENDATION_REQUESTED`

These events are persisted to `audit_events` with `user_id`, `action`, `resource_type`, `resource_id`, `correlation_id`, and `metadata_json`.

## KPI definitions

The activity summary defines a small but useful analytics layer for the authenticated user:

- `total_events`: number of audit rows for the authenticated user inside the selected time window
- `by_action`: count of events grouped by action name
- `by_day`: count of events grouped by UTC date
- `window_start` and `window_end`: open/closed interval used for the analytic slice

These KPIs support basic product questions like:

- Which activities are users performing most often?
- Are collection or rating events increasing over time?
- Are search or AI actions concentrated in a specific window?

## Reproducible analysis

MovieTrack exposes `GET /api/analytics/activity?days=30`. It reports authenticated-user audit-event counts by action and by UTC calendar day. The analysis filters by `user_id` and a half-open UTC interval `[window_start, window_end)`. `days` is bounded to 1–365.

Example response:

```json
{
  "window_start": "2026-09-02T12:00:00+00:00",
  "window_end": "2026-10-02T12:00:00+00:00",
  "days": 30,
  "total_events": 3,
  "by_action": {
    "MOVIE_SEARCHED": 1,
    "RATING_CREATED": 1,
    "USER_REGISTERED": 1
  },
  "by_day": {
    "2026-10-01": 1,
    "2026-10-02": 2
  }
}
```

The analysis is implemented by `summarize_user_activity` in `backend/app/analytics/service.py`. Its `now` parameter makes the time window deterministic in tests. The regression test inserts events for two users and a fixed clock, then verifies per-action and per-day counts and user isolation.

Run it from `backend/`:

```powershell
python -m pytest tests/test_app.py::test_activity_analytics_is_reproducible_and_user_scoped -q
```

The endpoint is read-only; it neither mutates audit events nor returns other users' activity.
