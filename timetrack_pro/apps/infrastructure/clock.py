"""
Clock service for time operations.

Provides a testable abstraction over datetime.now() to enable
deterministic testing of time-dependent business logic.
"""
from datetime import datetime, timedelta
from typing import Protocol

import pytz


class Clock(Protocol):
    """Protocol for time operations, enabling test injection."""

    def now(self) -> datetime:
        """Get current UTC datetime."""
        ...

    def today(self) -> datetime:
        """Get current date (start of day in UTC)."""
        ...

    def travel_to(self, dt: datetime) -> None:
        """Set current time (test only)."""
        ...

    def advance(self, delta: timedelta) -> None:
        """Advance time by delta (test only)."""
        ...


class SystemClock:
    """Production clock using actual system time."""

    def now(self) -> datetime:
        """Get current UTC datetime."""
        return datetime.now(pytz.UTC)

    def today(self) -> datetime:
        """Get current date (start of day in UTC)."""
        now = self.now()
        return now.replace(hour=0, minute=0, second=0, microsecond=0)

    def travel_to(self, dt: datetime) -> None:
        """Not supported in production."""
        raise NotImplementedError("Cannot travel in production")

    def advance(self, delta: timedelta) -> None:
        """Not supported in production."""
        raise NotImplementedError("Cannot advance in production")


class TestClock:
    """
    Test clock with time travel capabilities.

    Usage in tests:
        clock = TestClock(initial=datetime(2024, 1, 15, 12, 0, 0, tzinfo=pytz.UTC))
        clock.travel_to(datetime(2024, 2, 1, 9, 0, 0, tzinfo=pytz.UTC))
        clock.advance(timedelta(days=3))
    """

    def __init__(self, initial: datetime | None = None):
        """Initialize with optional starting time (defaults to current UTC)."""
        if initial is None:
            self._current = datetime.now(pytz.UTC)
        elif initial.tzinfo is None:
            self._current = pytz.UTC.localize(initial)
        else:
            self._current = initial

    def now(self) -> datetime:
        """Get current mocked datetime."""
        return self._current

    def today(self) -> datetime:
        """Get current mocked date (start of day)."""
        return self._current.replace(hour=0, minute=0, second=0, microsecond=0)

    def travel_to(self, dt: datetime) -> None:
        """Set current time to specified datetime."""
        if dt.tzinfo is None:
            self._current = pytz.UTC.localize(dt)
        else:
            self._current = dt

    def advance(self, delta: timedelta) -> None:
        """Advance current time by delta."""
        self._current += delta


_clock_instance: Clock | None = None


def get_clock() -> Clock:
    """
    Get the current clock instance.

    In tests, use set_clock() to inject a TestClock.
    In production, returns SystemClock.
    """
    global _clock_instance
    if _clock_instance is not None:
        return _clock_instance

    from django.conf import settings
    if getattr(settings, 'TESTING', False):
        return TestClock()
    return SystemClock()


def set_clock(clock: Clock | None) -> None:
    """
    Set the clock instance (for testing).

    Pass None to reset to default behavior.
    """
    global _clock_instance
    _clock_instance = clock


def reset_clock() -> None:
    """Reset clock to default behavior."""
    set_clock(None)
