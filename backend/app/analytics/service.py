from collections import Counter
from datetime import datetime, timedelta, timezone

from ..models import AuditEvent


def summarize_user_activity(user_id, *, days=30, now=None):
    if isinstance(days, bool) or not isinstance(days, int) or not 1 <= days <= 365:
        raise ValueError("days must be an integer between 1 and 365")

    window_end = now or datetime.now(timezone.utc)
    if window_end.tzinfo is None:
        window_end = window_end.replace(tzinfo=timezone.utc)
    else:
        window_end = window_end.astimezone(timezone.utc)
    window_start = window_end - timedelta(days=days)

    events = (
        AuditEvent.query
        .filter(
            AuditEvent.user_id == user_id,
            AuditEvent.created_at >= window_start,
            AuditEvent.created_at < window_end,
        )
        .all()
    )

    action_counts = Counter(event.action for event in events)
    daily_counts = Counter()
    for event in events:
        created_at = event.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        daily_counts[created_at.astimezone(timezone.utc).date().isoformat()] += 1

    return {
        "window_start": window_start.isoformat(),
        "window_end": window_end.isoformat(),
        "days": days,
        "total_events": len(events),
        "by_action": dict(sorted(action_counts.items())),
        "by_day": dict(sorted(daily_counts.items())),
    }