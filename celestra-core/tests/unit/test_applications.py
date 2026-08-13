"""Application registry / identity policy tests."""

from __future__ import annotations

import pytest

from config.applications import (
    APPROVED_APPLICATIONS,
    require_approved_application,
    require_memory_application,
)
from memory.conversation import normalize_application
from monitoring.application_context import normalize_application_label
from shared.exceptions.base import ValidationAppError


def test_approved_applications_vocabulary():
    assert APPROVED_APPLICATIONS == {"revenue", "hiring", "finance", "chrona"}


@pytest.mark.parametrize("app", sorted(APPROVED_APPLICATIONS))
def test_approved_application_accepted(app: str):
    assert require_approved_application(app) == app
    assert require_approved_application(app.upper()) == app


def test_unknown_application_rejected():
    with pytest.raises(ValidationAppError):
        require_approved_application("custom-app")
    with pytest.raises(ValidationAppError):
        require_approved_application("default")  # default not allowed on bridge


def test_memory_allows_default_rejects_unknown():
    assert require_memory_application(None) == "default"
    assert require_memory_application("default") == "default"
    assert normalize_application("revenue") == "revenue"
    with pytest.raises(ValidationAppError):
        normalize_application("totally-free-form")


def test_metric_labels_bounded():
    assert normalize_application_label("revenue") == "revenue"
    assert normalize_application_label("weird") == "unknown"
    assert normalize_application_label(None) == "default"
