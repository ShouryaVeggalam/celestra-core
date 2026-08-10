# Analytics — Celestra Core (Phase 6)

Product analytics event tracking for every Celestra app.

## Usage

```python
from analytics import AnalyticsService, TrackEventRequest, EventQuery

analytics.track(TrackEventRequest(name="ai.complete", account_id="acct", properties={"model": "gpt"}))
events = analytics.query(EventQuery(name="ai.complete", limit=50))
counts = analytics.counts(account_id="acct")
```

## HTTP (`/api/v1/analytics`) — auth required

| Method | Path |
|---|---|
| POST | `/track` |
| POST | `/query` |
| GET | `/counts` |
