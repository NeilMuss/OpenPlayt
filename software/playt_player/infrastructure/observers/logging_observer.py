"""Logging observer implementation for debugging and monitoring."""

import logging
from typing import Any

from ...domain.interfaces.observer import Observer

logger = logging.getLogger(__name__)


class LoggingObserver(Observer):
    """
    Observer that logs all state change events.

    Useful for debugging and monitoring player state changes.
    """

    def __init__(self, log_level: int = logging.INFO) -> None:
        """
        Initialize the logging observer.

        Args:
            log_level: Logging level (default: INFO)
        """
        self._logger = logging.getLogger(f"{__name__}.LoggingObserver")
        self._logger.setLevel(log_level)

    def update(self, event_type: str, data: Any) -> None:
        """
        Log the state change event.

        Args:
            event_type: Type of event
            data: Event data
        """
        self._logger.info(f"Event: {event_type}, Data: {data}")





