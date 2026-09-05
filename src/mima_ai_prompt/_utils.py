"""Private helpers: UTC clocks, ids, and catalog string cleanup."""

from __future__ import annotations

import textwrap
from datetime import datetime, timezone
from uuid import uuid4


def utc_now() -> datetime:
    """Current time in UTC (timezone-aware)."""
    return datetime.now(timezone.utc)


def new_id() -> str:
    """Random hex UUID without dashes."""
    return uuid4().hex


def catalog_text(text: str) -> str:
    """``textwrap.dedent`` plus strip, for indented catalog literals."""
    return textwrap.dedent(text).strip()


def aware_utc(value: datetime) -> datetime:
    """Treat naive datetimes as UTC, then convert to UTC."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
