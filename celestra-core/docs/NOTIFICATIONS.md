# Notifications — Celestra Core (Phase 5)

Multi-channel notification dispatch for every Celestra app.

## Channels

| Channel | Behavior (Phase 5) |
|---|---|
| `email` | Logging outbox (swap for SES/SMTP later) |
| `webhook` | HTTP POST via httpx |
| `in_app` | Per-user inbox |

## Usage

```python
from notifications import NotificationService, SendNotificationRequest

await notifications.send(
    SendNotificationRequest(
        channel="email",
        recipient="ops@celestra.dev",
        subject="Alert",
        body="Something happened",
    )
)
inbox = notifications.list_inbox(user_id)
```

## HTTP (`/api/v1/notifications`) — auth required

| Method | Path |
|---|---|
| POST | `/send` |
| GET | `/inbox` |
