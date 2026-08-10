"""In-memory analytics event store."""

from __future__ import annotations

from analytics.types import AnalyticsEvent, EventCount, EventQuery


class AnalyticsStore:
    def __init__(self) -> None:
        self._events: list[AnalyticsEvent] = []

    def append(self, event: AnalyticsEvent) -> AnalyticsEvent:
        self._events.append(event.model_copy(deep=True))
        return event.model_copy(deep=True)

    def query(self, query: EventQuery) -> list[AnalyticsEvent]:
        results = self._events
        if query.name:
            results = [e for e in results if e.name == query.name]
        if query.account_id:
            results = [e for e in results if e.account_id == query.account_id]
        if query.user_id:
            results = [e for e in results if e.user_id == query.user_id]
        # newest first
        results = sorted(results, key=lambda e: e.timestamp, reverse=True)
        return [e.model_copy(deep=True) for e in results[: query.limit]]

    def counts(self, *, account_id: str | None = None) -> list[EventCount]:
        tallies: dict[str, int] = {}
        for event in self._events:
            if account_id and event.account_id != account_id:
                continue
            tallies[event.name] = tallies.get(event.name, 0) + 1
        return [EventCount(name=name, count=count) for name, count in sorted(tallies.items())]
