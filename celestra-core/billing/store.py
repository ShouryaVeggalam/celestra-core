"""In-memory billing store — subscriptions + usage ledger."""

from __future__ import annotations

from billing.types import Subscription, UsageEvent, UsageSummary


class BillingStore:
    def __init__(self) -> None:
        self.subscriptions: dict[str, Subscription] = {}  # account_id -> sub
        self.usage: list[UsageEvent] = []

    def set_subscription(self, subscription: Subscription) -> Subscription:
        self.subscriptions[subscription.account_id] = subscription.model_copy(deep=True)
        return subscription.model_copy(deep=True)

    def get_subscription(self, account_id: str) -> Subscription | None:
        sub = self.subscriptions.get(account_id)
        return sub.model_copy(deep=True) if sub else None

    def add_usage(self, event: UsageEvent) -> UsageEvent:
        self.usage.append(event.model_copy(deep=True))
        return event.model_copy(deep=True)

    def summarize(self, account_id: str, metric: str | None = None) -> list[UsageSummary]:
        totals: dict[str, UsageSummary] = {}
        for event in self.usage:
            if event.account_id != account_id:
                continue
            if metric and event.metric != metric:
                continue
            key = event.metric
            if key not in totals:
                totals[key] = UsageSummary(
                    account_id=account_id,
                    metric=event.metric,
                    total=0.0,
                    unit=event.unit,
                    event_count=0,
                )
            totals[key].total += event.quantity
            totals[key].event_count += 1
        return sorted(totals.values(), key=lambda s: s.metric)

    def metric_total(self, account_id: str, metric: str) -> float:
        return sum(e.quantity for e in self.usage if e.account_id == account_id and e.metric == metric)
