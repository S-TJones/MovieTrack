# Audit Activity Analysis

## Measure

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

## Reproduce

The analysis is implemented by `summarize_user_activity` in `backend/app/analytics/service.py`. Its `now` parameter makes the time window deterministic in tests. The regression test inserts events for two users and a fixed clock, then verifies per-action and per-day counts and user isolation.

Run it from `backend/`:

```powershell
python -m pytest tests/test_app.py::test_activity_analytics_is_reproducible_and_user_scoped -q
```

The endpoint is read-only; it neither mutates audit events nor returns other users' activity.
