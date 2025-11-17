"""Unit tests for observer pattern implementations."""

from unittest.mock import MagicMock

import pytest

from playt_player.domain.interfaces.observer import Observer, Subject
from playt_player.infrastructure.observers.logging_observer import LoggingObserver


class TestSubject:
    """Test suite for Subject base class."""

    def test_attach_observer(self) -> None:
        """Test attaching an observer."""
        subject = Subject()
        observer = MagicMock(spec=Observer)

        subject.attach(observer)
        subject.notify("test_event", "test_data")

        observer.update.assert_called_once_with("test_event", "test_data")

    def test_detach_observer(self) -> None:
        """Test detaching an observer."""
        subject = Subject()
        observer = MagicMock(spec=Observer)

        subject.attach(observer)
        subject.detach(observer)
        subject.notify("test_event", "test_data")

        observer.update.assert_not_called()

    def test_multiple_observers(self) -> None:
        """Test notifying multiple observers."""
        subject = Subject()
        observer1 = MagicMock(spec=Observer)
        observer2 = MagicMock(spec=Observer)

        subject.attach(observer1)
        subject.attach(observer2)
        subject.notify("test_event", "test_data")

        observer1.update.assert_called_once_with("test_event", "test_data")
        observer2.update.assert_called_once_with("test_event", "test_data")

    def test_duplicate_attach(self) -> None:
        """Test that attaching the same observer twice doesn't duplicate notifications."""
        subject = Subject()
        observer = MagicMock(spec=Observer)

        subject.attach(observer)
        subject.attach(observer)
        subject.notify("test_event", "test_data")

        assert observer.update.call_count == 1


class TestLoggingObserver:
    """Test suite for LoggingObserver."""

    def test_logging_observer_update(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test that LoggingObserver logs events."""
        import logging

        observer = LoggingObserver(log_level=logging.INFO)
        observer.update("test_event", "test_data")

        assert "test_event" in caplog.text
        assert "test_data" in caplog.text





