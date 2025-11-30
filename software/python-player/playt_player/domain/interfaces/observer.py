"""Observer pattern interface for state change notifications."""

from abc import ABC, abstractmethod
from typing import Any


class Observer(ABC):
    """
    Abstract observer interface for receiving state change notifications.

    Observers can be registered with subjects to receive updates when
    state changes occur (e.g., playback started, paused, etc.).
    """

    @abstractmethod
    def update(self, event_type: str, data: Any) -> None:
        """
        Receive a state change notification.

        Args:
            event_type: Type of event (e.g., 'track_started', 'track_paused')
            data: Event data (e.g., Song object, state information)
        """
        pass


class Subject(ABC):
    """
    Abstract subject interface for managing observers.

    Subjects notify all registered observers when state changes occur.
    """

    def __init__(self) -> None:
        """Initialize the observer list."""
        self._observers: list[Observer] = []

    def attach(self, observer: Observer) -> None:
        """
        Register an observer to receive notifications.

        Args:
            observer: The observer to register
        """
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        """
        Unregister an observer.

        Args:
            observer: The observer to unregister
        """
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, event_type: str, data: Any) -> None:
        """
        Notify all registered observers of a state change.

        Args:
            event_type: Type of event
            data: Event data
        """
        for observer in self._observers:
            observer.update(event_type, data)


