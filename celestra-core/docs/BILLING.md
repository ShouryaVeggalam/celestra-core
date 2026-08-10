# Billing — Celestra Core (Phase 6)

Plans, metering, and entitlements (Stripe-style platform primitives).

## Plans

| Plan | Highlights |
|---|---|
| `free` | 100 AI req/day, 1 knowledge base |
| `pro` | Higher limits + analytics export |
| `enterprise` | Unlimited (+ SSO flag) |

Numeric entitlement `-1` means unlimited.

## Usage

```python
from billing import BillingService, AssignPlanRequest, RecordUsageRequest

billing.assign_plan(AssignPlanRequest(account_id="acct", plan_id="pro"))
billing.record_usage(RecordUsageRequest(account_id="acct", metric="ai.requests_per_day", quantity=1))
check = billing.check_entitlement("acct", "ai.requests_per_day")
billing.require_entitlement("acct", "agents.enabled")
```

## HTTP (`/api/v1/billing`) — auth required

| Method | Path |
|---|---|
| GET | `/plans` |
| POST | `/subscriptions` |
| GET | `/subscriptions/{account_id}` |
| POST | `/usage` |
| GET | `/usage/{account_id}` |
| GET | `/entitlements/{account_id}/{feature}` |
